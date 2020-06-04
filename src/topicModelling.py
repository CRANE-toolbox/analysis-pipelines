# Run a topic modelling algorithm on a subset of the dataset, either tweets classified as anti-asian hate speech or covid19-related tweets.
# This subset is split into two corpora around a given date, to investigate the change in topics with the onset of the crisis.
# Topic modelling with Latent Dirichlet Allocation, as described in https://arxiv.org/pdf/2004.06986.pdf page 13
# Implementation based on gemsim tutorial: https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html#sphx-glr-auto-examples-tutorials-run-lda-py
# Used as a module: e.g. python -m genericDatasetAnalysis.topicModelling 1 empty output.txt
# WARNING: Delete pickled datasets if you changed the source of the inputs


import logging

import datetime
import argparse
import gensim
import wordsegment
import json
import nltk
import pickle
import pandas as pd
from functools import partial
from multiprocessing import Pool, cpu_count
from src import NoDaemonPool
from os import path
from time import time
from pprint import pprint
from os import listdir
from os.path import isfile
from gensim.corpora import Dictionary
from gensim.models import LdaMulticore, Phrases
from nltk import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from os import environ as env
from datetime import datetime as dt

from src.preprocessingTools import preprocessing

# Set logging level
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.WARNING)

# Load data for wordsegment
wordsegment.load()

# Stone B, Dennis S, Kwantes PJ. Comparing methods for single paragraph similarity analysis. Topics in Cognitive
# Science 2011. 3(1), 92-122. doi: 10.1111/j.1756-8765.2010.01108.x
# https://onlinelibrary.wiley.com/doi/full/10.1111/j.1756-8765.2010.01108.x Supplementary Info Annex C
stopWords = "a about above across after afterwards again against all almost alone along already also although always am among amongst amoungst amount an and another any anyhow anyone anything anyway anywhere are around as at back be became because become becomes becoming been before beforehand behind being below beside besides between beyond bill both bottom but by call can cannot cant co computer con could couldnt cry de describe detail do done down due during each eg eight either eleven else elsewhere empty enough etc even ever every everyone everything everywhere except few fifteen fify fill find fire first five for former formerly forty found four from front full further get give go had has hasnt have he hence her here hereafter hereby herein hereupon hers herself him himself his how however hundred i ie if in inc indeed interest into is it its itself keep last latter latterly least less ltd made many may me meanwhile might mill mine more moreover most mostly move much must my myself name namely neither never nevertheless next nine no nobody none noone nor not nothing now nowhere of off often on once one only onto or other others otherwise our ours ourselves out over own part per perhaps please put rather re same see seem seemed seeming seems serious several she should show side since sincere six sixty so some somehow someone something sometime sometimes somewhere still such system take ten than that the their them themselves then thence there thereafter thereby therefore therein thereupon these they thick thin third this those though three through throughout thru thus to together too top toward towards twelve twenty two un under until up upon us very via was we well were what whatever when whence whenever where whereafter whereas whereby wherein whereupon wherever whether which while whither who whoever whole whom whose why will with within without would yet you your yours yourself yourselves"

stopWords = stopWords + " http https"

# Make the list of topic numbers to try global for multithreading
topicNumbersToTry = [3, 6, 9]

# Split dataset around 1st Feb 2020
splitDate = pd.to_datetime(datetime.date(2020, 2, 1)).tz_localize("UTC")

# Regex of covid-related keywords to detect
keywords = {"covid", "corona", "ncov", "cov19",
            "wuhanvirus", "sars-cov", "sarscov"}

# Make the output path global for multithreading
outputPath = ""


def preprocessingTopicModelling(text, segmentHashtags):
    """Helper function to preprocess for topic modelling"""
    return preprocessing(text, False, False, (not segmentHashtags), False, False)


