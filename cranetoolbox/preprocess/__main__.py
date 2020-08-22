import argparse
import csv

from cranetoolbox.fileHandler import scan_folder_csv
from cranetoolbox.preprocess.preprocess import *


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Dataset preprocessing. Prepare the text of each tweet for analysis and count the number of "
                    "tweets per day.")

    # Positional mandatory arguments
    parser.add_argument(
        "input_path", help="Path to the folder containing the dataset formated with the *import* module, or a single "
                           "file.")
    parser.add_argument(
        "output_path", help="Path to the folder where the preprocessed dataset should be saved.")

    # Optional arguments
    parser.add_argument("-url", "--remove-url",
                        help="Use this flag to remove URLs from the tweets instead of replacing them with 'url'",
                        action='store_false')
    parser.add_argument("-mention", "--remove-mentions",
                        help="Use this flag to remove user mentions '@userHandle' from the tweets instead of "
                             "replacing them with 'atUser'",
                        action='store_false')
    parser.add_argument("-hashtag", "--segment-hashtags",
                        help="Use this flag to segment hashtags instead of simply removing the preceding '#' "
                             "character. See documentation for details on the segmentation.",
                        action='store_false')
    parser.add_argument("-punct", "--remove-punctuation",
                        help="Use this flag to remove all punctuation expect hyphens, instead of replacing repeated "
                             "symbols and newlines.",
                        action='store_false')
    parser.add_argument("-num", "--remove-numbers",
                        help="Use this flag to remove all numbers from the tweets instead of replacing them with "
                             "their text version",
                        action='store_false')

    # Parse arguments
    args = parser.parse_args()

    # Scan supplied directory for files
    input_paths = scan_folder_csv(args.input_path)
    print(f"Found the following files: {[str(x) for x in input_paths]}")
    # If the directory did not contain any file with the right extension
    if len(input_paths) == 0:
        print("No appropriate file could be found in the provided directory.")
        return

    failed_file_reading = 0
    date_dataframes = []
    # For each input file
    for file_path in input_paths:
        with open(file_path, 'r') as csv_input:
            print(f"Processing file {str(file_path)}")
            csv_reader = csv.reader(csv_input)
            date_dataframe = preprocess_csv_file(csv_reader, file_path, args.output_path, args.remove_url,
                                                 args.remove_mentions, args.segment_hashtags, args.remove_punctuation,
                                                 args.remove_numbers)
            if date_dataframe is not None:
                date_dataframes.append(date_dataframe)
            else:
                failed_file_reading += 1

    if len(date_dataframes) > 0:
        final_dataframe = merge_counts_dataframe(date_dataframes)
        final_dataframe.to_csv('all_date_counts.csv')

    if failed_file_reading > 0:
        print("Failed to read %d files." % failed_file_reading)
    else:
        print("Fully successful")


if __name__ == '__main__':
    main()
