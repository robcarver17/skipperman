import glob
import os
from copy import copy
from dataclasses import dataclass
from datetime import datetime
from typing import List

import qrcode

from app.data_access.configuration.configuration import HOMEPAGE, PUBLIC_REPORTING_SUBDIRECTORY
from app.data_access.init_directories import upload_directory, download_directory
from app.objects.abstract_objects.abstract_form import File
from app.objects.utilities.exceptions import MissingData, arg_not_passed


def get_files_in_directory_mask_suffix_and_extension_from_filename_remove_duplicates(
    mypath: str,
):
    onlyfiles = get_files_in_directory(mypath)
    masked_files = [
        mask_suffix_and_extension_from_filename(filename) for filename in onlyfiles
    ]
    no_duplicated_files = list(set(masked_files))

    return no_duplicated_files


def get_files_in_directory(mypath: str):
    onlyfiles = [
        f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))
    ]
    return onlyfiles


def mask_suffix_and_extension_from_filename(filename: str):
    filename_without_extension = get_filename_and_extension(filename)[0]
    filename_without_extension_and_suffix = filename_without_extension[:-12]

    return filename_without_extension_and_suffix


def get_filename_and_extension(filename: str):
    filename_and_extension = filename.split(".")
    filename_without_extension = filename.split(".")[0]
    if len(filename_and_extension) == 1:
        return filename_without_extension, ""
    extension = filename.split(".")[-1]

    return filename_without_extension, extension


def files_with_extension_in_resolved_pathname(
    resolved_pathname: str, extension=".csv"
) -> List[str]:
    """
    Find all the files with a particular extension in a directory
    """

    file_list = os.listdir(resolved_pathname)
    file_list = [filename for filename in file_list if filename.endswith(extension)]
    file_list_no_extension = [filename.split(".")[0] for filename in file_list]

    return file_list_no_extension


@dataclass
class PathAndFilename:
    filename_without_extension: str
    path: str = ""
    extension: str = ""

    @classmethod
    def from_filename_without_path(cls, filename_without_path: str):
        filename, extension = filename_without_path.split(".")
        return cls(filename_without_extension=filename, extension=extension
                   )

    @property
    def full_path_and_name(self):
        filename = self.filename
        path_and_filename = os.path.join(self.path, filename)

        return path_and_filename

    @property
    def filename(self):
        return self.filename_without_extension + "." + self.extension

    def replace_path(self, path: str):
        self.path = path

    def add_or_replace_extension(self, extension: str):
        self.extension = extension

    def add_suffix_to_end_of_filename(self, suffix: str):
        self.filename_without_extension = self.filename_without_extension + suffix


def web_pathname_of_public_version_of_local_file_without_extension(
    path_and_filename: PathAndFilename, public_path: str, webserver_url: str
):
    filename_with_extension = path_and_filename.filename_without_extension
    return "%s/%s/%s" % (webserver_url, public_path, filename_with_extension)


def get_public_filename_given_local_file(
    local_path_and_filename: PathAndFilename, public_path: str
) -> PathAndFilename:
    output_path_and_filename = copy(local_path_and_filename)
    output_path_and_filename.replace_path(public_path)

    return output_path_and_filename


def add_suffix_to_public_filename(output_path_and_filename: PathAndFilename):
    suffix = datetime.now().strftime("%y%m%d%H%M%S")
    output_path_and_filename.add_suffix_to_end_of_filename(suffix)


def get_newest_file_matching_filename(filename: str, pathname: str):
    all_files = get_all_files_matching_filename(filename=filename, pathname=pathname)
    if len(all_files) == 0:
        raise MissingData

    latest_file = max(all_files, key=os.path.getctime)

    return latest_file


def get_all_files_matching_filename(filename: str, pathname: str):
    matching = "%s/%s*" % (pathname, filename)
    print(matching)
    return glob.glob(matching)


def delete_all_files_matching_filename(filename: str, pathname: str):
    list_of_files = get_all_files_matching_filename(
        filename=filename, pathname=pathname
    )
    for filename in list_of_files:
        os.remove(filename)


def get_staged_adhoc_filename(adhoc_name: str):
    return os.path.join(upload_directory, "_%s" % adhoc_name)


def generate_qr_code_for_file_in_public_path(filename_without_extension: str) -> File:
    path_and_filename = PathAndFilename(
        path="", extension="", filename_without_extension=filename_without_extension
    )
    web_path = web_pathname_of_public_version_of_local_file_without_extension(
        path_and_filename,
        webserver_url=HOMEPAGE,
        public_path=PUBLIC_REPORTING_SUBDIRECTORY,
    )
    return generate_qr_code_for_file_with_web_path(
        web_path=web_path, filename_without_extension=filename_without_extension
    )


def generate_qr_code_for_file_with_web_path(
    web_path: str, filename_without_extension: str = arg_not_passed
) -> File:
    if filename_without_extension is arg_not_passed:
        filename_without_extension = web_path

    img = qrcode.make(web_path)
    qr_code_filename = temp_qr_code_file_name(filename_without_extension)
    with open(qr_code_filename, "wb") as qr:
        img.save(qr)

    return File(qr_code_filename)


def temp_qr_code_file_name(filename: str) -> str:
    return os.path.join(download_directory, "temp_qr_code_%s.png" % filename)