def getCorpusHateSpeech(inputName, date, segmentHashtags):
    """Get the tweets selected by the classifier and split it into two corpora.

    :param str inputName: The name of the file containing the results from the classifier. The file should be located in the "classification" results folder.
    :param datetime date: A pandas datetime date to split the dataset around.
    :param bool segmentHashtags: Segment hashtags into words.
    :return: List of tweet text contents from before date, List of tweet text content from after date.
    :rtype: list(str), list(str)

    """

    # Get the text of tweets classified as racists
    inputDirectory = env.get("RESULTS_PATH")
    inputPath = inputDirectory + "/classification/" + inputName
    inputDataFrame = pd.read_csv(inputPath)

    # Get only tweets detected as anti-asian hate speech
    inputDataFrame = inputDataFrame[inputDataFrame["anti-asian detected"] is True].copy()

    # Generate corpora for before and after split date
    beforeDataframe = inputDataFrame[(pd.to_datetime(
        inputDataFrame["timestamp"]) < date)].copy()
    afterDataframe = inputDataFrame[(pd.to_datetime(
        inputDataFrame["timestamp"]) >= date)].copy()
    rawDocumentsBefore = beforeDataframe["originalText"].to_list()
    rawDocumentsAfter = afterDataframe["originalText"].to_list()

    # Preprocess text
    print("Pre-processing tweets...")
    documentsBefore = [preprocessingTopicModelling(
        text, segmentHashtags) for text in rawDocumentsBefore]
    documentsAfter = [preprocessingTopicModelling(
        text, segmentHashtags) for text in rawDocumentsAfter]

    return documentsBefore, documentsAfter


def filterFileToDataframe(filePath, keywords):
    """Load json-encoded tweets to a Dataframe, filtering for given keywords.

    :param str filePath: Full path to the file to be read.
    :param list(str) keywords: List of keywords to select.
    :return: A Dataframe containing only tweets with at least of words from keywords.
    :rtype: Dataframe

    """

    print("reading ", filePath)
    col = ["id", "timestamp", "text"]
    fileJson = []
    # Read file
    with open(filePath, encoding="utf-8", mode='r') as lines:
        # For each tweet
        for line in lines:
            tweet = json.loads(line)
            text = tweet["text"]
            # Check if the text contains one of the keywords right away to save on time
            if len(keywords.intersection(text.casefold().split())) > 0:
                # Save tweet
                id = tweet["id"]
                timestamp = pd.to_datetime(tweet["created_at"])
                fileJson.append(
                    {"id": id, "timestamp": timestamp, "text": text})
    return pd.DataFrame(fileJson, columns=col)


def getCorpusCovid(date, segmentHashtags):
    """Get tweets containing covid19-related keywords and split into two corpora.

    :param datetime date: A pandas datetime date to split the dataset around.
    :param bool segmentHashtags: Segment hashtags into words.
    :return: List of tweet text contents from before date, List of tweet text content from after date.
    :rtype: list(str), list(str)

    """

    # List of files to read
    inputDirectory = env.get("INTERMEDIATE_PATH")

    # Filter files down to ones that are actually files plus have the correct extension
    # Only applies to files with .predictor extension
    inputPaths = [path.join(inputDirectory, f) for f in listdir(inputDirectory, ) if
                  isfile(path.join(inputDirectory, f)) and path.splitext(path.join(inputDirectory, f))[
                      1] is not '']
    if len(inputPaths) < 1:
        raise FileNotFoundError(
            "No files with the correct extension found in folder " +
            inputDirectory + ". Files should have an "
            "extension, any extension is "
            "valid")

    global keywords
    # Make sure all the keywords are lower case
    for word in keywords:
        keywords.remove(word)
        keywords.add(word.casefold())

    # Iterate over files
    col = ["id", "timestamp", "text"]
    covidData = pd.DataFrame(columns=col)
    with Pool(processes=cpu_count()) as pool:
        # Create partial arguments, sets keywords to a static variable defined above since it
        # does not change for each map iteration
        args = partial(filterFileToDataframe, keywords=keywords)
        df_list = pool.map(args, inputPaths)
        covidData = pd.concat(df_list, ignore_index=True)

    # Generate corpora for before and after split date
    beforeDataframe = covidData.loc[covidData['timestamp'] < date]
    afterDataframe = covidData.loc[covidData['timestamp'] >= date]
    rawDocumentsBefore = beforeDataframe["text"].to_list()
    rawDocumentsAfter = afterDataframe["text"].to_list()

    # Preprocess text
    documentsBefore = []
    documentsAfter = []
    print("Pre-processing tweets...")
    with Pool(processes=cpu_count()) as pool:
        args = partial(preprocessingTopicModelling,
                       segmentHashtags=segmentHashtags)
        documentsBefore = pool.map(args, rawDocumentsBefore)
        documentsAfter = pool.map(args, rawDocumentsAfter)
    return documentsBefore, documentsAfter


