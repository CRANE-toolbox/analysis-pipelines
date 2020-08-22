# Main preprocessing module

import csv
import os
from os import makedirs
from os.path import splitext, basename, exists
from typing import List, Optional

import pandas as pd

from cranetoolbox.preprocess import preprocessTools

MAX_BUFFER_SIZE = 1000


def preprocessing_text(text: str, replace_or_remove_url: bool, replace_or_remove_mentions: bool,
                       remove_hashtag_or_segment: bool,
                       replace_or_remove_punctuation: bool, replace_or_remove_numbers: bool) -> str:
    """Preprocess the text content of a tweet for analysis.

    :param text: Text content of a tweet.
    :type text: str
    :param replace_or_remove_url: True to replace URLs, False to remove them.
    :type replace_or_remove_url: bool
    :param replace_or_remove_mentions: True to replace mentions, False to remove them.
    :type replace_or_remove_mentions: bool
    :param remove_hashtag_or_segment: True to remove '#' in front of hashtags, False to segment hashtags.
    :type remove_hashtag_or_segment: bool
    :param replace_or_remove_punctuation: True to replace multiple punctuation, False to remove all punctuation.
    :type replace_or_remove_punctuation: bool
    :param replace_or_remove_numbers: True to replace numbers by their text version, False to remove them.
    :type replace_or_remove_numbers: bool
    :return: The clean version of the text.
    :rtype: str

    """

    # Lowercase
    lowercase_text = text.lower()

    # Remove unicode noise
    no_unicode_text = preprocessTools.remove_unicode(
        lowercase_text)  # Technique 0

    if replace_or_remove_url:
        # Replace URLs
        no_link_text = preprocessTools.replace_url(
            no_unicode_text)  # Technique 1
    else:
        # Remove URLs
        no_link_text = preprocessTools.remove_url(no_unicode_text)

    if replace_or_remove_mentions:
        # Replace mentions by 'atUser'
        no_mention_text = preprocessTools.replace_at_user(
            no_link_text)  # Technique 1
    else:
        # Remove mentions
        no_mention_text = preprocessTools.remove_at_user(no_link_text)

    if remove_hashtag_or_segment:
        # Remove '#' character from hashtags
        no_hashtag_text = preprocessTools.remove_hashtag_in_front_of_word(
            no_mention_text)  # Technique 1
    else:
        # Segment hashtags
        no_hashtag_text = preprocessTools.replace_hashtags(no_mention_text)

    # Replace contractions
    # Technique 3: replaces contractions to their equivalents
    no_contraction_text = preprocessTools.replace_contraction(no_hashtag_text)

    if replace_or_remove_punctuation:
        # Replace punctuation repetition by a descriptive tag
        # Technique 5: replaces repetitions of exlamation marks with the tag "multiExclamation"
        simple_punctuation_text = preprocessTools.replace_multi_exclamation_mark(
            no_contraction_text)
        # Technique 5: replaces repetitions of question marks with the tag "multiQuestion"
        simple_punctuation_text = preprocessTools.replace_multi_question_mark(
            simple_punctuation_text)
        # Technique 5: replaces repetitions of stop marks with the tag "multiStop"
        simple_punctuation_text = preprocessTools.replace_multi_stop_mark(
            simple_punctuation_text)
        # Replace new line with space
        clean_punctuation_text = preprocessTools.replace_new_line(
            simple_punctuation_text)
    else:
        clean_punctuation_text = preprocessTools.remove_punctuation(
            no_contraction_text)

    if replace_or_remove_numbers:
        clean_text = preprocessTools.replace_numbers(clean_punctuation_text)
    else:
        clean_text = preprocessTools.remove_numbers(clean_punctuation_text)

    return clean_text


def preprocessing_tweet(tweet: [str, str, str], replace_or_remove_url: bool, replace_or_remove_mentions: bool,
                        remove_hashtag_or_segment: bool,
                        replace_or_remove_punctuation: bool, replace_or_remove_numbers: bool) -> [str, str, str, str]:
    """Preprocess the text content of a tweet for analysis.

    :param tweet: An array with the tweet info, in format [id, original_text, timestamp].
    :type tweet: list()
    :param replace_or_remove_url: True to replace URLs, False to remove them.
    :type replace_or_remove_url: bool
    :param replace_or_remove_mentions: True to replace mentions, False to remove them.
    :type replace_or_remove_mentions: bool
    :param remove_hashtag_or_segment: True to remove '#' in front of hashtags, False to segment hashtags.
    :type remove_hashtag_or_segment: bool
    :param replace_or_remove_punctuation: True to replace multiple punctuation, False to remove all punctuation.
    :type replace_or_remove_punctuation: bool
    :param replace_or_remove_numbers: True to replace numbers by their text version, False to remove them.
    :type replace_or_remove_numbers: bool
    :return: An array with the tweet info, including clean text, in format [id, original_text, clean_text, timestamp].
    :rtype: list()

    """

    text = tweet[1]
    clean_text = preprocessing_text(text, replace_or_remove_url, replace_or_remove_mentions,
                                    remove_hashtag_or_segment, replace_or_remove_punctuation, replace_or_remove_numbers)
    clean_tweet = [tweet[0], tweet[1], clean_text, tweet[2]]
    return clean_tweet


