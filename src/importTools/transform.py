import csv
import json
import os
import tarfile
from itertools import islice
from typing import List

# The max number of lines that will be written and held in memory at any given point
MAX_BUFFER_SIZE = 10000


class TransformationOptions:
    """
    A simple class to handle ETL options as specified in the driver
    """
    filter_language: str
    include_retweet: bool
    max_in_memory_size: int

    def __init__(self, languagefilter: str, retweets: bool, max_in_mem: int):
        self.filter_language = languagefilter
        self.include_retweet = retweets
        self.max_in_memory_size = max_in_mem


def process_files(file_list: List[str], opts: TransformationOptions, csv_output_path: str) -> (int, int):
    """
    This the top level file function for combing files in the input set into a single output file.
    Files are saved into a single CSV file with three columns as specified by the params.
    :param file_list: paths to files to be processed
    :type file_list: List(str)
    :param opts: An instance of the transformation options, used to control filtering and parsing of tweets
    :type opts: TransformationOptions
    :param csv_output_path: Full output path, folder, filename and extension
    :type csv_output_path: str
    :return: A tuple of (successes, failures) that represents the number of lines written to the file
    :rtype: Tuple(int, int)
    """
    line_count = 0
    failure_count = 0
    for file in file_list:
        print("Processing file " + str(file))
        if tarfile.is_tarfile(file):
            lines_written, failures = process_tar_file(file, opts, csv_output_path)
            line_count += lines_written
            failure_count += failures
        else:
            try:
                with open(file, 'r') as f:
                    if os.stat(file).st_size < opts.max_in_memory_size * 1000000:
                        # load the entire file into memory because it is small
                        full_file = f.readlines()
                        lines_written, failures = write_tweets_by_chunk(full_file, csv_output_path, opts)
                        line_count += lines_written
                        failure_count += failures
                    else:
                        # Iterate over lines in chunks
                        while True:
                            chunk = islice(f, MAX_BUFFER_SIZE)
                            if not chunk:
                                # End of file returns an empty list
                                break
                            lines_written, failures = write_tweets_by_chunk(chunk, csv_output_path, opts)
                            line_count += lines_written
                            failure_count += failures
            except UnicodeDecodeError:
                print("Could not open file " + str(file) + " but recovered and will continue")
                continue

    return line_count, failure_count


def write_tweets_by_chunk(lines, csv_output_path: str, opts: TransformationOptions) -> (int, int):
    """
    Takes in an arbitrarily sized number of lines and writes them out in chunks to the filesystem
    :param lines: Lines of tweets to process and write to file
    :type lines: List of strings or buffer
    :param csv_output_path: Full output path of CSV file, including filename and extension
    :type csv_output_path: str
    :param opts: Transformation options
    :type opts: TransformationOptions
    :return: Tuple of write pass/failures
    :rtype: Tuple(int, int)
    """
    line_count = 0
    parse_failure_count = 0
    # Supports
    with open(csv_output_path, 'a+') as csv_file:
        while True:
            chunk = list(islice(lines, MAX_BUFFER_SIZE))
            if not chunk or chunk == []:
                # End of iterable
                break
            filtered_chunk, failure_count = filter_lighten_chunk(chunk, opts)
            parse_failure_count += failure_count
            line_count += len(filtered_chunk)
            csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL).writerows(filtered_chunk)
    return line_count, parse_failure_count


def filter_lighten_chunk(chunk, opts: TransformationOptions) -> (List[dict], int):
    """
    This takes a chunk of lines(some arbitrary number) and lightens them, selecting only the important keys
    :param chunk: The chunk of lines to process
    :type chunk: list(str) or buffer of str
    :param opts: Transformation options
    :type opts: TransformationOptions
    :return: List of filtered tweets and parse failure count
    :rtype: list[dict], int
    """
    output_buffer = []
    parse_failure_count = 0
    for line in chunk:
        try:
            tweet = parse_tweet(line)
        except json.JSONDecodeError as e:
            parse_failure_count += 1
            continue
        if matches_language_filter(tweet, opts) and not is_retweet(tweet):
            try:
                light_tweet = lighten_tweet(tweet)
            except ValueError:
                # Issue parsing JSON tweet, raise this as a failure and continue
                parse_failure_count += 1
                continue
            output_buffer.append(light_tweet)
    return output_buffer, parse_failure_count


