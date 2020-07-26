from src.importTools import *
import argparse

if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description="A tool to transform twitter data into a CSV")
    # parser.add_argument()
    opts = TransformationOptions("en", True, 4096)
    file_list = scan_folder("../../data")
    print("Found the following files")
    print(file_list)
    line_count, failure_count = process_files(file_list, opts, "./output_test.csv")
    print("wrote ", file_list, " lines", " failures ", failure_count)


