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


def aggregate_stats(input_name, output_prefix, date_format):
    """Compute freq of anti-black and anti-asian speech per day in the dataset.

    :param input_name: Name of the file results of classifier.runClassifier. The file should be located in the "classification" results folder.
    :type input_name: str
    :param output_prefix: Prefix for the output files. The files will be saved in the "classification" results folder.
    :type output_prefix: str
    :param date_format: String defining the format of dates in the dataset.
    :type date_format: str

    """

    # Count number of tweets per day in data before classification
    # List of files to read
    input_directory = env.get("INTERMEDIATE_PATH")
    input_paths = [join(input_directory, f) for f in listdir(
        input_directory) if isfile(join(input_directory, f))]
    all_dates_count_list = []
    timestamps = []
    for raw_data_name in input_paths:
        with open(raw_data_name, "r") as raw_data_file:
            counter = 0
            # For each tweet
            for line in raw_data_file:
                tweet = json.loads(line)
                date = tweet["created_at"]
                timestamps.append(date)
                counter += 1
                # Aggregate chunks to avoid memory error
                if counter % 500000 == 0:
                    temp_dates = pd.DataFrame(data={"timestamp": timestamps})
                    # Transform timestamps to a date format
                    temp_dates["timestamp"] = pd.to_datetime(
                        temp_dates["timestamp"], format=date_format)
                    temp_dates = transform_date_format(temp_dates)
                    # Aggregate counts
                    temp_count = temp_dates.groupby(
                        "day").count().add_suffix('_count').reset_index()
                    # Save chunk results to a list for performance
                    all_dates_count_list.append(temp_count)
                    del temp_dates, temp_count
                    timestamps = []
    # Concatenate all chunks
    all_dates_counts = pd.concat(all_dates_count_list, ignore_index=True)
    # Aggregate over chunks
    all_dates_counts = all_dates_counts.groupby("day").sum()

    # Read results from classifier
    input_name = env.get("RESULTS_PATH") + "/classification/" + input_name
    data = pd.read_csv(input_name)

    # Transform timestamps to a date format
    data["timestamp"] = pd.to_datetime(data["timestamp"], format=date_format)
    data = transform_date_format(data)

    # Aggregate per day for anti-black and anti-asian hate speech
    data_for_aggregation = data[[
        "day", "anti-black detected", "anti-asian detected"]].copy()
    aggregated_data = data_for_aggregation.groupby("day").sum()

    # Divide by daily total to get frequency
    frequency_data = aggregated_data.copy()
    frequency_data = pd.concat(
        [frequency_data, all_dates_counts], axis=1, join='inner')
    frequency_data["freq anti-black"] = frequency_data["anti-black detected"].map(
        float) / frequency_data["timestamp_count"]
    frequency_data["freq anti-asian"] = frequency_data["anti-asian detected"].map(
        float) / frequency_data["timestamp_count"]

    # Save results in ubiquitous CSV format
    output_path = env.get("RESULTS_PATH") + "/classification/" + output_prefix
    csv_output_path = output_path + ".csv"
    frequency_data.to_csv(csv_output_path, index=True)

    # Generate format for nivo https://nivo.rocks/line/
    nivo_output_path = output_path + ".json"
    # Extract dataframe with dates and frequencies then transform them to dict
    aggregated_asian = pd.DataFrame(data={"x": [x.strftime("%d-%b-%Y") for x in list(
        frequency_data.index.values)], "y": list(frequency_data["freq anti-asian"])})
    records_asian = aggregated_asian.to_dict("records")
    aggregated_black = pd.DataFrame(data={"x": [x.strftime("%d-%b-%Y") for x in list(
        frequency_data.index.values)], "y": list(frequency_data["freq anti-black"])})
    records_black = aggregated_black.to_dict("records")
    # Save in proper format
    nivo_format = [{"id": "sinophobia", "data": records_asian},
                  {"id": "anti-black racism", "data": records_black}]
    with open(nivo_output_path, "w") as nivo_file:
        json.dump(nivo_format, nivo_file)


def parse_arguments():
    """Parse script arguments.

    :return: The command line arguments entered by the user.
    :rtype: ArgumentParser object

    """

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Compute the frequency of tweets classified as anti-black and anti-asian hate speech in the dataset over time.")

    # Positional mandatory arguments
    parser.add_argument(
        "input_name", help="Name of the result file from the classifier. The file should be located in the 'classification' results folder.")
    parser.add_argument(
        "output_prefix", help="Prefix for the names of the output files.")

    # Optional arguments
    parser.add_argument("-d",
                        "--date_format", help="String defining the format of dates in the dataset.", default="%a %b %d %H:%M:%S %z %Y")

    # Parse arguments
    args = parser.parse_args()

    return args


args = parse_arguments()

aggregate_stats(args.input_name, args.output_prefix, args.date_format)
