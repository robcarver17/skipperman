import pandas as pd
from app.data_access.csv.generic_csv_data import GenericCsvData
from app.data_access.classes.cadets import DataListOfCadets

from app.objects.cadets import ListOfCadets

LIST_OF_CADETS_FILE_ID = "cadet_master_list"

class CsvDataListOfCadets(GenericCsvData, DataListOfCadets):
    def read(self) -> ListOfCadets:
        list_of_cadets = self.read_and_return_object_of_type(ListOfCadets, file_identifier=LIST_OF_CADETS_FILE_ID)

        return list_of_cadets

    def write(self, list_of_cadets: ListOfCadets):
        self.write_object(list_of_cadets, file_identifier=LIST_OF_CADETS_FILE_ID)