def process_tar_file(file: str, opts: TransformationOptions, csv_output_path: str) -> (int, int):
    """
    This handles a single tar file, processes any uncompressed nested files contained within the archive.
    THis cannot handle nested compression, ie a tar inside a tar.
    :param file: Path to tar file
    :type file: str
    :param opts: Transformation options
    :type opts: TransformationOptions
    :param csv_output_path: Output path for the combined CSV file
    :type csv_output_path: str
    :return: pass/fail counts
    :rtype: tuple(int, int)
    """
    line_count = 0
    members = []
    failure_count = 0
    with tarfile.open(file, 'r|*') as tf:
        members = tf.getmembers()
    with tarfile.open(file, 'r|*') as tf:
        for file in members:
            # Returns an io.buffer, should not load entire file into memory...?
            buffer = tf.extractfile(file)
            lines_written, errors = write_tweets_by_chunk(buffer, csv_output_path, opts)
            line_count += lines_written
            failure_count += errors
    return line_count, failure_count


def matches_language_filter(tweet: dict, opts: TransformationOptions) -> bool:
    """
    Check if the passed tweet matches the language filter as specified in the TransformationOptions instance
    :param tweet: A dictionary representing a full JSON tweet(with no data removed etc)
    :type tweet: dict
    :param opts: Transformation options
    :type opts: TransformationOptions
    :return: True/False if the tweet matches the user specified language filter
    :rtype: bool
    """
    language = tweet.get("lang", None)
    return language == opts.filter_language


def is_retweet(tweet: dict) -> bool:
    """
    Checks if the passed tweet is retweeted. Using the mechanism included in the tweet, a retweet flag. But also
    checks for so called "manual" retweets where a user uses the form of "RT [original tweet]"
    :param tweet: A dictionary representing a single tweet
    :type tweet: dict
    :return: True/False if the tweet has been labeled as a retweet.
    :rtype: bool
    """
    text = tweet.get("text", None)
    if len(text) >= 2 and text[0:2] == "RT":
        return True
    if not tweet.get("retweeted", False):
        # If the field does not exist that means it isn't a "modern" retweet
        # There are two types of retweets, those done by hitting the RT button
        # and those done "manually" where someone uses the keyword RT: [Original Tweet]
        return False
    # If it got here, it must be a re-tweet.
    return True


def parse_tweet(tweet: str) -> dict:
    """
    A simple function to parse the passed JSON format tweet from str to dictionary.
    :param tweet: JSON tweet as a string
    :type tweet: str
    :return: Dictionary representing the JSON parse results of the passed tweet
    :rtype: dict
    """
    return json.loads(tweet)


def lighten_tweet(tweet: dict) -> (str, str, str):
    """
    This lightens a single tweet, pulling out only the most important values for
    processing and returning them as a tuple.
    :param tweet: a parsed JSON tweet
    :type tweet: dict
    :return: a tuple of the three values scraped from the passed tweet
    :rtype: tuple(str, str, str)
    """
    created_at = tweet.get("created_at", None)
    tweet_id = tweet.get("id", None)
    text = ""
    if tweet.get("truncated", False):
        ext_tweet = tweet.get("extended_tweet", None)
        if ext_tweet is not None:
            text = ext_tweet.get("full_text", "")
    else:
        text = tweet.get("text", "")
    # Simple verification to make sure the keys where found
    if not created_at:
        raise ValueError
    if not tweet_id:
        raise ValueError
    if text is "":
        raise ValueError
    # Strip newline chars from the tweet -- we do this here for ease of CSV writing
    text = " ".join(text.splitlines())
    return tweet_id, text, created_at
