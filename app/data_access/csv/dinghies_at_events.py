from app.data_access.csv.generic_csv_data import GenericCsvData

from app.data_access.resolve_paths_and_filenames import (
    LIST_OF_DINGHIES_FILE_ID,
    LIST_OF_CADETS_WITH_DINGHIES_AT_EVENT_FILE_ID,
)
from app.objects.boat_classes import ListOfBoatClasses
from app.objects.cadet_at_event_with_boat_class_and_partners_with_ids import (
    ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
)


class CsvDataListOfDinghies(GenericCsvData):


    def read(self) -> ListOfBoatClasses:
        list_of_boats = self.read_and_return_object_of_type(
            ListOfBoatClasses, file_identifier=LIST_OF_DINGHIES_FILE_ID
        )

        return list_of_boats

    def write(self, list_of_boats: ListOfBoatClasses):
        self.write_object(list_of_boats, file_identifier=LIST_OF_DINGHIES_FILE_ID)


class CsvDataListOfCadetAtEventWithDinghies(
    GenericCsvData
):
    def read(self, event_id: str) -> ListOfCadetAtEventWithBoatClassAndPartnerWithIds:
        people_and_boats = self.read_and_return_object_of_type(
            ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
            file_identifier=LIST_OF_CADETS_WITH_DINGHIES_AT_EVENT_FILE_ID,
            additional_file_identifiers=event_id,
        )

        return people_and_boats

    def write(
        self,
        people_and_boats: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
        event_id: str,
    ):
        self.write_object(
            people_and_boats,
            file_identifier=LIST_OF_CADETS_WITH_DINGHIES_AT_EVENT_FILE_ID,
            additional_file_identifiers=event_id,
        )
