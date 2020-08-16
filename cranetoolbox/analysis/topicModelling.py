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
from cranetoolbox.analysis import NoDaemonPool
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

from cranetoolbox.preprocess.preprocessingTools import preprocessing

# Set logging level
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.WARNING)

# Load data for wordsegment
wordsegment.load()

# Stone B, Dennis S, Kwantes PJ. Comparing methods for single paragraph similarity analysis. Topics in Cognitive
# Science 2011. 3(1), 92-122. doi: 10.1111/j.1756-8765.2010.01108.x
# https://onlinelibrary.wiley.com/doi/full/10.1111/j.1756-8765.2010.01108.x Supplementary Info Annex C
stop_words = "a about above across after afterwards again against all almost alone along already also although always am among amongst amoungst amount an and another any anyhow anyone anything anyway anywhere are around as at back be became because become becomes becoming been before beforehand behind being below beside besides between beyond bill both bottom but by call can cannot cant co computer con could couldnt cry de describe detail do done down due during each eg eight either eleven else elsewhere empty enough etc even ever every everyone everything everywhere except few fifteen fify fill find fire first five for former formerly forty found four from front full further get give go had has hasnt have he hence her here hereafter hereby herein hereupon hers herself him himself his how however hundred i ie if in inc indeed interest into is it its itself keep last latter latterly least less ltd made many may me meanwhile might mill mine more moreover most mostly move much must my myself name namely neither never nevertheless next nine no nobody none noone nor not nothing now nowhere of off often on once one only onto or other others otherwise our ours ourselves out over own part per perhaps please put rather re same see seem seemed seeming seems serious several she should show side since sincere six sixty so some somehow someone something sometime sometimes somewhere still such system take ten than that the their them themselves then thence there thereafter thereby therefore therein thereupon these they thick thin third this those though three through throughout thru thus to together too top toward towards twelve twenty two un under until up upon us very via was we well were what whatever when whence whenever where whereafter whereas whereby wherein whereupon wherever whether which while whither who whoever whole whom whose why will with within without would yet you your yours yourself yourselves"

stop_words = stop_words + " http https"

# Make the list of topic numbers to try global for multithreading
topic_numbers_to_try = [3, 6, 9]

# Split dataset around 1st Feb 2020
split_date = pd.to_datetime(datetime.date(2020, 2, 1)).tz_localize("UTC")

# Regex of covid-related keywords to detect
keywords = {"covid", "corona", "ncov", "cov19",
            "wuhanvirus", "sars-cov", "sarscov"}

# Make the output path global for multithreading
output_path = ""


def preprocessing_topic_modelling(text, segment_hashtags):
    """Helper function to preprocess for topic modelling"""
    return preprocessing(text, False, False, (not segment_hashtags), False, False)


def get_corpus_hate_speech(input_name, date, segment_hashtags):
    """Get the tweets selected by the classifier and split it into two corpora.

    :param input_name: The name of the file containing the results from the classifier. The file should be located in the "classification" results folder.
    :type input_name: str
    :param date: A pandas datetime date to split the dataset around.
    :type date: datetime
    :param segment_hashtags: Segment hashtags into words.
    :type segment_hashtags: bool
    :return: List of tweet text contents from before date, List of tweet text content from after date.
    :rtype: list(str), list(str)

    """

    # Get the text of tweets classified as racists
    input_directory = env.get("RESULTS_PATH")
    input_path = input_directory + "/classification/" + input_name
    input_dataframe = pd.read_csv(input_path)

    # Get only tweets detected as anti-asian hate speech
    input_dataframe = input_dataframe[input_dataframe["anti-asian detected"] is True].copy()

    # Generate corpora for before and after split date
    before_dataframe = input_dataframe[(pd.to_datetime(
        input_dataframe["timestamp"]) < date)].copy()
    after_dataframe = input_dataframe[(pd.to_datetime(
        input_dataframe["timestamp"]) >= date)].copy()
    raw_documents_before = before_dataframe["originalText"].to_list()
    raw_documents_after = after_dataframe["originalText"].to_list()

    # Preprocess text
    print("Pre-processing tweets...")
    documents_before = [preprocessing_topic_modelling(
        text, segment_hashtags) for text in raw_documents_before]
    documents_after = [preprocessing_topic_modelling(
        text, segment_hashtags) for text in raw_documents_after]

    return documents_before, documents_after


