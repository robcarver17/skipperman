import pandas as pd
from data_access.csv.generic_csv_data import GenericCsvData
from data_access.csv.utils import (
    transform_df_column_from_str_to_dates,
    transform_df_column_from_dates_to_str,
)
from data_access.classes.master_list_of_cadets import DataListOfCadets, ListOfCadets

from objects.cadets import ListOfCadets, CADET_DOB_FIELD


class CsvDataListOfCadets(GenericCsvData, DataListOfCadets):
    def read(self) -> ListOfCadets:
        path_and_filename = self.path_and_filename
        raw_df = pd.read_csv(path_and_filename)
        raw_df_with_dob_set_to_date = transform_df_column_from_str_to_dates(
            raw_df, CADET_DOB_FIELD
        )
        list_of_cadets = ListOfCadets.from_df(raw_df_with_dob_set_to_date)

        return list_of_cadets

    def write(self, list_of_cadets: ListOfCadets):
        df = list_of_cadets.to_df()
        df_with_dob_set_to_str = transform_df_column_from_dates_to_str(
            df, CADET_DOB_FIELD
        )
        path_and_filename = self.path_and_filename

        df_with_dob_set_to_str.to_csv(path_and_filename, index=False)

    @property
    def path_and_filename(self):
        return self.get_path_and_filename_for_named_csv_file("cadet_master_list")
