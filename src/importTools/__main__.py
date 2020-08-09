from src.importTools import *
import argparse

def main():
    parser = argparse.ArgumentParser(description="A tool to transform twitter data into a CSV or pickle format")
    parser.add_argument('--source-folder', metavar='s', type=str, required=True, default=None,
                        help='source folder to scan for input '
                             'files')
    parser.add_argument('-retweets', type=bool, default=False, help='this flag will include retweets in final output')
    parser.add_argument('--max-file-size-memory', type=int, default=4096, help='the max file size that will be held in '
                                                                               'memory, otherwise processes by chunks to '
                                                                               'avoid memory issues')
    parser.add_argument('--tweet-language', type=str, default='en', help='specifies the language of outputted tweets')
    parser.add_argument('--output_folder', type=str, default='./', help='specify the output directory for combined '
                                                                        'files')
    parser.add_argument('--output-name', type=str, default='filtered_data.csv',
                        help="Specify the output file name with extension")
    args = parser.parse_args()
    opts = TransformationOptions(args.tweet_language, args.retweets, args.max_file_size_memory)
    file_list = scan_folder(args.source_folder)
    print("Found the following files")
    print(file_list)
    line_count, failure_count = process_files(file_list, opts, path.join(args.output_folder, args.output_name))
    print("wrote ", file_list, " lines", " failures ", failure_count)


if __name__ == '__main__':
    main()