def merge_counts_dataframe(counts_list: List[pd.DataFrame]) -> Optional[pd.DataFrame]:
    """Get merged counts per day from a list of DataFrame

    :param counts_list: List of DataFrame with the count of occurences per day.
    :type counts_list: list(pandas.DataFrame)
    :return: A DataFrame, sum of the info contained in the input list
    :rtype: pandas.DataFrame

    """

    if len(counts_list) == 0:
        return None
    counts_merged = pd.concat(counts_list)
    return counts_merged.groupby('date').agg({'counts': 'sum'})


def count_per_day(data: [str, str, str, str]) -> pd.DataFrame:
    """Count occurences per day in a list of data records.

    :param data: List of data records, where the timestamp is the fourth column.
    :type data: list(list())
    :return: A DataFrame with the count of occurences per day.
    :rtype: pandas.DataFrame

    """

    counts = pd.DataFrame.from_records(data)

    counts[3] = pd.to_datetime(counts[3])
    counts[3] = counts[3].apply(lambda x: x.strftime('%Y-%m-%d'))

    return counts[3].value_counts().rename_axis('date').to_frame('counts')


def preprocess_csv_file(csv_reader: csv.reader, file_path: str, output_path: str, replace_or_remove_url: bool,
                        replace_or_remove_mentions: bool,
                        remove_hashtag_or_segment: bool, replace_or_remove_punctuation: bool,
                        replace_or_remove_numbers: bool) -> Optional[pd.DataFrame]:
    """Preprocess a single CSV file.

    :param csv_reader: The reader for the input CSV file, without header.
    :type csv_reader: csv.reader
    :param file_path: The path to the input file.
    :type file_path: str
    :param output_path: The path to the output folder.
    :type output_path: str
    :param replace_or_remove_url: True to replace URLs, False to remove them.
    :type replace_or_remove_url: bool
    :param replace_or_remove_mentions: True to replace mentions, False to remove them.
    :type replace_or_remove_mentions: bool
    :param remove_hashtag_or_segment: True to remove '#' in front of hashtags, False to segment hashtags.
    :type remove_hashtag_or_segment: bool
    :param replace_or_remove_punctuation: True to replace multiple punctuation, False to remove all punctuation.
    :type replace_or_remove_punctuation: bool
    :param replace_or_remove_numbers: True to replace numbers by their text version, False to remove them.
    :type replace_or_remove_numbers: bool
    :return: Dataframe of processed CSV file
    :rtype: pd.DataFrame

    """

    # Reading and saving in chunks to avoid memory overload
    buffer_size = 0
    buffer_data = []
    date_dataframes = []

    # Create output folder if it does not exists
    if not exists(output_path):
        makedirs(output_path)

    # Write to a CSV file, named from the input file with "_preprocessed.csv" appended
    input_file_name = splitext(basename(file_path))[0]
    output_file_path = os.path.join(output_path + "/", (input_file_name + "_preprocessed.csv"))
    with open(output_file_path, 'w+') as output_file:
        csv_writer = csv.writer(output_file, quoting=csv.QUOTE_MINIMAL)

        # Catch errors, no specific exception handling for now
        try:
            row_num = 0
            # For each line
            for row in csv_reader:
                print(f'\rProcessing line: {row_num}', end="")
                row_num += 1
                # Preprocess the text
                clean_tweet = preprocessing_tweet(row, replace_or_remove_url, replace_or_remove_mentions,
                                                  remove_hashtag_or_segment, replace_or_remove_punctuation,
                                                  replace_or_remove_numbers)
                buffer_data.append(clean_tweet)
                buffer_size += 1
                # If the buffer is full, save to file
                if buffer_size >= MAX_BUFFER_SIZE:
                    csv_writer.writerows(buffer_data)
                    date_dataframes.append(count_per_day(buffer_data))
                    buffer_data = []
                    buffer_size = 0

            # Saving incomplete buffer when end of file is reached
            if buffer_size > 0:
                csv_writer.writerows(buffer_data)
                date_dataframes.append(count_per_day(buffer_data))
        except Exception as e:
            print(e)
            return None
        finally:
            # Print newline to escape out of line used for status updates
            print()

    date_dataframe = merge_counts_dataframe(date_dataframes)
    return date_dataframe