def lemmatizeSingleCorpus(corpus, wordTags):
    """Lemmatize a corpus.

    :param list(str) corpus: List of texts to lemmatize.
    :param list(str) wordTags: List of one-character strings defining the POS-tags to select.
    :return: A lemmatized list of texts containing only words with wordTag POS-tag.
    :rtype: type

    """
    lemmatizer = WordNetLemmatizer()
    corpus = [lemmatizer.lemmatize(token) for token, tag in pos_tag(
        corpus) if (tag[0] in wordTags)]
    return corpus


def prepareCorpus(rawCorpus, useAdjectives):
    """Prepare a corpus for training.

    :param list(str) rawCorpus: The corpus is a list of texts.
    :param bool useAdjectives: Use words with adjective POS-tagging in addition to nouns.
    :return: The prepared corpus, The corpus dictionary.
    :rtype: list(list(int, int)), Dictionary

    """

    print("Preparing corpus")
    # Tokenise and remove tokens with len < 3
    tokenisedCorpus = [gensim.utils.simple_preprocess(
        doc, deacc=False, min_len=3) for doc in rawCorpus]

    # Remove words that are less than 3 characters.
    print("Removing words less than 3 characters")
    tokenisedCorpus = [[token for token in doc if len(
        token) > 2] for doc in tokenisedCorpus]

    # Get only nouns, use lemmatiser
    if useAdjectives:
        print("Keeping only nouns and adjectives")
        wordTags = ["N", "J"]
    else:
        print("Keeping only nouns")
        wordTags = ["N"]
    with Pool(processes=2) as pool:
        args = partial(lemmatizeSingleCorpus, wordTags=wordTags)
        tokenisedCorpus = pool.map(args, tokenisedCorpus)

    # Remove stop words
    print("Removing stop words")
    global stopWords
    stopWordSet = set(stopWords.split())
    for tweet in tokenisedCorpus:
        for word in tweet:
            if word in stopWordSet:
                tweet.remove(word)

    # Add bigrams and trigrams to docs (only ones that appear 20 times or more).
    print("Creating bigrams")
    bigram = Phrases(tokenisedCorpus, min_count=20)
    for idx in range(len(tokenisedCorpus)):
        for token in bigram[tokenisedCorpus[idx]]:
            if '_' in token:
                # Token is a bigram, add to document.
                tokenisedCorpus[idx].append(token)

    # Extract dictionary
    print("Extracting dictionary")
    dictionary = Dictionary(tokenisedCorpus)

    # Turning the tokens into bag of words
    print("Creating bag of words")
    preparedCorpus = [dictionary.doc2bow(doc) for doc in tokenisedCorpus]

    return preparedCorpus, dictionary


def trainModel(preparedCorpus, dictionary, numberOfTopics):
    """Train LDA model on corpus.

    :param list(list(int, int)) preparedCorpus: The bag-of-words corpus.
    :param Dictionary dictionary: The Dictionnary corresponding to preparedCorpus.
    :param int numberOfTopics: Number of topics to train the LDA with.
    :return: The trained model.
    :rtype: LdaMulticore

    """

    # Set training parameters.
    # Check the Training section of https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html
    # to learn how to pick parameters
    num_topics = numberOfTopics
    chunksize = 5000000
    passes = 10
    iterations = 200
    eval_every = None  # Don't evaluate model perplexity, takes too much time.

    # Make a index to word dictionary.
    temp = dictionary[0]  # This is only to "load" the dictionary.
    id2word = dictionary.id2token

    try:
        # Train model
        model = LdaMulticore(
            corpus=preparedCorpus,
            id2word=id2word,
            workers=4,
            chunksize=chunksize,
            # alpha='asymmetric',
            eta='auto',
            iterations=iterations,
            num_topics=num_topics,
            passes=passes,
            eval_every=eval_every
        )
    except Exception as e:
        print(e.with_traceback())

    return model


