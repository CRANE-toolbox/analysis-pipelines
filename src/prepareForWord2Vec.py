# Iterate over the full INTERMEDIATE_PATH folder, preprocess the dataset and split it according to the date of the tweets


import sys
import json
import argparse
from datetime import datetime
from os import listdir
from os.path import isfile, join
from os import environ as env
from preprocessingTools import *


def getPeriodNumber(dateString, dateFormat, startDate, periodLengthInDays):
    """Return period id for a given date, if periods have a fix number of days.

    :param dateString: Date for which the period id must be determined.
    :type dateString: str
    :param dateFormat: Format of dateString.
    :type dateFormat: str
    :param startDate: Beginning date of the first period.
    :type startDate: datetime
    :param periodLengthInDays: Fixed length of a period in days.
    :type periodLengthInDays: int
    :return: The period id corresponding to dateString. This will be negative is dateString is before startDate.
    :rtype: int

    """

    currentDate = datetime.strptime(dateString, dateFormat)
    dayDiff = (currentDate - startDate).days
    period = dayDiff // periodLengthInDays
    return period


def getPeriodMonth(dateString, dateFormat):
    """Return period descriptor for a given date, if period = month.

    :param dateString: Date for which the period id must be determined.
    :type dateString: str
    :param dateFormat: Format of the date strings (dateString and startDate).
    :type dateFormat: str
    :return: The period descriptor (month abbreviation + year) corresponding to dateString.
    :rtype: str

    """
    periodMonth = datetime.strptime(dateString, dateFormat).strftime('%h%y')
    return periodMonth


def sortDatasetIntoPeriod(periodMode, outputPrefix, dateFormat, startDate, periodLengthInDays):
    """Preprocess the dataset and split it according to the date of the tweets.

    :param periodMode: 0 for period = month, 1 for fixed-length periods.
    :type periodMode: int
    :param outputPrefix: Prefix for the output files. The files will be saved in the "wordEmbedding" results folder.
    :type outputPrefix: str
    :param dateFormat: String format for dates.
    :type dateFormat: str
    :param startDate: Beginning date of the first period. Ignored if periodMode == 0.
    :type startDate: datetime
    :param periodLengthInDays: Fixed length of a period in days. Ignored if periodMode == 0.
    :type periodLengthInDays: int

    """

    # Get paths
    inputDirectory = env.get("INTERMEDIATE_PATH")
    inputPaths = [join(inputDirectory, f) for f in listdir(
        inputDirectory) if isfile(join(inputDirectory, f))]
    outputDirectory = env.get("RESULTS_PATH")
    outputPath = outputDirectory + "/wordEmbedding/" + outputPrefix

    # For each file
    for inputPath in inputPaths:
        with open(inputPath, 'r') as inputFile:
            # For each tweet
            for line in inputFile:
                tweet = json.loads(line)
                dateString = tweet["created_at"]
                # Get the period
                periodSuffix = ""
                if periodMode == 0:
                    periodSuffix = getPeriodMonth(dateString, dateFormat)
                elif periodMode == 1:
                    periodId = getPeriodNumber(
                        dateString, dateFormat, startDate, periodLengthInDays)
                    if periodId < 0:
                        # If before startDate, ignore tweet
                        continue
                    periodSuffix = "_period%d" % periodId

                text = tweet["text"]
                # Tweet preprocessing
                cleanText = preprocessing(text, True, True, True, False, False)

                # Save to period file
                outputFullPath = outputPath + periodSuffix + ".txt"
                with open(outputFullPath, "a+") as outputFile:
                    outputFile.write(cleanText)
                    outputFile.write("\n")


def parseArguments():
    """Parse script arguments.

    :return: The command line arguments entered by the user.
    :rtype: ArgumentParser object

    """

    parser = argparse.ArgumentParser(
        description="Preprocessing pipeline for word2vec.")

    # Positional mandatory arguments
    parser.add_argument(
        "outputPrefix", help="Prefix for the names of the output files")
    parser.add_argument(
        "periodMode", help="0 for period = month, 1 for fixed length in days", type=int)

    # Optional arguments
    parser.add_argument("-f", "--dateFormat", help="String defining the format of dates in the dataset.", default="%a %b %d %H:%M:%S %z %Y")
    parser.add_argument("-s", "--startDate", help="First period start date if periodMode == 1, formated as %a %b %d %H:%M:%S %z %Y, else ignored",
                        default="Wed Jan 1 00:00:01 +0000 2020")
    parser.add_argument("-d", "--periodLength",
                        help="Period length in days if periodMode == 1, else ignored", default=7)

    # Parse arguments
    args = parser.parse_args()

    return args


# Get arguments
args = parseArguments()
startDate = datetime.strptime(args.startDate, args.dateFormat)

sortDatasetIntoPeriod(args.periodMode, args.outputPrefix, args.dateFormat, startDate,
                      args.periodLength)
