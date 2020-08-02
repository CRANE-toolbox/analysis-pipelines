# Main preprocessing module

import argparse
import pandas as pd
from csv import reader
from os import listdir
from os.path import isfile, join, splitext, basename
import src.preprocess.preprocessTools

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

    # Write to a CSV file, named from the input file with "_preprocessed" appended
    input_file_name = splitext(basename(file_path))[0]
    output_file = output_path + input_file_name + "_preprocessed"
    csv_writer = csv.writer(output_file, quoting=csv.QUOTE_MINIMAL)

    # Write header
    csv_writer.writerow(["id", "original_text", "clean_text", "timestamp"])

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
                buffer_data = []
                buffer_size = 0

        # Saving incomplete buffer when end of file is reached
        if buffer_size > 0:
            csv_writer.writerows(buffer_data)
    except Exception as e:
        print(e)
        return False

    return True


def list_files(input_path, pickled_input=False):
    """ List all CSV (or pickled) files in the specified directory.

    :param input_path: Path to the directory containing the files.
    :type input_path: str
    :param pickled_input: True if the input is in pickled pandas DataFrame rather than CSV files.
    :type pickled_input: bool
    :return: A list of the paths to the input files.
    :rtype: list(str)

    """

    extension = ".csv"
    if pickled_input:
        extension = ".pickle"

    # Iterates over the content of the directory and keep only files with the correct extension
    # The search is not recursive!
    input_paths = [join(input_path, f) for f in listdir(
        input_path) if (isfile(join(input_path, f)) and splitext(f)[-1].lower() == extension)]
    return input_paths


def parse_arguments():
    """Parse script arguments.

    :return: The command line arguments entered by the user.
    :rtype: ArgumentParser object

    """

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Dataset preprocessing. Prepare the text of each tweet for analysis and count the number of tweets per day.")

    # Positional mandatory arguments
    parser.add_argument(
        "input_path", help="Path to the folder containing the dataset formated with the *import* module, or a single file.")
    parser.add_argument(
        "output_path", help="Path to the folder where the preprocessed dataset should be saved.")

    # Optional arguments
    parser.add_argument("-pi", "--pickled_input",
                        help="The dataset to load is stored in pickled pandas DataFrame rather than CSV files.",
                        action='store_true')
    parser.add_argument("-po", "--pickled_output",
                        help="The output dataset is saved in pickled pandas DataFrame rather than CSV files.",
                        action='store_true')
    parser.add_argument("-url", "--remove_url",
                        help="Use this flag to remove URLs from the tweets instead of replacing them with 'url'",
                        action='store_false')
    parser.add_argument("-mention", "--remove_mentions",
                        help="Use this flag to remove user mentions '@userHandle' from the tweets instead of replacing them with 'atUser'",
                        action='store_false')
    parser.add_argument("-hashtag", "--segment_hashtags",
                        help="Use this flag to segment hashtags instead of simply removing the preceding '#' character. See documentation for details on the segmentation.",
                        action='store_false')
    parser.add_argument("-punct", "--remove_punctuation",
                        help="Use this flag to remove all punctuation expect hyphens, instead of replacing repeated symbols and newlines.",
                        action='store_false')
    parser.add_argument("-num", "--remove_numbers",
                        help="Use this flag to remove all numbers from the tweets instead of replacing them with their text version",
                        action='store_false')

    # Parse arguments
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = parse_arguments()

    # Check whether the input_path correspond to a single file or a directory
    if isfile(input_path):
        # Single file
        input_paths = [input_path]
    else:
        # Get the list of files from the directory
        input_paths = list_files(input_path, pickled_input)
        # If the directory did not contain any file with the right extension
        if len(input_paths) == 0:
            print("No appropriate file could be found in the provided directory.")
            print("Please remember that the search is not recursive.")
            return

    # /!\ Only deals with CSV inputs and outputs right now
    if pickled_input or pickled_output:
        print("pickled input and output not yet supported")
        return
    failed_file_reading = 0
    # For each input file
    for file_path in input_paths:
        with open(file_path, 'r') as csv_input:
            csv_reader = reader(csv_input)
            # Check that the header has the proper columns
            header = next(csv_reader)
            if header != ["id", "original_text", "timestamp"]:
                print("The CSV file header should be ['id', 'original_text', 'timestamp'"].)
                failed_file_reading += 1
                continue
            success= preprocess_csv_file(csv_reader, file_path, args.output_path, args.remove_url, args.remove_mentions, args.segment_hashtags, args.remove_punctuation, args.remove_numbers)
            if not success:
                failed_file_reading += 1

    print("Failed to read %d because of improper format or headers." %
          failed_file_reading)
