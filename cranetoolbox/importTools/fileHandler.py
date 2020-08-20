import os
import typing
from os import path
from pathlib import PurePath


def scan_folder(search_path: str) -> [str]:
    """List all files in the file-system tree down from the search path.

    :param search_path: The path that represents the file or folder where the search
    should be conducted
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
