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


def detect_slurs(input_path, output_path):
    """Filter tweets from a file, keeping those that contain at least one slur.

    :param input_path: Full path to the file containing the json-encoded tweets.
    :type input_path: str
    :param output_path: Full path to the CSV file where the selected tweets should be added. The file will be created if it does not exist.
    :type output_path: str
    :return: A DataFrame containing the selected tweets.
    :rtype: DataFrame

    """

    # Get slurs list from file
    slurs_file = env.get("SLURS_LIST_PATH")
    try:
        with open(slurs_file, "r") as slurs:
            slurs_dict = json.load(slurs)
    except Exception as e:
        print(e)
        raise Exception(e)

    # Check that the necessary keys are present in the slurs list
    ethnicities = list(slurs_dict.keys())
    if (not "black" in ethnicities or not "asian" in ethnicities):
        print("For this version, 'black' and 'asian' are the only processed keys and they must be present")
        raise Exception(KeyError)

    col = ["id", "timestamp", "original_text", "clean_text", "anti-black detected",
           "anti-black slur", "anti-asian detected", "anti-asian slur"]
    flagged_tweets_list = []
    flagged_tweets = pd.DataFrame(columns=col)

    # Detect slurs
    try:
        # Read input file
        with open(input_path, 'r') as original:
            # For each tweet
            for line in original:
                tweet = json.loads(line)
                id = tweet["id"]
                text = tweet["text"]
                timestamp = tweet["created_at"]
                cleaned_text = preprocessing(
                    text, True, True, True, True, False)

                # Check presence of slurs for each ethnicity and keep detected word
                contains_slur = {}
                flagged_word = {}
                for ethnicity, slurs in slurs_dict.items():
                    for word in slurs:
                        # Necessary else it detects part of words, example "night" matches for "nig"
                        term = " " + word + " "
                        if term in cleaned_text:
                            contains_slur.update({ethnicity: True})
                            flagged_word.update({ethnicity: word})
                            break
                        else:
                            contains_slur.update({ethnicity: False})
                            flagged_word.update({ethnicity: None})
                # Save/flag tweets with at least one detected slur
                if any(contains_slur.values()):
                    flagged_tweet = {"id": id, "timestamp": timestamp, "original_text": text, "clean_text": cleaned_text, "anti-black detected":
                                     contains_slur["black"], "anti-black slur": flagged_word["black"], "anti-asian detected": contains_slur["asian"], "anti-asian slur": flagged_word["asian"]}
                    flagged_tweets_list.append(pd.DataFrame(
                        flagged_tweet, columns=col, index=[0]))
    except Exception as e:
        print(e)
        raise Exception(e)

    # Save results
    try:
        # If at least one flagged tweet
        if len(flagged_tweets_list) > 0:
            with open(output_path, 'a') as outputFile:
                # Concatenate results
                flagged_tweets = pd.concat(
                    flagged_tweets_list, ignore_index=True)
                # Only add headers if creating the file, so the results of several input files can be saved into the same output file
                flagged_tweets.to_csv(
                    outputFile, index=False, quotechar='"', quoting=2, header=outputFile.tell() == 0)
    except Exception as e:
        print(e)
        raise Exception(e)

    return flagged_tweets


# Query Google Perspective API for a given text
# ratelimit decorator is dealing with our API QPS max rate
perspective_qps = int(env.get("PERSPECTIVE_QPS"))


@sleep_and_retry
@limits(calls=perspective_qps, period=1)
def query_perspective(tweet, score_type, threshold):
    """Score the text content of a tweet using Google Perspective API.

    :param tweet: One row of a DataFrame, corresponds to a tweet to score.
    :type tweet: Series
    :param score_type: The type of score to require from Perspective. Tested values for now are TOXICITY and SEVERE_TOXICITY.
    :type score_type: str
    :param threshold: Only tweets scored at or above this threshold will be kept.
    :type threshold: float
    :return: The Perspective score, or -1 if the score is below the defined threshold.
    :rtype: int

    """

    # Get API key
    api_key = env.get('PERSPECTIVE_KEY')

    # Prepare query for Perspective API
    url = ('https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze' + '?key=' + api_key)
    data_dict = {'comment': {'text': tweet.clean_text}, 'languages': [
        'en'], 'requested_attributes': {score_type: {}}}

    # Loop to deal with API call errors
    while True:
        # Get the response from the API
        response = requests.post(url=url, data=json.dumps(data_dict))
        response_dict = json.loads(response.content)

        # Check for errors
        error = response_dict.get("error", None)
        if error != None:
            code = error["code"]
            if code == 429:
                # If error because overuse of API
                # Should not happen with ratelimit decorators!!
                print("Went over API QPS limit!")
                raise RuntimeError(
                    "Went over API QPS limit! Should not happen with ratelimit decorators!!")
            else:
                print(response_dict)
                print("Unknown API error")
                raise RuntimeError("Unknown Google Perspective API error")
        else:
            # No error, continue function
            break

    # Extract toxicity score
    score = 0
    try:
        score = response_dict["attributeScores"][score_type]["summaryScore"]["value"]
    except Exception as e:
        print(e)
        print("Incorrect query response structure")
        raise Exception(e)

    # Classify tweet
    if score >= threshold:
        return score
    else:
        return -1


