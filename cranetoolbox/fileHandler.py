import os
import typing
from os import path
from pathlib import PurePath, Path


def scan_folder(search_path: str) -> [str]:
    """List all files in the file-system tree down from the search path.

    :param search_path: The path that represents the file or folder where the search should be conducted
    :type search_path: str
    :return: An array of strings, each representing a single file
    :rtype: list(str)
    """

    if not path.exists(search_path):
        # Not a path, return empty array to indicate that no files where found
        return []
    if path.isfile(search_path):
        # Single file, return single array
        return [search_path]

    file_list = []
    # Build list of files in folder and its sub-folders
    for root, _, files in os.walk(search_path):
        for file in files:
            file_list.append(PurePath(search_path, file))
    return file_list


def scan_folder_csv(search_path: str) -> typing.List[str]:
    """Scans a given path and extracts all files that end with .csv
    
    :param search_path: Any path on the machine
    :type search_path: str
    :return: List of CSV files
    :rtype: list(PurePath)
    """

    all_files = scan_folder(search_path)
    output_file_list = []
    for curr_path in all_files:
        if Path(curr_path).suffix == '.csv':
            output_file_list.append(curr_path)
    return output_file_list
