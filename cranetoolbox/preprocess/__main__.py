from cranetoolbox.preproces import *
import argparse


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Dataset preprocessing. Prepare the text of each tweet for analysis and count the number of tweets per day.")

    # Positional mandatory arguments
    parser.add_argument(
        "input_path", help="Path to the folder containing the dataset formated with the *import* module, or a single file.")
    parser.add_argument(
        "output_path", help="Path to the folder where the preprocessed dataset should be saved.")

    # Optional arguments
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

    # Check whether the input_path correspond to a single file or a directory
    if isfile(input_path):
        # Single file
        input_paths = [input_path]
    else:
        # Get the list of files from the directory
        input_paths = list_files(input_path)
        # If the directory did not contain any file with the right extension
        if len(input_paths) == 0:
            print("No appropriate file could be found in the provided directory.")
            print("Please remember that the search is not recursive.")
            return


    failed_file_reading = 0
    date_dataframes = []
    # For each input file
    for file_path in input_paths:
        with open(file_path, 'r') as csv_input:
            csv_reader = reader(csv_input)
            # Check that the header has the proper columns
            header = next(csv_reader)
            if header != ["id", "original_text", "timestamp"]:
                print("The CSV file header should be ['id', 'original_text', 'timestamp'].")
                failed_file_reading += 1
                continue
            date_dataframe = preprocess_csv_file(csv_reader, file_path, args.output_path, args.remove_url, args.remove_mentions, args.segment_hashtags, args.remove_punctuation, args.remove_numbers)
            if date_dataframe:
                date_dataframes.append(date_dataframe)
            else:
                failed_file_reading += 1

    if date_dataframes:
        final_dataframe = merge_counts_dataframe(date_dataframes)
        final_dataframe.to_csv('all_date_counts.csv')

    print("Failed to read %d because of improper format or headers." %
          failed_file_reading)


if __name__ == '__main__':
    main()
