# Take a list of keywords (with spelling variants) and compute their daily frequency in the entire dataset

import json
from csv import reader
from datetime import datetime
from typing import Dict, List

import pandas as pd

MAX_BUFFER_SIZE = 1000


def transform_date_format(df: pd.DataFrame) -> pd.DataFrame:
    """Add the date of the "timestamp" column of a DataFrame to a "day" column.

    :param df: A DataFrame with a "timestamp" column containing pandas datetime objects.
    :type df: DataFrame
    :return: df with a new column "day" that corresponds to the date version of the "timestamp" column.
    :rtype: DataFrame

    """

    timestamps = df["timestamp"].to_list()
    days = [datetime.date(t) for t in timestamps]
    df["day"] = days
    return df


def get_keywords(path: str) -> Dict[str, List[str]]:
    """Load the keywords and their variants.

    :param path: Path to the JSON file with the keywords.
    :type path: str
    :return: The dictionary with the keywords and their variants.
    :rtype: dict(str, list(str))

    """

    keywords = []
    try:
        with open(path, "r") as keywords_file:
            keywords = json.load(keywords_file)
    except FileNotFoundError as e:
        print("Could not find specified keywords file.")
        print(e)
        raise e
    except json.JSONDecodeError as e:
        print("Specified keywords file does not contain a valid JSON.")
        print(e)
        raise e
    except Exception as e:
        print("Unknown error while reading keywords")
        print(e)
        raise e
    return keywords 


def get_tweet_counts(path: str) -> pd.DataFrame:
    """Load the DataFrame with the daily tweet counts.

    :param path: Path to the file with the number of tweets per day.
    :type path: str
    :return: DataFrame with the number of tweets for each day in the dataset.
    :rtype: pandas.DataFrame

    """

    try:
        tweet_counts = pd.read_csv(path, parse_dates=[0], infer_datetime_format=True)
    except FileNotFoundError as e:
        print("Could not find specified tweet counts file.")
        print(e)
        raise e
    except Exception as e:
        print("Unexpected error while reading the keywords file.")
        print(e)
        raise e

    return tweet_counts


def detect_keywords(text: str, keywords: Dict[str, List[str]]) -> Dict[str, bool]:
    """Look for each keyword (with variants) in a tweet.

    :param text: The preprocessed text of the tweet.
    :type text: str
    :param keywords: The dictionary of keywords with their variants.
    :type keywords: dict(str, list(str))
    :return: A dictionary indicating the presence or absence of each keyword.
    :rtype: dict(str, bool)

    """

    tweet_info = {}
    for main_variant in keywords.keys():
        # Detect if one of the variants of the keyword is present in the tweet
        variants = keywords[main_variant]
        tweet_info[main_variant] = any([variant in text for variant in variants])

    return tweet_info


def aggregate_counts(data, main_variants: List[str], date_format: str) -> pd.DataFrame:
    """Create a DataFrame with keywords daily counts.

    :param data: List of dictionaries, each dictionary with a date, boolean indicators for the presence of each keyword, and a 1-valued 'total' column.
    :type data: list(dict())
    :param main_variants: List of the keywords main variants.
    :type main_variants: list(str)
    :param date_format: String defining the format of dates in the dataset.
    :type date_format: str
    :return: A DataFrame with counts for each keyword and each day.
    :rtype: pandas.DataFrame

    """

    # Get data into a DataFrame
    occurences = pd.DataFrame(data)

    # Transform timestamps to a date format, adding a 'day' column
    occurences["timestamp"] = pd.to_datetime(
        occurences["timestamp"], format=date_format)
    occurences = transform_date_format(occurences)

    # Aggregate counts:
    #   - sum by date
    #   - rename columns with the suffix '_count'
    #   - reset index so the temp_counts DataFrames for the different chunks can later be concatenated
    count_columns = ["day", "total"] + main_variants
    counts = occurences[count_columns].groupby(
        "day").sum().add_suffix('_count').reset_index()

    return counts


def count_keywords(input_paths: List[str], keywords: Dict[str, List[str]], date_format: str) -> pd.DataFrame:
    """Search all tweets for keywords and count their occurences per day.

    :param input_paths: The list of the paths to the input files.
    :type input_paths: list(str)
    :param keywords: The dictionary of keywords with their variants.
    :type keywords: dict(str, list(str))
    :param date_format: String defining the format of dates in the dataset.
    :type date_format: str
    :return: A DataFrame with the number of occurences of each keyword for each day.
    :rtype: pandas.DataFrame

    """

    # List the main variants of the keywords (e.g. the keys of the keywords dict)
    main_variants = list(keywords.keys())

    # Create a list of intermediate DataFrames to store the day-aggregated counts for each chunk of the dataset
    chunks_counts = []

    # For each input file
    for input_path in input_paths:
        try:
            with open(input_path, 'r') as csv_input:
                csv_reader = reader(csv_input)
                # Reading and saving in chunks to avoid memory overload
                buffer_size = 0
                buffer_data = []
                # Catch errors, no specific exception handling for now
                try:
                    # For each line
                    for row in csv_reader:
                        # Detect keywords
                        clean_text = row[2]
                        has_keyword = detect_keywords(clean_text, keywords)
                        has_keyword["timestamp"] = row[3]
                        has_keyword["total"] = 1  # Easier group_by later
                        buffer_data.append(has_keyword)
                        buffer_size += 1

                        # If the buffer is full, aggregate daily counts
                        if buffer_size >= MAX_BUFFER_SIZE:
                            temp_counts = aggregate_counts(buffer_data, main_variants, date_format)
                            # Save aggregate DataFrame to list
                            chunks_counts.append(temp_counts)
                            del temp_counts
                            buffer_data = []
                            buffer_size = 0

                    # Saving incomplete buffer when end of file is reached
                    if buffer_size > 0:
                        temp_counts = aggregate_counts(buffer_data, main_variants, date_format)
                        # Save aggregate DataFrame to list
                        chunks_counts.append(temp_counts)
                except Exception as e:
                    print("Unknown error while counting keywords")
                    print(e)
                    raise e
        except Exception as e:
            print("Cannot read CSV input file: %s" % input_path)
            print(e)
            raise e

    # Concatenate all chunks
    daily_counts = pd.concat(chunks_counts, ignore_index=True)
    # Aggregate over chunks
    daily_counts = daily_counts.groupby("day").sum()

    return daily_counts


def counts_to_freq(keyword_counts: pd.DataFrame, keywords: Dict[str, List[str]]) -> pd.DataFrame:
    """For each day, divide the count for each keyword by the daily total.

    :param keyword_counts: DataFrame with the number of occurences of each keyword for each day.
    :type keyword_counts: pandas.DataFrame
    :param keywords: The dictionary of keywords with their variants.
    :type keywords: dict(str, list(str))
    :return: A DataFrame with the count and frequency of each keyword for each day.
    :rtype: pandas.DataFrame

    """

    # List the main variants of the keywords (e.g. the keys of the keywords dict)
    main_variants = list(keywords.keys())

    # Divide by daily total to get frequency
    for keyword in main_variants:
        keyword_count_col = keyword + "_count"
        keyword_freq_col = keyword + "_freq"
        keyword_counts[keyword_freq_col] = keyword_counts[keyword_count_col].map(
            float) / keyword_counts["total_count"]

    return keyword_counts