def filter_file_to_dataframe(file_path, keywords):
    """Load json-encoded tweets to a Dataframe, filtering for given keywords.

    :param file_path: Full path to the file to be read.
    :type file_path: str
    :param keywords: List of keywords to select.
    :type keywords: list(str)
    :return: A Dataframe containing only tweets with at least of words from keywords.
    :rtype: Dataframe

    """

    print("reading ", file_path)
    col = ["id", "timestamp", "text"]
    file_json = []
    # Read file
    with open(file_path, encoding="utf-8", mode='r') as lines:
        # For each tweet
        for line in lines:
            tweet = json.loads(line)
            text = tweet["text"]
            # Check if the text contains one of the keywords right away to save on time
            if len(keywords.intersection(text.casefold().split())) > 0:
                # Save tweet
                id = tweet["id"]
                timestamp = pd.to_datetime(tweet["created_at"])
                file_json.append(
                    {"id": id, "timestamp": timestamp, "text": text})
    return pd.DataFrame(file_json, columns=col)


def get_corpus_covid(date, segment_hashtags):
    """Get tweets containing covid19-related keywords and split into two corpora.

    :param date: A pandas datetime date to split the dataset around.
    :type date: datetime
    :param segment_hashtags: Segment hashtags into words.
    :type segment_hashtags: bool
    :return: List of tweet text contents from before date, List of tweet text content from after date.
    :rtype: list(str), list(str)

    """

    # List of files to read
    input_directory = env.get("INTERMEDIATE_PATH")

    # Filter files down to ones that are actually files plus have the correct extension
    # Only applies to files with .predictor extension
    input_paths = [path.join(input_directory, f) for f in listdir(input_directory, ) if
                  isfile(path.join(input_directory, f)) and path.splitext(path.join(input_directory, f))[
                      1] is not '']
    if len(input_paths) < 1:
        raise FileNotFoundError(
            "No files with the correct extension found in folder " +
            input_directory + ". Files should have an "
            "extension, any extension is "
            "valid")

    global keywords
    # Make sure all the keywords are lower case
    for word in keywords:
        keywords.remove(word)
        keywords.add(word.casefold())

    # Iterate over files
    col = ["id", "timestamp", "text"]
    covid_data = pd.DataFrame(columns=col)
    with Pool(processes=cpu_count()) as pool:
        # Create partial arguments, sets keywords to a static variable defined above since it
        # does not change for each map iteration
        args = partial(filter_file_to_dataframe, keywords=keywords)
        df_list = pool.map(args, input_paths)
        covid_data = pd.concat(df_list, ignore_index=True)

    # Generate corpora for before and after split date
    before_dataframe = covid_data.loc[covid_data['timestamp'] < date]
    after_dataframe = covid_data.loc[covid_data['timestamp'] >= date]
    raw_documents_before = before_dataframe["text"].to_list()
    raw_documents_after = after_dataframe["text"].to_list()

    # Preprocess text
    documents_before = []
    documents_after = []
    print("Pre-processing tweets...")
    with Pool(processes=cpu_count()) as pool:
        args = partial(preprocessing_topic_modelling,
                       segment_hashtags=segment_hashtags)
        documents_before = pool.map(args, raw_documents_before)
        documents_after = pool.map(args, raw_documents_after)
    return documents_before, documents_after


def lemmatize_single_corpus(corpus, word_tags):
    """Lemmatize a corpus.

    :param corpus: List of texts to lemmatize.
    :type corpus: list(str)
    :param word_tags: List of one-character strings defining the POS-tags to select.
    :type word_tags: list(str)
    :return: A lemmatized list of texts containing only words with wordTag POS-tag.
    :rtype: type

    """
    lemmatizer = WordNetLemmatizer()
    corpus = [lemmatizer.lemmatize(token) for token, tag in pos_tag(
        corpus) if (tag[0] in word_tags)]
    return corpus


def prepare_corpus(raw_corpus, use_adjectives):
    """Prepare a corpus for training.

    :param raw_corpus: The corpus is a list of texts.
    :type raw_corpus: list(str)
    :param use_adjectives: Use words with adjective POS-tagging in addition to nouns.
    :type use_adjectives: bool
    :return: The prepared corpus, The corpus dictionary.
    :rtype: list(list(int, int)), Dictionary

    """

    print("Preparing corpus")
    # Tokenise and remove tokens with len < 3
    tokenised_corpus = [gensim.utils.simple_preprocess(
        doc, deacc=False, min_len=3) for doc in raw_corpus]

    # Remove words that are less than 3 characters.
    print("Removing words less than 3 characters")
    tokenised_corpus = [[token for token in doc if len(
        token) > 2] for doc in tokenised_corpus]

    # Get only nouns, use lemmatiser
    if use_adjectives:
        print("Keeping only nouns and adjectives")
        word_tags = ["N", "J"]
    else:
        print("Keeping only nouns")
        word_tags = ["N"]
    with Pool(processes=2) as pool:
        args = partial(lemmatize_single_corpus, word_tags=word_tags)
        tokenised_corpus = pool.map(args, tokenised_corpus)

    # Remove stop words
    print("Removing stop words")
    global stop_words
    stop_wordset = set(stop_words.split())
    for tweet in tokenised_corpus:
        for word in tweet:
            if word in stop_wordset:
                tweet.remove(word)

    # Add bigrams and trigrams to docs (only ones that appear 20 times or more).
    print("Creating bigrams")
    bigram = Phrases(tokenised_corpus, min_count=20)
    for idx in range(len(tokenised_corpus)):
        for token in bigram[tokenised_corpus[idx]]:
            if '_' in token:
                # Token is a bigram, add to document.
                tokenised_corpus[idx].append(token)

    # Extract dictionary
    print("Extracting dictionary")
    dictionary = Dictionary(tokenised_corpus)

    # Turning the tokens into bag of words
    print("Creating bag of words")
    prepared_corpus = [dictionary.doc2bow(doc) for doc in tokenised_corpus]

    return prepared_corpus, dictionary


