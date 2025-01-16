import os
from importlib import import_module
from typing import List

from app.data_access.configuration.configuration import (
    DOWNLOAD_DIRECTORY,
    PUBLIC_REPORTING_SUBDIRECTORY,
    UPLOADS,
    PUBLIC_WEB_PATH,
)


def get_files_in_directory(mypath: str):
    onlyfiles = [
        f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))
    ]
    return onlyfiles


home_directory = os.path.expanduser("~")

public_reporting_directory = os.path.join(home_directory, PUBLIC_REPORTING_SUBDIRECTORY)
upload_directory = os.path.join(home_directory, UPLOADS)
download_directory = os.path.join(home_directory, DOWNLOAD_DIRECTORY)

skipperman_directory = os.path.join(home_directory, "skipperman")
docs_directory = os.path.join(skipperman_directory, "docs")

try:
    os.mkdir(public_reporting_directory)
except:
    pass


try:
    os.mkdir(upload_directory)
except:
    pass

try:
    os.mkdir(download_directory)
except:
    pass


def web_pathname_of_file(filename_with_extension: str):
    return PUBLIC_WEB_PATH + filename_with_extension


def temp_file_name() -> str:
    return os.path.join(download_directory, "temp_file.csv")


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
