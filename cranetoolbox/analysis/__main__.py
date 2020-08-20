from cranetoolbox.analysis.countOccurences import *
import argparse
from os import makedirs
from os.path import isfile, dirname


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Quantitative analysis. Daily frequency of each given keyword in the dataset.")
    # Positional mandatory arguments
    parser.add_argument(
        "input_path", help="Path to the folder containing the dataset preprocessed with the *preprocess* module, or a single file.")
    parser.add_argument(
        "keywords_path", help="Path to the JSON file containing the keywords and their variants. See main documentation for expected format.")
    parser.add_argument(
        "output_path", help="Path for the result file.")
    # Optional arguments
    parser.add_argument("-d",
                        "--date_format", help="String defining the format of dates in the dataset.", default="%a %b %d %H:%M:%S %z %Y")
    # Parse arguments
    args = parser.parse_args()


    # Load the dictionary of keywords
    keywords = get_keywords(args.keywords_path)

    # Check whether the input_path correspond to a single file or a directory
    if isfile(args.input_path):
        # Single file
        input_paths = [args.input_path]
    else:
        # Get the list of files from the directory
        input_paths = list_files(args.input_path)
        # If the directory did not contain any file with the right extension
        if len(input_paths) == 0:
            print("No appropriate file could be found in the provided directory.")
            print("Please remember that the search is not recursive.")
            return

    # Count the keywords' occurences
    keyword_counts = count_keywords(input_paths, keywords, args.date_format)

    # Compute daily frequencies
    keyword_counts_and_freqs = counts_to_freq(keyword_counts, tweet_counts, keywords)

    # Create output folder if it does not exists
    makedirs(dirname(args.output_path), exist_ok=True)
    # Save to file
    keyword_counts_and_freqs.to_csv(args.output_path, index=True)


if __name__ == '__main__':
    main()