def printResults(corpus, model, numberOfTopics):
    """Print results of LDA model with topic coherence and main words.

    :param list(list(int, int)) corpus: The bag-of-words corpus.
    :param LdaMulticore model: The trained LDA model.
    :param int numberOfTopics: Number of topics the model has been trained for.

    """

    top_topics = model.top_topics(corpus)

    # Average topic coherence is the sum of topic coherences of all topics, divided by the number of topics.
    avg_topic_coherence = sum([t[1] for t in top_topics]) / numberOfTopics
    print('Average topic coherence: %.4f.' % avg_topic_coherence)
    pprint(top_topics)


def saveResults(corpus, model, numberOfTopics, outputPath):
    """Save results of LDA model with topic coherence and main words.

    :param list(list(int, int)) corpus: The bag-of-words corpus.
    :param LdaMulticore model: The trained LDA model.
    :param int numberOfTopics: Number of topics the model has been trained for.
    :param str outputPath: Full path of the file to save the results to.

    """

    with open(outputPath, mode='a') as f:
        f.write(str(dt.now()) + " number of topics: " +
                str(numberOfTopics) + "\n")

        top_topics = model.top_topics(corpus)
        # Average topic coherence is the sum of topic coherences of all topics, divided by the number of topics.
        avg_topic_coherence = sum([t[1] for t in top_topics]) / numberOfTopics
        f.write('Average topic coherence: %.4f.' % avg_topic_coherence + "\n")
        # Write to the file
        pprint(top_topics, f)


def runOnPreppedCorpus(preparedCorpus, dictionary, numberOfTopics):
    """Train the model on a given corpus for a given number of topics.

    :param list(list(int, int)) preparedCorpus: The bag-of-words corpus.
    :param Dictionary dictionary: The Dictionnary corresponding to preparedCorpus.
    :param int numberOfTopics: Number of topics to train the LDA with.

    """

    print("Trying %d topics" % numberOfTopics)
    start_time = time()
    # Train the model
    model = trainModel(preparedCorpus, dictionary, numberOfTopics)
    # Print the results to the console
    printResults(preparedCorpus, model, numberOfTopics)
    # Save the results to a file
    global outputPath
    saveResults(preparedCorpus, model, numberOfTopics, outputPath)
    print("--- %s seconds ---" % (time() - start_time))


def runOnCorpus(rawCorpus, useAdjectives, segmentHashtags):
    """Run full pipeline on a given corpus, using multiple cores.

    :param list(str) rawCorpus: The corpus is a list of texts.
    :param bool useAdjectives: Use words with adjective POS-tagging in addition to nouns.
    :param bool segmentHashtags: Segment hashtags into words.

    """

    # Preprocessing
    preparedCorpus, dictionary = prepareCorpus(rawCorpus, useAdjectives)

    # Run all the LDA model options on multiple cores
    with NoDaemonPool.NoDaemonPool(len(topicNumbersToTry)) as pool:
        args = partial(runOnPreppedCorpus, preparedCorpus, dictionary)
        pool.map(args, topicNumbersToTry)


