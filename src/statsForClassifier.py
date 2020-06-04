# Transform the results of the classifier into frequency stats


import json
import collections
import functools
import operator
import time
import argparse
import pandas as pd
from datetime import datetime
from os import listdir
from os.path import isfile, join
from os import environ as env
from utils import *


def aggregateStats(inputName, outputPrefix, dateFormat):
    """Compute freq of anti-black and anti-asian speech per day in the dataset.

    :param str inputName: Name of the file results of classifier.runClassifier. The file should be located in the "classification" results folder.
    :param str outputPrefix: Prefix for the output files. The files will be saved in the "classification" results folder.
    :param: str dateFormat: String defining the format of dates in the dataset.

    """

    # Count number of tweets per day in data before classification
    # List of files to read
    inputDirectory = env.get("INTERMEDIATE_PATH")
    inputPaths = [join(inputDirectory, f) for f in listdir(
        inputDirectory) if isfile(join(inputDirectory, f))]
    allDatesCountList = []
    timestamps = []
    for rawDataName in inputPaths:
        with open(rawDataName, "r") as rawDataFile:
            counter = 0
            # For each tweet
            for line in rawDataFile:
                tweet = json.loads(line)
                date = tweet["created_at"]
                timestamps.append(date)
                counter += 1
                # Aggregate chunks to avoid memory error
                if counter % 500000 == 0:
                    tempDates = pd.DataFrame(data={"timestamp": timestamps})
                    # Transform timestamps to a date format
                    tempDates["timestamp"] = pd.to_datetime(
                        tempDates["timestamp"], format=dateFormat)
                    tempDates = transformDateFormat(tempDates)
                    # Aggregate counts
                    tempCount = tempDates.groupby(
                        "day").count().add_suffix('_Count').reset_index()
                    # Save chunk results to a list for performance
                    allDatesCountList.append(tempCount)
                    del tempDates, tempCount
                    timestamps = []
    # Concatenate all chunks
    allDatesCounts = pd.concat(allDatesCountList, ignore_index=True)
    # Aggregate over chunks
    allDatesCounts = allDatesCounts.groupby("day").sum()

    # Read results from classifier
    inputName = env.get("RESULTS_PATH") + "/classification/" + inputName
    data = pd.read_csv(inputName)

    # Transform timestamps to a date format
    data["timestamp"] = pd.to_datetime(data["timestamp"], format=dateFormat)
    data = transformDateFormat(data)

    # Aggregate per day for anti-black and anti-asian hate speech
    dataForAggregation = data[[
        "day", "anti-black detected", "anti-asian detected"]].copy()
    aggregatedData = dataForAggregation.groupby("day").sum()

    # Divide by daily total to get frequency
    frequencyData = aggregatedData.copy()
    frequencyData = pd.concat(
        [frequencyData, allDatesCounts], axis=1, join='inner')
    frequencyData["freq anti-black"] = frequencyData["anti-black detected"].map(
        float) / frequencyData["timestamp_Count"]
    frequencyData["freq anti-asian"] = frequencyData["anti-asian detected"].map(
        float) / frequencyData["timestamp_Count"]

    # Save results in ubiquitous CSV format
    outputPath = env.get("RESULTS_PATH") + "/classification/" + outputPrefix
    csvOutputPath = outputPath + ".csv"
    frequencyData.to_csv(csvOutputPath, index=True)

    # Generate format for nivo https://nivo.rocks/line/
    nivoOutputPath = outputPath + ".json"
    # Extract dataframe with dates and frequencies then transform them to dict
    aggregatedAsian = pd.DataFrame(data={"x": [x.strftime("%d-%b-%Y") for x in list(
        frequencyData.index.values)], "y": list(frequencyData["freq anti-asian"])})
    recordsAsian = aggregatedAsian.to_dict("records")
    aggregatedBlack = pd.DataFrame(data={"x": [x.strftime("%d-%b-%Y") for x in list(
        frequencyData.index.values)], "y": list(frequencyData["freq anti-black"])})
    recordsBlack = aggregatedBlack.to_dict("records")
    # Save in proper format
    nivoFormat = [{"id": "sinophobia", "data": recordsAsian},
                  {"id": "anti-black racism", "data": recordsBlack}]
    with open(nivoOutputPath, "w") as nivoFile:
        json.dump(nivoFormat, nivoFile)


def parseArguments():
    """Parse script arguments.

    :return: The command line arguments entered by the user.
    :rtype: ArgumentParser object

    """

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Compute the frequency of tweets classified as anti-black and anti-asian hate speech in the dataset over time.")

    # Positional mandatory arguments
    parser.add_argument(
        "inputName", help="Name of the result file from the classifier. The file should be located in the 'classification' results folder.")
    parser.add_argument(
        "outputPrefix", help="Prefix for the names of the output files.")

    # Optional arguments
    parser.add_argument("-d",
                        "--dateFormat", help="String defining the format of dates in the dataset.", default="%a %b %d %H:%M:%S %z %Y")

    # Parse arguments
    args = parser.parse_args()

    return args


args = parseArguments()

aggregateStats(args.inputName, args.outputPrefix, args.dateFormat)
