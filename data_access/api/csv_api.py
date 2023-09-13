from data_access.api.generic_api import GenericDataApi
from data_access.csv.master_list_of_cadets import CsvDataListOfCadets


class CsvDataApi(GenericDataApi):
    def __init__(self, master_data_path: str):
        self._master_data_path = master_data_path

    @property
    def data_list_of_cadets(self):
        return CsvDataListOfCadets(master_data_path=self.master_data_path)

    @property
    def master_data_path(self) -> str:
        return self._master_data_path