def mainTopicModelling(inputMode, inputName, useAdjectives, segmentHashtags):
    """Run full pipeline. Corpora are pickled on creation, only created once.

    :param int inputMode: 0 for tweets classified as anti-asian hate-speech, 1 for covid19-related tweets.
    :param str inputName: Ignored if inputMode == 1. The name of the file containing the results from the classifier. The file should be located in the "classification" results folder.
    :param bool useAdjectives: Use words with adjective POS-tagging in addition to nouns.
    :param bool segmentHashtags: Segment hashtags into words.

    """

    # Get data
    global splitDate
    documentsBefore = []
    documentsAfter = []
    # Using the tweets classified as anti-asian hate speech by the classifier
    if inputMode == 0:
        beforePicklePath = env.get("RESULTS_PATH") + \
            "/topicModelling/docsBeforeHateSpeech.pkl"
        afterPicklePath = env.get("RESULTS_PATH") + \
            "/topicModelling/docsAfterHateSpeech.pkl"
        # If datasets have already been generated, load pickles
        if path.exists(beforePicklePath) and path.exists(afterPicklePath):
            print("Loading corpus from file...")
            with open(beforePicklePath, mode='rb') as f:
                documentsBefore = pickle.load(f)
            with open(afterPicklePath) as f:
                documentsAfter = pickle.load(f)
        # If no pickled dataset exists, prepare the corpora
        else:
            documentsBefore, documentsAfter = getCorpusHateSpeech(
                inputName, splitDate, segmentHashtags)
    # Filter the full dataset for covid-related tweets
    elif inputMode == 1:
        beforePicklePath = env.get("RESULTS_PATH") + \
            "/topicModelling/docsBeforeCovid.pkl"
        afterPicklePath = env.get("RESULTS_PATH") + \
            "/topicModelling/docsAfterCovid.pkl"
        # If datasets have already been generated, load pickles
        if path.exists(beforePicklePath) and path.exists(afterPicklePath):
            print("Loading corpus from file...")
            with open(beforePicklePath, mode='rb') as f:
                documentsBefore = pickle.load(f)
            with open(afterPicklePath, mode='rb') as f:
                documentsAfter = pickle.load(f)
        # If no pickled dataset exists, prepare the corpora
        else:
            print("Saved pickle not found, loading directly from files")
            documentsBefore, documentsAfter = getCorpusCovid(
                splitDate, segmentHashtags)
            print("Saving corpus for future use")
            with open(beforePicklePath, mode="wb") as f:
                pickle.dump(documentsAfter, f)
            with open(afterPicklePath, mode="wb") as f:
                pickle.dump(documentsBefore, f)

    # Run pipeline on Before corpus
    with open(outputPath, mode='a') as f:
        print(splitDate.strftime("Before %d %b %Y"))
        f.write("Number of tweets in corpus: " +
                str(len(documentsBefore)) + "\n")
        f.write(splitDate.strftime("Before %d %b %Y") + "\n")
    runOnCorpus(documentsBefore, useAdjectives, segmentHashtags)
    # Run pipeline on After corpus
    with open(outputPath, mode='a') as f:
        print(splitDate.strftime("After %d %b %Y"))
        f.write(splitDate.strftime("After %d %b %Y") + "\n")
        f.write("Number of tweets in corpus: " +
                str(len(documentsAfter)) + "\n")
    runOnCorpus(documentsAfter, useAdjectives, segmentHashtags)

    with open(outputPath, mode='a') as f:
        print("Done")
        f.write("Done")


def parseArguments():
    """Parse script arguments.

    :return: The command line arguments entered by the user.
    :rtype: ArgumentParser object

    """

    # Create argument parser
    parser = argparse.ArgumentParser(description="Topic modelling pipeline.")

    # Positional mandatory arguments
    parser.add_argument(
        "inputMode", help="0 for anti-asian hate speech, 1 for covid-related", type=int)
    parser.add_argument(
        "inputName", help="Ignored it inputMode == 1. Name of the result file from the classifier. The file should be located in the 'classification' results folder.")
    parser.add_argument(
        "outputName", help="Name of the file to save the output in, including extension.", default="output.txt")

    # Optional arguments
    parser.add_argument("-adj", "--useAdjectives",
                        help="Use words with adjective POS-tagging in addition to nouns.", action='store_true')
    parser.add_argument("-seg", "--segmentHashtags",
                        help="Segment hashtags into words.", action='store_true')

    # Parse arguments
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = parseArguments()

    # Download NLTK data if not downloaded
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')

    outputPath = env.get("RESULTS_PATH") + "/topicModelling/" + args.outputName
    mainTopicModelling(args.inputMode, args.inputName,
                       args.useAdjectives, args.segmentHashtags)