def train_model(prepared_corpus, dictionary, number_of_topics):
    """Train LDA model on corpus.

    :param prepared_corpus: The bag-of-words corpus.
    :type prepared_corpus: list(list(int, int))
    :param dictionary: The Dictionnary corresponding to prepared_corpus.
    :type dictionary: Dictionary
    :param number_of_topics: Number of topics to train the LDA with.
    :type number_of_topics: int
    :return: The trained model.
    :rtype: LdaMulticore

    """

    # Set training parameters.
    # Check the Training section of https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html
    # to learn how to pick parameters
    num_topics = number_of_topics
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
            corpus=prepared_corpus,
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


def print_results(corpus, model, number_of_topics):
    """Print results of LDA model with topic coherence and main words.

    :param corpus: The bag-of-words corpus.
    :type corpus: list(list(int, int))
    :param model: The trained LDA model.
    :type model: LdaMulticore
    :param number_of_topics: Number of topics the model has been trained for.
    :type number_of_topics: int

    """

    top_topics = model.top_topics(corpus)

    # Average topic coherence is the sum of topic coherences of all topics, divided by the number of topics.
    avg_topic_coherence = sum([t[1] for t in top_topics]) / number_of_topics
    print('Average topic coherence: %.4f.' % avg_topic_coherence)
    pprint(top_topics)


def save_results(corpus, model, number_of_topics, output_path):
    """Save results of LDA model with topic coherence and main words.

    :param corpus: The bag-of-words corpus.
    :type corpus: list(list(int, int))
    :param model: The trained LDA model.
    :type model: LdaMulticore
    :param number_of_topics: Number of topics the model has been trained for.
    :type number_of_topics: int
    :param output_path: Full path of the file to save the results to.
    :type output_path: str

    """

    with open(output_path, mode='a') as f:
        f.write(str(dt.now()) + " number of topics: " +
                str(number_of_topics) + "\n")

        top_topics = model.top_topics(corpus)
        # Average topic coherence is the sum of topic coherences of all topics, divided by the number of topics.
        avg_topic_coherence = sum([t[1] for t in top_topics]) / number_of_topics
        f.write('Average topic coherence: %.4f.' % avg_topic_coherence + "\n")
        # Write to the file
        pprint(top_topics, f)


def run_on_prepped_corpus(prepared_corpus, dictionary, number_of_topics):
    """Train the model on a given corpus for a given number of topics.

    :param prepared_corpus: The bag-of-words corpus.
    :type prepared_corpus: list(list(int, int))
    :param dictionary: The Dictionnary corresponding to prepared_corpus.
    :type dictionary: Dictionary
    :param number_of_topics: Number of topics to train the LDA with.
    :type number_of_topics: int

    """

    print("Trying %d topics" % number_of_topics)
    start_time = time()
    # Train the model
    model = train_model(prepared_corpus, dictionary, number_of_topics)
    # Print the results to the console
    print_results(prepared_corpus, model, number_of_topics)
    # Save the results to a file
    global output_path
    save_results(prepared_corpus, model, number_of_topics, output_path)
    print("--- %s seconds ---" % (time() - start_time))


def run_on_corpus(raw_corpus, use_adjectives, segment_hashtags):
    """Run full pipeline on a given corpus, using multiple cores.

    :param raw_corpus: The corpus is a list of texts.
    :type raw_corpus: list(str)
    :param use_adjectives: Use words with adjective POS-tagging in addition to nouns.
    :type use_adjectives: bool
    :param segment_hashtags: Segment hashtags into words.
    :type segment_hashtags: bool

    """

    # Preprocessing
    prepared_corpus, dictionary = prepare_corpus(raw_corpus, use_adjectives)

    # Run all the LDA model options on multiple cores
    with NoDaemonPool.NoDaemonPool(len(topic_numbers_to_try)) as pool:
        args = partial(run_on_prepped_corpus, prepared_corpus, dictionary)
        pool.map(args, topic_numbers_to_try)


