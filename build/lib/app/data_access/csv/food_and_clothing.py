from app.data_access.csv.generic_csv_data import GenericCsvData

from app.data_access.classes.food_and_clothing import *
from app.data_access.csv.resolve_csv_paths_and_filenames import (
    LIST_OF_CADETS_WITH_CLOTHING_AT_EVENT,
    LIST_OF_CADETS_WITH_FOOD_AT_EVENT,
    LIST_OF_VOLUNTEERS_WITH_FOOD_AT_EVENT,
)


class CsvDataListOfCadetsWithClothingAtEvent(
    GenericCsvData, DataListOfCadetsWithClothingAtEvent
):
    def read(self, event_id: str) -> ListOfCadetsWithClothingAtEvent:
        return self.read_and_return_object_of_type(
            ListOfCadetsWithClothingAtEvent,
            file_identifier=LIST_OF_CADETS_WITH_CLOTHING_AT_EVENT,
            additional_file_identifiers=event_id,
        )

    def write(
        self,
        list_of_cadets_with_clothing: ListOfCadetsWithClothingAtEvent,
        event_id: str,
    ):
        self.write_object(
            list_of_cadets_with_clothing,
            file_identifier=LIST_OF_CADETS_WITH_CLOTHING_AT_EVENT,
            additional_file_identifiers=event_id,
        )


class CsvDataListOfCadetsWithFoodRequirementsAtEvent(
    GenericCsvData, DataListOfCadetsWithFoodRequirementsAtEvent
):
    def read(self, event_id: str) -> ListOfCadetsWithFoodRequirementsAtEvent:
        return self.read_and_return_object_of_type(
            ListOfCadetsWithFoodRequirementsAtEvent,
            file_identifier=LIST_OF_CADETS_WITH_FOOD_AT_EVENT,
            additional_file_identifiers=event_id,
        )

    def write(
        self,
        list_of_cadets_with_food: ListOfCadetsWithFoodRequirementsAtEvent,
        event_id: str,
    ):
        self.write_object(
            list_of_cadets_with_food,
            file_identifier=LIST_OF_CADETS_WITH_FOOD_AT_EVENT,
            additional_file_identifiers=event_id,
        )


class CsvDataListOfVolunteersWithFoodRequirementsAtEvent(
    GenericCsvData, DataListOfVolunteersWithFoodRequirementsAtEvent
):
    def read(self, event_id: str) -> ListOfVolunteersWithFoodRequirementsAtEvent:
        return self.read_and_return_object_of_type(
            ListOfVolunteersWithFoodRequirementsAtEvent,
            file_identifier=LIST_OF_VOLUNTEERS_WITH_FOOD_AT_EVENT,
            additional_file_identifiers=event_id,
        )

    def write(
        self,
        list_of_volunteers_with_food: ListOfVolunteersWithFoodRequirementsAtEvent,
        event_id: str,
    ):
        self.write_object(
            list_of_volunteers_with_food,
            file_identifier=LIST_OF_VOLUNTEERS_WITH_FOOD_AT_EVENT,
            additional_file_identifiers=event_id,
        )
