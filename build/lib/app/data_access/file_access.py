import os
from importlib import import_module
from typing import List


def get_files_in_directory(mypath: str):
    onlyfiles = [
        f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))
    ]
    return onlyfiles


def get_relative_pathname_from_list(path_as_list: List[str]) -> str:
    package_name = path_as_list[0]
    paths_or_files = path_as_list[1:]

    if len(paths_or_files) == 0:
        directory_name_of_package = os.path.dirname(
            import_module(package_name).__file__
        )
        return directory_name_of_package

    last_item_in_list = path_as_list.pop()
    pathname = os.path.join(
        get_relative_pathname_from_list(path_as_list), last_item_in_list
    )

    return pathname
