# Iterate over the full INTERMEDIATE_PATH folder, preprocess the dataset and split it according to the date of the tweets


import sys
import json
import argparse
from datetime import datetime
from os import listdir
from os.path import isfile, join
from os import environ as env
from preprocessingTools import *


def get_period_number(date_string, date_format, start_date, period_length_in_days):
    """Return period id for a given date, if periods have a fix number of days.

    :param date_string: Date for which the period id must be determined.
    :type date_string: str
    :param date_format: Format of date_string.
    :type date_format: str
    :param start_date: Beginning date of the first period.
    :type start_date: datetime
    :param period_length_in_days: Fixed length of a period in days.
    :type period_length_in_days: int
    :return: The period id corresponding to date_string. This will be negative is date_string is before start_date.
    :rtype: int

    """

    current_date = datetime.strptime(date_string, date_format)
    day_diff = (current_date - start_date).days
    period = day_diff // period_length_in_days
    return period


def get_period_month(date_string, date_format):
    """Return period descriptor for a given date, if period = month.

    :param date_string: Date for which the period id must be determined.
    :type date_string: str
    :param date_format: Format of the date strings (date_string and start_date).
    :type date_format: str
    :return: The period descriptor (month abbreviation + year) corresponding to date_string.
    :rtype: str

    """
    period_month = datetime.strptime(date_string, date_format).strftime('%h%y')
    return period_month


def sort_dataset_into_period(period_mode, output_prefix, date_format, start_date, period_length_in_days):
    """Preprocess the dataset and split it according to the date of the tweets.

    :param period_mode: 0 for period = month, 1 for fixed-length periods.
    :type period_mode: int
    :param output_prefix: Prefix for the output files. The files will be saved in the "wordEmbedding" results folder.
    :type output_prefix: str
    :param date_format: String format for dates.
    :type date_format: str
    :param start_date: Beginning date of the first period. Ignored if period_mode == 0.
    :type start_date: datetime
    :param period_length_in_days: Fixed length of a period in days. Ignored if period_mode == 0.
    :type period_length_in_days: int

    """

    # Get paths
    input_directory = env.get("INTERMEDIATE_PATH")
    input_paths = [join(input_directory, f) for f in listdir(
        input_directory) if isfile(join(input_directory, f))]
    output_directory = env.get("RESULTS_PATH")
    output_path = output_directory + "/wordEmbedding/" + output_prefix

    # For each file
    for input_path in input_paths:
        with open(input_path, 'r') as input_file:
            # For each tweet
            for line in input_file:
                tweet = json.loads(line)
                date_string = tweet["created_at"]
                # Get the period
                period_suffix = ""
                if period_mode == 0:
                    period_suffix = get_period_month(date_string, date_format)
                elif period_mode == 1:
                    periodId = get_period_number(
                        date_string, date_format, start_date, period_length_in_days)
                    if periodId < 0:
                        # If before start_date, ignore tweet
                        continue
                    period_suffix = "_period%d" % periodId

                text = tweet["text"]
                # Tweet preprocessing
                clean_text = preprocessing(text, True, True, True, False, False)

                # Save to period file
                output_full_path = output_path + period_suffix + ".txt"
                with open(output_full_path, "a+") as output_file:
                    output_file.write(clean_text)
                    output_file.write("\n")


def parse_arguments():
    """Parse script arguments.

    :return: The command line arguments entered by the user.
    :rtype: ArgumentParser object

    """

    parser = argparse.ArgumentParser(
        description="Preprocessing pipeline for word2vec.")

    # Positional mandatory arguments
    parser.add_argument(
        "output_prefix", help="Prefix for the names of the output files")
    parser.add_argument(
        "period_mode", help="0 for period = month, 1 for fixed length in days", type=int)

    # Optional arguments
    parser.add_argument("-f", "--date_format", help="String defining the format of dates in the dataset.", default="%a %b %d %H:%M:%S %z %Y")
    parser.add_argument("-s", "--start_date", help="First period start date if period_mode == 1, formated as %a %b %d %H:%M:%S %z %Y, else ignored",
                        default="Wed Jan 1 00:00:01 +0000 2020")
    parser.add_argument("-d", "--periodLength",
                        help="Period length in days if period_mode == 1, else ignored", default=7)

    # Parse arguments
    args = parser.parse_args()

    return args


# Get arguments
args = parse_arguments()
start_date = datetime.strptime(args.start_date, args.date_format)

sort_dataset_into_period(args.period_mode, args.output_prefix, args.date_format, start_date,
                      args.periodLength)
