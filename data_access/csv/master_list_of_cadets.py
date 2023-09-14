import pandas as pd
from data_access.csv.generic_csv_data import GenericCsvData
from data_access.classes.master_list_of_cadets import DataListOfCadets

from objects.cadets import ListOfCadets


class CsvDataListOfCadets(GenericCsvData, DataListOfCadets):
    def read(self) -> ListOfCadets:
        path_and_filename = self.path_and_filename
        df = pd.read_csv(path_and_filename)
        list_of_cadets = ListOfCadets.from_df_of_str(df)

        return list_of_cadets

    def write(self, list_of_cadets: ListOfCadets):
        df = list_of_cadets.to_df_of_str()
        path_and_filename = self.path_and_filename

        df.to_csv(path_and_filename, index=False)

    @property
    def path_and_filename(self):
        return self.get_path_and_filename_for_named_csv_file("cadet_master_list")
