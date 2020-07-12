# Classifies the tweets into anti-black hate speech, anti-asian hate speech and none, using a two-steps approach.
# The first step selects the tweets containing anti-black and anti-asian slurs. The intermediate results are saved to a file.
# The second steps evaluate the toxicity of the selected tweets using Google Perspective API.
# Only tweets with toxicity over a given threshold are saved.


import json
import requests
import argparse
import re
import pandas as pd
from os import listdir
from os.path import isfile, join
from datetime import datetime
from ratelimit import limits, sleep_and_retry
from time import time
from os import environ as env
from preprocessingTools import *


def detectSlurs(inputPath, outputPath):
    """Filter tweets from a file, keeping those that contain at least one slur.

    :param inputPath: Full path to the file containing the json-encoded tweets.
    :type inputPath: str
    :param outputPath: Full path to the CSV file where the selected tweets should be added. The file will be created if it does not exist.
    :type outputPath: str
    :return: A DataFrame containing the selected tweets.
    :rtype: DataFrame

    """

    # Get slurs list from file
    slursFile = env.get("SLURS_LIST_PATH")
    try:
        with open(slursFile, "r") as slurs:
            slursDict = json.load(slurs)
    except Exception as e:
        print(e)
        raise Exception(e)

    # Check that the necessary keys are present in the slurs list
    ethnicities = list(slursDict.keys())
    if (not "black" in ethnicities or not "asian" in ethnicities):
        print("For this version, 'black' and 'asian' are the only processed keys and they must be present")
        raise Exception(KeyError)

    col = ["id", "timestamp", "originalText", "cleanText", "anti-black detected",
           "anti-black slur", "anti-asian detected", "anti-asian slur"]
    flaggedTweetsList = []
    flaggedTweets = pd.DataFrame(columns=col)

    # Detect slurs
    try:
        # Read input file
        with open(inputPath, 'r') as original:
            # For each tweet
            for line in original:
                tweet = json.loads(line)
                id = tweet["id"]
                text = tweet["text"]
                timestamp = tweet["created_at"]
                cleanedText = preprocessing(
                    text, True, True, True, True, False)

                # Check presence of slurs for each ethnicity and keep detected word
                containsSlur = {}
                flaggedWord = {}
                for ethnicity, slurs in slursDict.items():
                    for word in slurs:
                        # Necessary else it detects part of words, example "night" matches for "nig"
                        term = " " + word + " "
                        if term in cleanedText:
                            containsSlur.update({ethnicity: True})
                            flaggedWord.update({ethnicity: word})
                            break
                        else:
                            containsSlur.update({ethnicity: False})
                            flaggedWord.update({ethnicity: None})
                # Save/flag tweets with at least one detected slur
                if any(containsSlur.values()):
                    flaggedTweet = {"id": id, "timestamp": timestamp, "originalText": text, "cleanText": cleanedText, "anti-black detected":
                                    containsSlur["black"], "anti-black slur": flaggedWord["black"], "anti-asian detected": containsSlur["asian"], "anti-asian slur": flaggedWord["asian"]}
                    flaggedTweetsList.append(pd.DataFrame(
                        flaggedTweet, columns=col, index=[0]))
    except Exception as e:
        print(e)
        raise Exception(e)

    # Save results
    try:
        # If at least one flagged tweet
        if len(flaggedTweetsList) > 0:
            with open(outputPath, 'a') as outputFile:
                # Concatenate results
                flaggedTweets = pd.concat(flaggedTweetsList, ignore_index=True)
                # Only add headers if creating the file, so the results of several input files can be saved into the same output file
                flaggedTweets.to_csv(
                    outputFile, index=False, quotechar='"', quoting=2, header=outputFile.tell() == 0)
    except Exception as e:
        print(e)
        raise Exception(e)

    return flaggedTweets


# Query Google Perspective API for a given text
# ratelimit decorator is dealing with our API QPS max rate
perspectiveQps = int(env.get("PERSPECTIVE_QPS"))


@sleep_and_retry
@limits(calls=perspectiveQps, period=1)
def queryPerspective(tweet, scoreType, threshold):
    """Score the text content of a tweet using Google Perspective API.

    :param tweet: One row of a DataFrame, corresponds to a tweet to score.
    :type tweet: Series
    :param scoreType: The type of score to require from Perspective. Tested values for now are TOXICITY and SEVERE_TOXICITY.
    :type scoreType: str
    :param threshold: Only tweets scored at or above this threshold will be kept.
    :type threshold: float
    :return: The Perspective score, or -1 if the score is below the defined threshold.
    :rtype: int

    """

    # Get API key
    apiKey = env.get('PERSPECTIVE_KEY')

    # Prepare query for Perspective API
    url = ('https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze' + '?key=' + apiKey)
    dataDict = {'comment': {'text': tweet.cleanText}, 'languages': [
        'en'], 'requestedAttributes': {scoreType: {}}}

    # Loop to deal with API call errors
    while True:
        # Get the response from the API
        response = requests.post(url=url, data=json.dumps(dataDict))
        responseDict = json.loads(response.content)

        # Check for errors
        error = responseDict.get("error", None)
        if error != None:
            code = error["code"]
            if code == 429:
                # If error because overuse of API
                # Should not happen with ratelimit decorators!!
                print("Went over API QPS limit!")
                raise RuntimeError(
                    "Went over API QPS limit! Should not happen with ratelimit decorators!!")
            else:
                print(responseDict)
                print("Unknown API error")
                raise RuntimeError("Unknown Google Perspective API error")
        else:
            # No error, continue function
            break

    # Extract toxicity score
    score = 0
    try:
        score = responseDict["attributeScores"][scoreType]["summaryScore"]["value"]
    except Exception as e:
        print(e)
        print("Incorrect query response structure")
        raise Exception(e)

    # Classify tweet
    if score >= threshold:
        return score
    else:
        return -1


