from app.data_access.csv.generic_csv_data import GenericCsvData

from app.data_access.classes.qualifications import *
from app.objects.qualifications import ListOfQualifications, ListOfCadetsWithQualifications
from app.data_access.csv.resolve_csv_paths_and_filenames import LIST_OF_QUALIFICATIONS, LIST_OF_CADETS_WITH_QUALIFICATIONS, LIST_OF_TICK_SHEET_ITEMS, LIST_OF_TICK_SUBSTAGES, LIST_OF_CADETS_WITH_TICK_LIST_ITEMS

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



class CsvDataListOfTickSubStages(GenericCsvData, DataListOfTickSubStages):

    def read(self) -> ListOfTickSubStages:
        list_of_tick_substages = self.read_and_return_object_of_type(ListOfTickSubStages, file_identifier=LIST_OF_TICK_SUBSTAGES)

        return list_of_tick_substages

    def write(self, list_of_tick_substages: ListOfTickSubStages):
        self.write_object(list_of_tick_substages, file_identifier=LIST_OF_TICK_SUBSTAGES)



class CsvDataListOfTickSheetItems(GenericCsvData, DataListOfTickSheetItems):

    def read(self) -> ListOfTickSheetItems:
        list_of_tick_sheet_items = self.read_and_return_object_of_type(ListOfTickSheetItems, file_identifier=LIST_OF_TICK_SHEET_ITEMS)

        return list_of_tick_sheet_items

    def write(self, list_of_tick_sheet_items: ListOfTickSheetItems):
        self.write_object(list_of_tick_sheet_items, file_identifier=LIST_OF_TICK_SHEET_ITEMS)



class CsvDataListOfCadetsWithTickListItems(GenericCsvData, DataListOfCadetsWithTickListItems):

    def read(self) -> ListOfCadetsWithTickListItems:
        list_of_cadets_with_tick_list_items = self.read_and_return_object_of_type(ListOfCadetsWithTickListItems, file_identifier=LIST_OF_CADETS_WITH_TICK_LIST_ITEMS)

        return list_of_cadets_with_tick_list_items

    def write(self, list_of_cadets_with_tick_list_items: ListOfCadetsWithTickListItems):
        self.write_object(list_of_cadets_with_tick_list_items, file_identifier=LIST_OF_CADETS_WITH_TICK_LIST_ITEMS)

