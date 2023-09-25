from objects.constants import arg_not_passed

from data_access.csv.resolve_csv_paths_and_filenames import (
    get_path_and_filename_for_named_csv_file,
)


class GenericCsvData(object):
    def __init__(self, master_data_path: str):
        self._master_data_path = master_data_path

    def get_path_and_filename_for_named_csv_file(
        self, generic_name_of_file_required: str,
            additional_file_identifiers=arg_not_passed
    ) -> str:
        return get_path_and_filename_for_named_csv_file(
            generic_name_of_file_required=generic_name_of_file_required,
            master_data_path=self._master_data_path,
            additional_file_identifiers=additional_file_identifiers
        )
