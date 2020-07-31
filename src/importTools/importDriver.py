from src.importTools import *
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A tool to transform twitter data into a CSV or pickle format")
    parser.add_argument('--source-folder', metavar='s', type=str, required=True, default=None,
                        help='source folder to scan for input '
                             'files')
    parser.add_argument('-retweets', type=bool, default=False, help='this flag will include retweets in final output')
    parser.add_argument('--max-in-memory', type=int, default=4096, help='the max file size that will be held in '
                                                                        'memory, otherwise processes by chunks to '
                                                                        'avoid memory issues')
    parser.add_argument('--tweet-language', type=str, default='en', help='specifies the language of outputted tweets')
    parser.add_argument('--pkl-output-name', type=str, default='combined_output.pkl', help='specify output name of '
                                                                                           'the pickle file, '
                                                                                           'required that the '
                                                                                           'corresponding output '
                                                                                           'format is specified too')
    parser.add_argument('--csv-output-name', type=str, default='combined_output.csv', help='specify output name of '
                                                                                           'the csv file, '
                                                                                           'required that the '
                                                                                           'corresponding output '
                                                                                           'format is specified too')
    parser.add_argument('--output_folder', type=str, default='./', help='specify the output directory for combined '
                                                                        'files')
    output_group = parser.add_mutually_exclusive_group(required=True)

    output_group.add_argument('-pkl-output', action='store_true', help='use this flag to create a '
                                                                       'pickle file as the processed '
                                                                       'output')
    output_group.add_argument('-csv-output', action='store_true', help='use this flag to create a '
                                                                       'csv file as the processed '
                                                                       'output')
    output_group.add_argument('-pkl-csv-output', action='store_true', help='use this flag to '
                                                                           'generate both a '
                                                                           'pickle and csv '
                                                                           'output file')
    args = parser.parse_args()
    # Select output format
    output_format = None
    if args.pkl_output:
        output_format = OutputFormat.PKL
    if args.csv_output:
        output_format = OutputFormat.CSV
    if args.pkl_csv_output:
        output_format = OutputFormat.BOTH
    opts = TransformationOptions(args.tweet_language, args.retweets, args.max_in_memory, output_format)
    file_list = scan_folder(args.source_folder)
    print("Found the following files")
    print(file_list)
    line_count, failure_count = process_files(file_list, opts, path.join(args.output_folder, args.csv_output_name),
                                              path.join(args.output_folder, args.pkl_output_name))
    print("wrote ", file_list, " lines", " failures ", failure_count)
