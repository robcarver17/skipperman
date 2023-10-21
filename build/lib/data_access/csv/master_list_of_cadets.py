import pandas as pd
from app.data_access import GenericCsvData
from app.data_access import DataListOfCadets

from app.objects import ListOfCadets


class CsvDataListOfCadets(GenericCsvData, DataListOfCadets):
    def read(self) -> ListOfCadets:
        path_and_filename = self.path_and_filename
        try:
            df = pd.read_csv(path_and_filename)
        except:
            return ListOfCadets.create_empty()

        list_of_cadets = ListOfCadets.from_df_of_str(df)

        return list_of_cadets

    def write(self, list_of_cadets: ListOfCadets):
        df = list_of_cadets.to_df_of_str()
        path_and_filename = self.path_and_filename

        df.to_csv(path_and_filename, index=False)

    @property
    def path_and_filename(self):
        return self.get_path_and_filename_for_named_csv_file("cadet_master_list")
