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


def count_slurs(output_prefix, slurs, date_format):
    """Count daily occurrences of a given list of slurs in the dataset.

    :param output_prefix: Prefix for the output files. The files will be saved in the "slurFreq" results folder.
    :type output_prefix: str
    :param slurs: The slurs to detect and count. Each element is a list of variants to be counted as the same slur. The first variant is used as the column title.
    :type slurs: list(list(str))
    :param date_format: String defining the format of dates in the dataset.
    :type date_format: str
    :return: The list of the main variants of the slurs.
    :rtype: list(str)

    """

    # List of files to read
    input_directory = env.get("INTERMEDIATE_PATH")
    input_paths = [join(input_directory, f) for f in listdir(
        input_directory) if isfile(join(input_directory, f))]

    count_list = []
    tweet_info_list = []
    main_variants = [slur[0] for slur in slurs]
    # For every file
    for raw_data_name in input_paths:
        with open(raw_data_name, "r") as raw_data_file:
            counter = 0
            # For each tweet
            for line in raw_data_file:
                tweet = json.loads(line)
                tweet_info = {
                    "id": tweet["id"], "timestamp": tweet["created_at"], "text": tweet["text"], "total": 1}
                # For each slur
                for slur in slurs:
                    # Detect if one of the variants of the slur is present in the tweet
                    main_variant = slur[0]
                    tweet_info[main_variant] = any(
                        [variant in tweet["text"].lower() for variant in slur])
                # Save results to a list for performance
                tweet_info_list.append(tweet_info)

                # Aggregate chunks to avoid memory error
                counter += 1
                if counter % 500000 == 0:
                    temp_df = pd.DataFrame(tweet_info_list)
                    # Transform timestamps to a date format
                    temp_df["timestamp"] = pd.to_datetime(
                        temp_df["timestamp"], format=date_format)
                    temp_df = transform_date_format(temp_df)
                    # Aggregate counts
                    count_columns = ["day", "total"] + main_variants
                    temp_count = temp_df[count_columns].groupby(
                        "day").sum().add_suffix('_count').reset_index()
                    # Save chunk results to a list for performance
                    count_list.append(temp_count)
                    del temp_df, temp_count
                    tweet_info_list = []
    # Concatenate all chunks
    all_counts = pd.concat(count_list, ignore_index=True)
    # Aggregate over chunks
    all_counts = all_counts.groupby("day").sum()

    # Divide by daily total to get frequency
    for variant in main_variants:
        slur_count_col = variant + "_count"
        slur_freq_col = variant + "_freq"
        all_counts[slur_freq_col] = all_counts[slur_count_col].map(
            float) / all_counts["total_count"]

    # Save results in ubiquitous CSV format
    output_prefix = env.get("RESULTS_PATH") + \
        "/slurFreq/" + output_prefix
    csv_output_name = output_prefix + ".csv"
    all_counts.to_csv(csv_output_name, index=True)

    # Generate format for nivo https://nivo.rocks/line/
    nivo_output_name = output_prefix + ".json"
    nivo_counts = []
    for variant in main_variants:
        slur_freq_col = variant + "_freq"
        slur_data = pd.DataFrame(data={"x": [x.strftime(
            "%d-%b-%Y") for x in list(all_counts.index.values)], "y": list(all_counts[slur_freq_col])})
        nivo_counts.append({"id": variant, "data": slur_data.to_dict("records")})
    with open(nivo_output_name, "w") as nivoFile:
        json.dump(nivo_counts, nivoFile)

    return main_variants


def by_week(file_prefix, main_variants):
    """Aggregate the results from count_slurs by week.

    :param file_prefix: Prefix used for count_slurs.
    :type file_prefix: str
    :param main_variants: The main variant for each slur, used as column title.
    :type main_variants: list(str)

    """

    # Paths to files
    input_name = env.get("RESULTS_PATH") + \
        "/slurFreq/" + file_prefix + ".csv"
    output_prefix = env.get("RESULTS_PATH") + \
        "/slurFreq/" + file_prefix + "_by_week"
    csv_output_name = output_prefix + ".csv"
    nivo_output_name = output_prefix + ".json"

    # Load daily counts
    data = pd.read_csv(input_name)

    # Drop daily freq columns
    col_names = ["day", "total_count"] + \
        [(variant + '_count') for variant in main_variants]
    data = data[col_names]

    # Resample by week
    data.index = pd.to_datetime(data["day"])
    week_data = data.resample('W').sum()

    # Divide by weekly total to get frequency
    for variant in main_variants:
        slur_count_col = variant + "_count"
        slur_freq_col = variant + "_freq"
        week_data[slur_freq_col] = week_data[slur_count_col].map(
            float) / week_data["total_count"]

    # Save results in ubiquitous CSV format
    week_data.to_csv(csv_output_name, index=True)

    # Generate format for nivo https://nivo.rocks/line/
    nivo_counts = []
    for variant in main_variants:
        slur_freq_col = variant + "_freq"
        slur_data = pd.DataFrame(data={"x": [pd.to_datetime(x).strftime(
            "%d-%b-%Y") for x in list(week_data.index.values)], "y": list(week_data[slur_freq_col])})
        nivo_counts.append({"id": variant, "data": slur_data.to_dict("records")})
    with open(nivo_output_name, "w") as nivoFile:
        json.dump(nivo_counts, nivoFile)


def run_analysis(output_prefix, slurs_path, date_format):
    """Main function.

    :param output_prefix: Prefix for the output files. The files will be saved in the "slurFreq" results folder.
    :type output_prefix: str
    :param slurs_path: Full path to the json file holding the list of slurs and variants to count.
    :type slurs_path: str
    :param date_format: String defining the format of dates in the dataset.
    :type date_format: str

    """
    slurs = []
    with open(slurs_path, "r") as slurs_file:
        slurs = json.load(slurs_file)

    main_variants = count_slurs(output_prefix, slurs, date_format)
    by_week(output_prefix, main_variants)


def parse_arguments():
    """Parse script arguments.

    :return: The command line arguments entered by the user.
    :rtype: ArgumentParser object

    """

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Compute the frequency of sinophobic slurs in the dataset over time.")

    # Positional mandatory arguments
    parser.add_argument(
        "output_prefix", help="Prefix for the names of the output files.")
    parser.add_argument(
        "slurs_path", help="Full path to the json file holding the list of slurs and variants to count. Must contain a list of lists of slurs. Nested lists are variants of the same slur.")

    # Optional arguments
    parser.add_argument("-d",
                        "--date_format", help="String defining the format of dates in the dataset.", default="%a %b %d %H:%M:%S %z %Y")

    # Parse arguments
    args = parser.parse_args()

    return args


args = parse_arguments()

run_analysis(args.output_prefix, args.slurs_path, args.date_format)
