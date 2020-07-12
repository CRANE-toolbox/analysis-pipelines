# Iterate over the full INTERMEDIATE_PATH folder to get daily and weekly frequence of given slurs in the dataset

import json
import time
import argparse
import pandas as pd
from datetime import datetime
from os import listdir
from os.path import isfile, join
from os import environ as env
from utils import *


def countSlurs(outputPrefix, slurs, dateFormat):
    """Count daily occurrences of a given list of slurs in the dataset.

    :param outputPrefix: Prefix for the output files. The files will be saved in the "slurFreq" results folder.
    :type outputPrefix: str
    :param slurs: The slurs to detect and count. Each element is a list of variants to be counted as the same slur. The first variant is used as the column title.
    :type slurs: list(list(str))
    :param dateFormat: String defining the format of dates in the dataset.
    :type dateFormat: str
    :return: The list of the main variants of the slurs.
    :rtype: list(str)

    """

    # List of files to read
    inputDirectory = env.get("INTERMEDIATE_PATH")
    inputPaths = [join(inputDirectory, f) for f in listdir(
        inputDirectory) if isfile(join(inputDirectory, f))]

    countList = []
    tweetInfoList = []
    mainVariants = [slur[0] for slur in slurs]
    # For every file
    for rawDataName in inputPaths:
        with open(rawDataName, "r") as rawDataFile:
            counter = 0
            # For each tweet
            for line in rawDataFile:
                tweet = json.loads(line)
                tweetInfo = {
                    "id": tweet["id"], "timestamp": tweet["created_at"], "text": tweet["text"], "total": 1}
                # For each slur
                for slur in slurs:
                    # Detect if one of the variants of the slur is present in the tweet
                    mainVariant = slur[0]
                    tweetInfo[mainVariant] = any(
                        [variant in tweet["text"].lower() for variant in slur])
                # Save results to a list for performance
                tweetInfoList.append(tweetInfo)

                # Aggregate chunks to avoid memory error
                counter += 1
                if counter % 500000 == 0:
                    tempDf = pd.DataFrame(tweetInfoList)
                    # Transform timestamps to a date format
                    tempDf["timestamp"] = pd.to_datetime(
                        tempDf["timestamp"], format=dateFormat)
                    tempDf = transformDateFormat(tempDf)
                    # Aggregate counts
                    countColumns = ["day", "total"] + mainVariants
                    tempCount = tempDf[countColumns].groupby(
                        "day").sum().add_suffix('Count').reset_index()
                    # Save chunk results to a list for performance
                    countList.append(tempCount)
                    del tempDf, tempCount
                    tweetInfoList = []
    # Concatenate all chunks
    allCounts = pd.concat(countList, ignore_index=True)
    # Aggregate over chunks
    allCounts = allCounts.groupby("day").sum()

    # Divide by daily total to get frequency
    for variant in mainVariants:
        slurCountCol = variant + "Count"
        slurFreqCol = variant + "Freq"
        allCounts[slurFreqCol] = allCounts[slurCountCol].map(
            float) / allCounts["totalCount"]

    # Save results in ubiquitous CSV format
    outputPrefix = env.get("RESULTS_PATH") + \
        "/slurFreq/" + outputPrefix
    csvOutputName = outputPrefix + ".csv"
    allCounts.to_csv(csvOutputName, index=True)

    # Generate format for nivo https://nivo.rocks/line/
    nivoOutputName = outputPrefix + ".json"
    nivoCounts = []
    for variant in mainVariants:
        slurFreqCol = variant + "Freq"
        slurData = pd.DataFrame(data={"x": [x.strftime(
            "%d-%b-%Y") for x in list(allCounts.index.values)], "y": list(allCounts[slurFreqCol])})
        nivoCounts.append({"id": variant, "data": slurData.to_dict("records")})
    with open(nivoOutputName, "w") as nivoFile:
        json.dump(nivoCounts, nivoFile)

    return mainVariants


def byWeek(filePrefix, mainVariants):
    """Aggregate the results from countSlurs by week.

    :param filePrefix: Prefix used for countSlurs.
    :type filePrefix: str
    :param mainVariants: The main variant for each slur, used as column title.
    :type mainVariants: list(str)

    """

    # Paths to files
    inputName = env.get("RESULTS_PATH") + \
        "/slurFreq/" + filePrefix + ".csv"
    outputPrefix = env.get("RESULTS_PATH") + \
        "/slurFreq/" + filePrefix + "_byWeek"
    csvOutputName = outputPrefix + ".csv"
    nivoOutputName = outputPrefix + ".json"

    # Load daily counts
    data = pd.read_csv(inputName)

    # Drop daily freq columns
    colNames = ["day", "totalCount"] + \
        [(variant + 'Count') for variant in mainVariants]
    data = data[colNames]

    # Resample by week
    data.index = pd.to_datetime(data["day"])
    weekData = data.resample('W').sum()

    # Divide by weekly total to get frequency
    for variant in mainVariants:
        slurCountCol = variant + "Count"
        slurFreqCol = variant + "Freq"
        weekData[slurFreqCol] = weekData[slurCountCol].map(
            float) / weekData["totalCount"]

    # Save results in ubiquitous CSV format
    weekData.to_csv(csvOutputName, index=True)

    # Generate format for nivo https://nivo.rocks/line/
    nivoCounts = []
    for variant in mainVariants:
        slurFreqCol = variant + "Freq"
        slurData = pd.DataFrame(data={"x": [pd.to_datetime(x).strftime(
            "%d-%b-%Y") for x in list(weekData.index.values)], "y": list(weekData[slurFreqCol])})
        nivoCounts.append({"id": variant, "data": slurData.to_dict("records")})
    with open(nivoOutputName, "w") as nivoFile:
        json.dump(nivoCounts, nivoFile)


def runAnalysis(outputPrefix, slursPath, dateFormat):
    """Main function.

    :param outputPrefix: Prefix for the output files. The files will be saved in the "slurFreq" results folder.
    :type outputPrefix: str
    :param slursPath: Full path to the json file holding the list of slurs and variants to count.
    :type slursPath: str
    :param dateFormat: String defining the format of dates in the dataset.
    :type dateFormat: str

    """
    slurs = []
    with open(slursPath, "r") as slursFile:
        slurs = json.load(slursFile)

    mainVariants = countSlurs(outputPrefix, slurs, dateFormat)
    byWeek(outputPrefix, mainVariants)


def parseArguments():
    """Parse script arguments.

    :return: The command line arguments entered by the user.
    :rtype: ArgumentParser object

    """

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Compute the frequency of sinophobic slurs in the dataset over time.")

    # Positional mandatory arguments
    parser.add_argument(
        "outputPrefix", help="Prefix for the names of the output files.")
    parser.add_argument(
        "slursPath", help="Full path to the json file holding the list of slurs and variants to count. Must contain a list of lists of slurs. Nested lists are variants of the same slur.")

    # Optional arguments
    parser.add_argument("-d",
                        "--dateFormat", help="String defining the format of dates in the dataset.", default="%a %b %d %H:%M:%S %z %Y")

    # Parse arguments
    args = parser.parse_args()

    return args


args = parseArguments()

runAnalysis(args.outputPrefix, args.slursPath, args.dateFormat)
