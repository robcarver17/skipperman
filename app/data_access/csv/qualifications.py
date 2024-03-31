from app.data_access.csv.generic_csv_data import GenericCsvData

from app.data_access.classes.qualifications import DataListOfQualifications, DataListOfCadetsWithQualifications
from app.objects.qualifications import ListOfQualifications, ListOfCadetsWithQualifications
from app.data_access.csv.resolve_csv_paths_and_filenames import LIST_OF_QUALIFICATIONS, LIST_OF_CADETS_WITH_QUALIFICATIONS

class CsvDataListOfQualifications(GenericCsvData, DataListOfQualifications):

    def read(self) -> ListOfQualifications:
        list_of_qualifications = self.read_and_return_object_of_type(ListOfQualifications, file_identifier=LIST_OF_QUALIFICATIONS)

        return list_of_qualifications

    def write(self, list_of_qualifications: ListOfQualifications):
        self.write_object(list_of_qualifications, file_identifier=LIST_OF_QUALIFICATIONS)


class CsvListOfCadetsWithQualifications(GenericCsvData, DataListOfCadetsWithQualifications):

    def read(self) -> ListOfCadetsWithQualifications:
        list_of_cadets_with_qualifications = self.read_and_return_object_of_type(ListOfCadetsWithQualifications,
                                                                                 file_identifier=LIST_OF_CADETS_WITH_QUALIFICATIONS)

        return list_of_cadets_with_qualifications

    def write(self, list_of_cadets_with_qualifications: ListOfCadetsWithQualifications):
        self.write_object(list_of_cadets_with_qualifications, file_identifier=LIST_OF_CADETS_WITH_QUALIFICATIONS)
