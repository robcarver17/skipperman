from app.objects.utilities.exceptions import arg_not_passed
import pandas as pd
from app.data_access.csv.resolve_paths_and_filenames import (
    get_path_and_filename_for_named_file,
    get_path_for_generic_name,
)
import os
from app.data_access.file_access import files_with_extension_in_resolved_pathname
from typing import List


class GenericCsvData(object):
    def __init__(self, master_data_path: str, backup_data_path: str):
        self._master_data_path = master_data_path
        self._backup_data_path = backup_data_path

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
        return get_path_and_filename_for_named_file(
            generic_name_of_file_required=generic_name_of_file_required,
            master_data_path=self._master_data_path,
            additional_file_identifiers=additional_file_identifiers,
        )

    def get_path_for_generic_file_name(self, generic_name_of_file_required: str) -> str:
        return get_path_for_generic_name(
            generic_name_of_file_required=generic_name_of_file_required,
            master_data_path=self._master_data_path,
        )

    def read_and_return_object_of_type(
        self,
        object_type,
        file_identifier: str,
        additional_file_identifiers=arg_not_passed,
    ):
        path_and_filename = self.get_path_and_filename_for_named_csv_file(
            file_identifier, additional_file_identifiers=additional_file_identifiers
        )
        object = read_object_of_type(object_type, path_and_filename)
        return object

    def write_object(
        self, object, file_identifier: str, additional_file_identifiers=arg_not_passed
    ):
        path_and_filename = self.get_path_and_filename_for_named_csv_file(
            file_identifier, additional_file_identifiers=additional_file_identifiers
        )
        write_object_as_csv_file(object, path_and_filename)

    def get_list_of_csv_files_in_path_for_field_id(
        self, file_identifier: str
    ) -> List[str]:
        path = self.path_for_field_id(file_identifier)
        return files_with_extension_in_resolved_pathname(path, extension=".csv")

    def path_for_field_id(self, file_identifier: str):
        return self.get_path_for_generic_file_name(file_identifier)


def write_object_as_csv_file(object, path_and_filename: str):
    df = object.as_df_of_str()
    df.to_csv(path_and_filename, index=False)


def read_object_of_type(object_type, path_and_filename):
    try:
        df = pd.read_csv(path_and_filename)
        assert len(df) > 0
    except:
        return object_type.create_empty()

    object = object_type.from_df_of_str(df)

    return object
