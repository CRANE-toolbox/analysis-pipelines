import io
import tarfile
import json
import csv
import os
from itertools import islice, chain

MAX_BUFFER_SIZE = 10000


# A simple class to handle ETL options
class TransformationOptions:
    filter_language: str
    include_retweet: bool
    max_in_memory_size: int

    def __init__(self, languagefilter: str, retweets: bool, max_in_mem: int):
        self.filter_language = languagefilter
        self.include_retweet = retweets
        self.max_in_memory_size = max_in_mem


def process_files(file_list: [str], opts: TransformationOptions, output_path: str) -> (int, int):
    line_count = 0
    failure_count = 0
    for file in file_list:
        print("Processing file " + str(file))
        if tarfile.is_tarfile(file):
            lines_written, failures = process_tar_file(file, opts, output_path)
            line_count += lines_written
            failure_count += failures
        else:
            try:
                with open(file, 'r') as f:
                    if os.stat(file).st_size < opts.max_in_memory_size * 1000000:
                        # load the entire file into memory because it is small
                        full_file = f.readlines()
                        lines_written, failures = write_tweets_by_chunk(full_file, output_path, opts)
                        line_count += lines_written
                        failure_count += failures
                    else:
                        # Iterate over lines in chunks
                        while True:
                            chunk = islice(f, MAX_BUFFER_SIZE)
                            if not chunk:
                                # End of file returns an empty list
                                break
                            lines_written, failures = write_tweets_by_chunk(chunk, output_path, opts)
                            line_count += lines_written
                            failure_count += failures
            except UnicodeDecodeError as e:
                print("Could not open file " + str(file) + " but recovered and will continue")
                continue

    return line_count, failure_count


# Takes in an arbitrarily sized number of lines and writes them out in chunks to the filesystem
def write_tweets_by_chunk(lines, output_path: str, opts: TransformationOptions) -> (int, int):
    line_count = 0
    parse_failure_count = 0
    with open(output_path, 'a+', newline='\n', encoding="utf-8") as output_file:
        csv_writer = csv.writer(output_file, quoting=csv.QUOTE_MINIMAL)
        while True:
            print(line_count)
            chunk = list(islice(lines, MAX_BUFFER_SIZE))
            if not chunk or chunk == []:
                # End of iterable
                break
            filtered_chunk, failure_count = filter_lighten_chunk(chunk, opts)
            parse_failure_count += failure_count
            line_count += len(filtered_chunk)
            csv_writer.writerows(filtered_chunk)
    return line_count, parse_failure_count


def filter_lighten_chunk(chunk, opts: TransformationOptions) -> ([], int):
    output_buffer = []
    parse_failure_count = 0
    for line in chunk:
        try:
            tweet = parse_tweet(line)
        except json.JSONDecodeError as e:
            parse_failure_count += 1
            continue
        if matches_language_filter(tweet, opts) and not is_retweet(tweet):
            light_tweet = lighten_tweet(tweet)
            output_buffer.append(light_tweet)
    return output_buffer, parse_failure_count


def process_tar_file(file: str, opts: TransformationOptions, output_path: str) -> (int, int):
    line_count = 0
    members = []
    failure_count = 0
    with tarfile.open(file, 'r|*') as tf:
        members = tf.getmembers()
    with tarfile.open(file, 'r|*') as tf:
        for file in members:
            # Returns an io.buffer, should not load entire file into memory...?
            buffer = tf.extractfile(file)
            lines_written, errors = write_tweets_by_chunk(buffer, output_path, opts)
            line_count += lines_written
            failure_count += errors
    return line_count, failure_count


def matches_language_filter(tweet: dict, opts: TransformationOptions) -> bool:
    language = tweet.get("lang", None)
    return language == opts.filter_language


def is_retweet(tweet: dict) -> bool:
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
    return json.loads(tweet)


# lighten a single tweet
def lighten_tweet(tweet: dict) -> (str, str, str):
    created_at = tweet.get("created_at", None)
    tweet_id = tweet.get("id", None)
    text = ""
    if tweet.get("truncated", False):
        ext_tweet = tweet.get("extended_tweet", None)
        if ext_tweet is not None:
            text = ext_tweet.get("full_text", "")
    else:
        text = tweet.get("text", "")
    # Strip newline chars from the tweet -- we do this here for ease of CSV writing
    text = " ".join(text.splitlines())
    return tweet_id, created_at, text
