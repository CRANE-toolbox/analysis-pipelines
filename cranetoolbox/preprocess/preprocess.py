# Main preprocessing module

import pandas as pd
from csv import reader, writer
from os import listdir
from os.path import isfile, join, splitext, basename
from cranetoolbox.preprocess import preprocessTools

MAX_BUFFER_SIZE = 1000


def preprocessing_text(text, replace_or_remove_url, replace_or_remove_mentions, remove_hashtag_or_segment, replace_or_remove_punctuation, replace_or_remove_numbers):
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


def preprocessing_tweet(tweet, replace_or_remove_url, replace_or_remove_mentions, remove_hashtag_or_segment, replace_or_remove_punctuation, replace_or_remove_numbers):
    """Preprocess the text content of a tweet for analysis.

    :param text: An array with the tweet info, in format [id, original_text, timestamp].
    :type text: list()
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


def merge_counts_dataframe(df_list):
    df_final = pd.concat(df_all)
    return df_final.groupby('date').agg({'counts': 'sum'})


def transform_to_date_counts_dataframe(buffer_data):

    df_counts = pd.DataFrame.from_records(buffer_data)

    df_counts[3] = pd.to_datetime(df_counts[3])
    df_counts[3] = df_counts[3].apply(lambda x: x.strftime('%Y-%m-%d'))

    return df[3].value_counts().rename_axis('date').to_frame('counts')

    '''
    Goal: Table with the number of tweets in the database for each date

    1/ takes an array of arrays
    2/ transform it into a pandas DataFrame
    3/ transform the timestamp in the last column into a date format (just year-month-day, no time info)
    4/ do a groupby count of this date column
    5/ returns this groupby DataFrame

    Call that function just before/after csv_writer.writerows(buffer_data) (lines 168 and 174 at the moment) and append the result to an array of DataFrames

    And when the loop is over, concatenate those DataFrames and do a groupby sum to add the totals

    Testing - need to use it as a package function now, not a script function.
    Also, check this https://docs.pytest.org/en/stable/goodpractices.html#goodpractices to install the package in editable mode
    '''


def preprocess_csv_file(csv_reader, file_path, output_path, replace_or_remove_url, replace_or_remove_mentions, remove_hashtag_or_segment, replace_or_remove_punctuation, replace_or_remove_numbers):
    """Short summary.

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
    :return: True if the file was properly preprocessed.
    :rtype: bool

    """

    # Reading and saving in chunks to avoid memory overload
    buffer_size = 0
    buffer_data = []
    date_dataframes = []

    # Write to a CSV file, named from the input file with "_preprocessed" appended
    input_file_name = splitext(basename(file_path))[0]
    output_file = output_path + input_file_name + "_preprocessed"
    csv_writer = writer(output_file, quoting=csv.QUOTE_MINIMAL)

    # Catch errors, no specific exception handling for now
    try:
        # For each line
        for row in csv_reader:
            # Preprocess the text
            clean_tweet = preprocessing_tweet(row, replace_or_remove_url, replace_or_remove_mentions,
                                              remove_hashtag_or_segment, replace_or_remove_punctuation, replace_or_remove_numbers)
            buffer_data.append(clean_tweet)
            buffer_size += 1
            # If the buffer is full, save to file
            if buffer_size >= MAX_BUFFER_SIZE:
                csv_writer.writerows(buffer_data)
                date_dataframes.append(transform_to_date_counts_dataframe(buffer_data))
                buffer_data = []
                buffer_size = 0

        # Saving incomplete buffer when end of file is reached
        if buffer_size > 0:
            csv_writer.writerows(buffer_data)
            date_dataframes.append(transform_to_date_counts_dataframe(buffer_data))
    except Exception as e:
        print(e)
        return False

    date_dataframe = merge_counts_dataframe(date_dataframes)
    return date_dataframe


def list_files(input_path):
    """ List all CSV files in the specified directory.

    :param input_path: Path to the directory containing the files.
    :type input_path: str
    :return: A list of the paths to the input files.
    :rtype: list(str)

    """

    extension = ".csv"

    # Iterates over the content of the directory and keep only files with the correct extension
    # The search is not recursive!
    input_paths = [join(input_path, f) for f in listdir(
        input_path) if (isfile(join(input_path, f)) and splitext(f)[-1].lower() == extension)]
    return input_paths
