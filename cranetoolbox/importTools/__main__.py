import argparse
import os

from cranetoolbox.fileHandler import scan_folder
from cranetoolbox.importTools import *


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="A tool to transform twitter data into a CSV format")
    parser.add_argument('--source-folder', metavar='s', type=str, required=True, default=None,
                        help='source folder to scan for input '
                             'files')
    parser.add_argument('-retweets', type=bool, default=False, help='this flag will include retweets in final output')
    parser.add_argument('--max-lines-in-memory', type=int, default=50000, help='the max number of lines from the source'
                                                                               'files that will be held in memory')
    parser.add_argument('--tweet-language', type=str, default='en', help='specifies the language of outputted tweets')
    parser.add_argument('--output-folder', type=str, default='./', help='specify the output directory for combined '
                                                                        'files')
    parser.add_argument('--output-name', type=str, default='filtered_data.csv',
                        help="Specify the output file name with extension")
    args = parser.parse_args()

    # Extract options
    opts = TransformationOptions(args.tweet_language, args.retweets, args.max_lines_in_memory)

    # Scan source folder for files
    file_list = scan_folder(args.source_folder)
    print("Found the following files")
    print(file_list)

    # Process the files and record stats
    line_count, failure_count = process_files(file_list, opts, os.path.join(args.output_folder, args.output_name))
    print("wrote ", line_count, " lines", " failures ", failure_count)


if __name__ == '__main__':
    main()
