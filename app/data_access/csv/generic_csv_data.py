from app.objects.constants import arg_not_passed

from app.data_access.csv.resolve_csv_paths_and_filenames import (
    get_path_and_filename_for_named_csv_file,
    get_path_for_generic_name,
)
import os


class GenericCsvData(object):
    def __init__(self, master_data_path: str):
        self._master_data_path = master_data_path

    def delete(self, filename):
        try:
            os.remove(filename)
        except:
            pass

    def get_path_and_filename_for_named_csv_file(
        self,
        generic_name_of_file_required: str,
        additional_file_identifiers=arg_not_passed,
    ) -> str:
        return get_path_and_filename_for_named_csv_file(
            generic_name_of_file_required=generic_name_of_file_required,
            master_data_path=self._master_data_path,
            additional_file_identifiers=additional_file_identifiers,
        )

    def get_path_for_generic_file_name(self, generic_name_of_file_required: str) -> str:
        return get_path_for_generic_name(
            generic_name_of_file_required=generic_name_of_file_required,
            master_data_path=self._master_data_path,
        )