def score_tweets(flagged_tweets, output_path, score_type, threshold):
    """Add a column with the Google Perspective score to a DataFrame of tweets.

    :param flagged_tweets: The result from detect_slurs, a DataFrame containing the tweets to score.
    :type flagged_tweets: DataFrame
    :param output_path: Full path to the CSV file where the selected tweets should be stored. The file will be created if it does not exist.
    :type output_path: str
    :param score_type: The type of score to require from Perspective. Tested values for now are TOXICITY and SEVERE_TOXICITY.
    :type score_type: str
    :param threshold: Only tweets scored at or above this threshold will be kept.
    :type threshold: float

    """

    # Get the scores
    try:
        flagged_tweets["score"] = flagged_tweets.apply(
            query_perspective, axis=1, args=(score_type, threshold))
    except Exception as e:
        print(e)
        raise Exception(e)

    # Remove tweets with scores below threshold
    scored_tweets = flagged_tweets.copy()
    scored_tweets.drop(
        scored_tweets[scored_tweets.score < 0].index, inplace=True)

    # Save results
    try:
        with open(output_path, 'w') as outputFile:
            scored_tweets.to_csv(outputFile, index=False,
                                 quotechar='"', quoting=2)
    except Exception as e:
        print(e)
        raise Exception(e)


# Main function, iterates over INTERMEDIATE_PATH, detects slurs then send flagged tweets to Perspective, saves results to a csv
def run_classifier(output_prefix, score_type, threshold, perspective_only, file):
    """Classifier main function, runs detect_slurs and score_tweets.

    :param output_prefix: Prefix for the output files. The output files will be saved in the "classification" results folder.
    :type output_prefix: str
    :param score_type: The type of score to require from Perspective. Tested values for now are TOXICITY and SEVERE_TOXICITY.
    :type score_type: str
    :param threshold: Only tweets scored at or above this threshold will be kept.
    :type threshold: float
    :param perspective_only: If true, skip detect_slurs and load its previous result from memory.
    :type perspective_only: bool
    :param file: If specified, name of the file to process. The file should be located in the INTERMEDIATE_PATH folder. It should contain one json-encoded tweet per line.
    :type file: str

    """

    # Get paths
    input_directory = env.get("INTERMEDIATE_PATH")
    input_paths = []
    if len(file) == 0:
        # Iterate over full directory
        input_paths = [join(input_directory, f) for f in listdir(
            input_directory) if isfile(join(input_directory, f))]
    else:
        # Process specified file
        input_path = join(input_directory, file)
        input_paths = [input_path]
    output_directory = env.get("RESULTS_PATH")
    output_path = output_directory + "/classification/" + output_prefix
    middle_output_path = output_path + "_flagged_tweets.csv"
    final_output_path = output_path + "_scored_tweets.csv"

    # Classify tweets
    if not perspective_only:
        # Full pipeline, detect slurs
        try:
            start_time = time()
            flagged_tweets_list = []
            # For each file
            for f in input_paths:
                flagged_tweetsForFile = detect_slurs(
                    f, middle_output_path)
                # Save to a list for performance issues
                flagged_tweets_list.append(flagged_tweetsForFile)
            # Concatenate results
            flagged_tweets = pd.concat(flagged_tweets_list, ignore_index=True)
            print("Slurs detected")
            print("--- %s seconds ---" % (time() - start_time))
        except Exception as e:
            print(e)
            print("Error while detecting slurs")
            return
    else:
        # Use results from previous slurs detection
        flagged_tweets = pd.read_csv(middle_output_path)

    # Score flagged tweets
    try:
        start_time = time()
        score_tweets(flagged_tweets, final_output_path, score_type, threshold)
        print("Toxicity scored")
        print("--- %s seconds ---" % (time() - start_time))
    except Exception as e:
        print(e)
        print("Error while computing score")


def parse_arguments():
    """Parse script arguments.

    :return: The command line arguments entered by the user.
    :rtype: ArgumentParser object

    """

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Classification pipeline. Select hate speech tweets from the files in INTERMEDIATE_PATH. All files should contain one json-encoded tweet per line.")

    # Positional mandatory arguments
    parser.add_argument(
        "output_prefix", help="Prefix for the output files. The output files will be saved in the 'classification' results folder.")

    # Optional arguments
    parser.add_argument(
        "-s", "--score_type", help="The type of score to require from Perspective. Tested values for now are TOXICITY and SEVERE_TOXICITY.", default="SEVERE_TOXICITY")
    parser.add_argument(
        "-t", "--threshold", help="Only tweets scored at or above this threshold will be kept.", default=0.6)
    parser.add_argument(
        "-f", "--file", help="If specified, name of the file to process. The file should be located in the INTERMEDIATE_PATH folder. It should contain one json-encoded tweet per line.", default="")
    parser.add_argument("-p", "--perspective_only",
                        help="Skips the detection of slurs and uses the results of a previous detection to score.", action='store_true')

    # Parse arguments
    args = parser.parse_args()

    return args


args = parse_arguments()

run_classifier(args.output_prefix, args.score_type,
               args.threshold, args.perspective_only, args.file)