def main_topic_modelling(input_mode, input_name, use_adjectives, segment_hashtags):
    """Run full pipeline. Corpora are pickled on creation, only created once.

    :param input_mode: 0 for tweets classified as anti-asian hate-speech, 1 for covid19-related tweets.
    :type input_mode: int
    :param input_name: Ignored if input_mode == 1. The name of the file containing the results from the classifier. The file should be located in the "classification" results folder.
    :type input_name: str
    :param use_adjectives: Use words with adjective POS-tagging in addition to nouns.
    :type use_adjectives: bool
    :param segment_hashtags: Segment hashtags into words.
    :type segment_hashtags: bool

    """

    # Get data
    global split_date
    documents_before = []
    documents_after = []
    # Using the tweets classified as anti-asian hate speech by the classifier
    if input_mode == 0:
        before_pickle_path = env.get("RESULTS_PATH") + \
            "/topicModelling/docsBeforeHateSpeech.pkl"
        after_pickle_path = env.get("RESULTS_PATH") + \
            "/topicModelling/docsAfterHateSpeech.pkl"
        # If datasets have already been generated, load pickles
        if path.exists(before_pickle_path) and path.exists(after_pickle_path):
            print("Loading corpus from file...")
            with open(before_pickle_path, mode='rb') as f:
                documents_before = pickle.load(f)
            with open(after_pickle_path) as f:
                documents_after = pickle.load(f)
        # If no pickled dataset exists, prepare the corpora
        else:
            documents_before, documents_after = get_corpus_hate_speech(
                input_name, split_date, segment_hashtags)
    # Filter the full dataset for covid-related tweets
    elif input_mode == 1:
        before_pickle_path = env.get("RESULTS_PATH") + \
            "/topicModelling/docsBeforeCovid.pkl"
        after_pickle_path = env.get("RESULTS_PATH") + \
            "/topicModelling/docsAfterCovid.pkl"
        # If datasets have already been generated, load pickles
        if path.exists(before_pickle_path) and path.exists(after_pickle_path):
            print("Loading corpus from file...")
            with open(before_pickle_path, mode='rb') as f:
                documents_before = pickle.load(f)
            with open(after_pickle_path, mode='rb') as f:
                documents_after = pickle.load(f)
        # If no pickled dataset exists, prepare the corpora
        else:
            print("Saved pickle not found, loading directly from files")
            documents_before, documents_after = get_corpus_covid(
                split_date, segment_hashtags)
            print("Saving corpus for future use")
            with open(before_pickle_path, mode="wb") as f:
                pickle.dump(documents_after, f)
            with open(after_pickle_path, mode="wb") as f:
                pickle.dump(documents_before, f)

    # Run pipeline on Before corpus
    with open(output_path, mode='a') as f:
        print(split_date.strftime("Before %d %b %Y"))
        f.write("Number of tweets in corpus: " +
                str(len(documents_before)) + "\n")
        f.write(split_date.strftime("Before %d %b %Y") + "\n")
    run_on_corpus(documents_before, use_adjectives, segment_hashtags)
    # Run pipeline on After corpus
    with open(output_path, mode='a') as f:
        print(split_date.strftime("After %d %b %Y"))
        f.write(split_date.strftime("After %d %b %Y") + "\n")
        f.write("Number of tweets in corpus: " +
                str(len(documents_after)) + "\n")
    run_on_corpus(documents_after, use_adjectives, segment_hashtags)

    with open(output_path, mode='a') as f:
        print("Done")
        f.write("Done")


def parse_arguments():
    """Parse script arguments.

    :return: The command line arguments entered by the user.
    :rtype: ArgumentParser object

    """

    # Create argument parser
    parser = argparse.ArgumentParser(description="Topic modelling pipeline.")

    # Positional mandatory arguments
    parser.add_argument(
        "input_mode", help="0 for anti-asian hate speech, 1 for covid-related", type=int)
    parser.add_argument(
        "input_name", help="Ignored it input_mode == 1. Name of the result file from the classifier. The file should be located in the 'classification' results folder.")
    parser.add_argument(
        "output_name", help="Name of the file to save the output in, including extension.", default="output.txt")

    # Optional arguments
    parser.add_argument("-adj", "--use_adjectives",
                        help="Use words with adjective POS-tagging in addition to nouns.", action='store_true')
    parser.add_argument("-seg", "--segment_hashtags",
                        help="Segment hashtags into words.", action='store_true')

    # Parse arguments
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = parse_arguments()

    # Download NLTK data if not downloaded
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')

    output_path = env.get("RESULTS_PATH") + "/topicModelling/" + args.output_name
    main_topic_modelling(args.input_mode, args.input_name,
                       args.use_adjectives, args.segment_hashtags)
