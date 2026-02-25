import os
from pathlib import Path


global_read_only_marker_file = "GLOBAL_READ_ONLY_SET_DELETE_ME_TO_REVERSE"


def is_global_read_only(user_data_path: str):
    filename = global_read_only_marker_file_name(user_data_path)
    return Path(filename).is_file()


def set_global_read_only(user_data_path: str, global_read_only: bool):
    filename = global_read_only_marker_file_name(user_data_path)
    if global_read_only:
        try:
            Path(filename).touch()
        except:
            pass
    else:
        try:
            os.remove(filename)
        except:
            pass


def global_read_only_marker_file_name(user_data_path: str):
    return os.path.join(user_data_path, global_read_only_marker_file)
