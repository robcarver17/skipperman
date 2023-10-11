import os
from pathlib import Path
from interface.cli.input import (
    print_menu_and_get_desired_option,
)


def interactive_file_selector(
    message_to_display: str, starting_directory_for_up_download: str
) -> str:
    print(message_to_display)
    input("Press return to start file selection")
    selected_file = recursive_file_selector(starting_directory_for_up_download)

    return selected_file


GO_UP_DIR = "<Parent directory>"


def recursive_file_selector(current_directory: str) -> str:
    try:
        list_of_files_and_directorys = os.listdir(current_directory)
    except NotADirectoryError:
        ## A file, return it
        return current_directory

    list_of_files_and_directorys.sort()

    list_of_files_and_directorys.insert(0, GO_UP_DIR)
    print("Files and directories in %s" % current_directory)
    selected_file_or_dir = print_menu_and_get_desired_option(
        list_of_files_and_directorys
    )

    if selected_file_or_dir == GO_UP_DIR:
        new_file_or_dir = Path(current_directory).parent.absolute()
    else:
        new_file_or_dir = os.path.join(current_directory, selected_file_or_dir)

    selected_file_or_dir = recursive_file_selector(new_file_or_dir)

    return selected_file_or_dir