def scoreTweets(flaggedTweets, outputPath, scoreType, threshold):
    """Add a column with the Google Perspective score to a DataFrame of tweets.

    :param flaggedTweets: The result from detectSlurs, a DataFrame containing the tweets to score.
    :type flaggedTweets: DataFrame
    :param outputPath: Full path to the CSV file where the selected tweets should be stored. The file will be created if it does not exist.
    :type outputPath: str
    :param scoreType: The type of score to require from Perspective. Tested values for now are TOXICITY and SEVERE_TOXICITY.
    :type scoreType: str
    :param threshold: Only tweets scored at or above this threshold will be kept.
    :type threshold: float

    """

    # Get the scores
    try:
        flaggedTweets["score"] = flaggedTweets.apply(
            queryPerspective, axis=1, args=(scoreType, threshold))
    except Exception as e:
        print(e)
        raise Exception(e)

    # Remove tweets with scores below threshold
    scoredTweets = flaggedTweets.copy()
    scoredTweets.drop(scoredTweets[scoredTweets.score < 0].index, inplace=True)

    # Save results
    try:
        with open(outputPath, 'w') as outputFile:
            scoredTweets.to_csv(outputFile, index=False,
                                quotechar='"', quoting=2)
    except Exception as e:
        print(e)
        raise Exception(e)


# Main function, iterates over INTERMEDIATE_PATH, detects slurs then send flagged tweets to Perspective, saves results to a csv
def runClassifier(outputPrefix, scoreType, threshold, perspectiveOnly, file):
    """Classifier main function, runs detectSlurs and scoreTweets.

    :param outputPrefix: Prefix for the output files. The output files will be saved in the "classification" results folder.
    :type outputPrefix: str
    :param scoreType: The type of score to require from Perspective. Tested values for now are TOXICITY and SEVERE_TOXICITY.
    :type scoreType: str
    :param threshold: Only tweets scored at or above this threshold will be kept.
    :type threshold: float
    :param perspectiveOnly: If true, skip detectSlurs and load its previous result from memory.
    :type perspectiveOnly: bool
    :param file: If specified, name of the file to process. The file should be located in the INTERMEDIATE_PATH folder. It should contain one json-encoded tweet per line.
    :type file: str

    """

    # Get paths
    inputDirectory = env.get("INTERMEDIATE_PATH")
    inputPaths = []
    if len(file) == 0:
        # Iterate over full directory
        inputPaths = [join(inputDirectory, f) for f in listdir(
            inputDirectory) if isfile(join(inputDirectory, f))]
    else:
        # Process specified file
        inputPath = join(inputDirectory, file)
        inputPaths = [inputPath]
    outputDirectory = env.get("RESULTS_PATH")
    outputPath = outputDirectory + "/classification/" + outputPrefix
    middleOutputPath = outputPath + "_flaggedTweets.csv"
    finalOutputPath = outputPath + "_scoredTweets.csv"

    # Classify tweets
    if not perspectiveOnly:
        # Full pipeline, detect slurs
        try:
            start_time = time()
            flaggedTweetsList = []
            # For each file
            for f in inputPaths:
                flaggedTweetsForFile = detectSlurs(
                    f, middleOutputPath)
                # Save to a list for performance issues
                flaggedTweetsList.append(flaggedTweetsForFile)
            # Concatenate results
            flaggedTweets = pd.concat(flaggedTweetsList, ignore_index=True)
            print("Slurs detected")
            print("--- %s seconds ---" % (time() - start_time))
        except Exception as e:
            print(e)
            print("Error while detecting slurs")
            return
    else:
        # Use results from previous slurs detection
        flaggedTweets = pd.read_csv(middleOutputPath)

    # Score flagged tweets
    try:
        start_time = time()
        scoreTweets(flaggedTweets, finalOutputPath, scoreType, threshold)
        print("Toxicity scored")
        print("--- %s seconds ---" % (time() - start_time))
    except Exception as e:
        print(e)
        print("Error while computing score")


def parseArguments():
    """Parse script arguments.

    :return: The command line arguments entered by the user.
    :rtype: ArgumentParser object

    """

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Classification pipeline. Select hate speech tweets from the files in INTERMEDIATE_PATH. All files should contain one json-encoded tweet per line.")

    # Positional mandatory arguments
    parser.add_argument(
        "outputPrefix", help="Prefix for the output files. The output files will be saved in the 'classification' results folder.")

    # Optional arguments
    parser.add_argument(
        "-s", "--scoreType", help="The type of score to require from Perspective. Tested values for now are TOXICITY and SEVERE_TOXICITY.", default="SEVERE_TOXICITY")
    parser.add_argument(
        "-t", "--threshold", help="Only tweets scored at or above this threshold will be kept.", default=0.6)
    parser.add_argument(
        "-f", "--file", help="If specified, name of the file to process. The file should be located in the INTERMEDIATE_PATH folder. It should contain one json-encoded tweet per line.", default="")
    parser.add_argument("-p", "--perspectiveOnly",
                        help="Skips the detection of slurs and uses the results of a previous detection to score.", action='store_true')

    # Parse arguments
    args = parser.parse_args()

    return args


args = parseArguments()

runClassifier(args.outputPrefix, args.scoreType,
              args.threshold, args.perspectiveOnly, args.file)
