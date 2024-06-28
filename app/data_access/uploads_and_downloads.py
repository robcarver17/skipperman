from app.data_access.file_access import get_files_in_directory, upload_directory
import os


def get_next_valid_upload_file_name(file_marker: str):
    suffix_id = get_last_id_of_file_uploaded(file_marker)
    suffix_id += 1

    filename = file_marker + "%d" % suffix_id
    full_filename = os.path.join(upload_directory, filename)

    return full_filename


def get_last_id_of_file_uploaded(file_marker: str) -> int:
    files_in_directory = get_files_in_upload_directory()
    matching_files = [
        filename for filename in files_in_directory if file_marker in filename
    ]
    if len(matching_files) == 0:
        return 0
    prefix_length = len(file_marker)
    suffixes_as_str = [filename[prefix_length:] for filename in matching_files]
    suffixes_as_int = [int(suffix) for suffix in suffixes_as_str]

    return max(suffixes_as_int)


def get_files_in_upload_directory():
    return get_files_in_directory(upload_directory)
