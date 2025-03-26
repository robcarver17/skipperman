from app.data_access.csv.generic_csv_data import GenericCsvData

from app.data_access.classes.resources import *
from app.data_access.resolve_paths_and_filenames import (
    LIST_OF_PATROL_BOATS_FILE_ID,
    LIST_OF_CLUB_DINGHIES_FILE_ID,
    LIST_OF_PATROL_BOATS_AND_VOLUNTEERS_FILE_ID,
    LIST_OF_CLUB_DINGHIES_AND_CADETS_FILE_ID,
)
from app.objects.cadet_at_event_with_club_boat_with_ids import (
    ListOfCadetAtEventWithIdAndClubDinghies,
)
from app.objects.patrol_boats import ListOfPatrolBoats
from app.objects.patrol_boats_with_volunteers_with_id import (
    ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
)


class CsvDataListOfPatrolBoats(GenericCsvData, DataListOfPatrolBoats):
    def read(self) -> ListOfPatrolBoats:
        list_of_boats = self.read_and_return_object_of_type(
            ListOfPatrolBoats, file_identifier=LIST_OF_PATROL_BOATS_FILE_ID
        )

        return list_of_boats

    def write(self, list_of_boats: ListOfPatrolBoats):
        self.write_object(list_of_boats, file_identifier=LIST_OF_PATROL_BOATS_FILE_ID)


class CsvDataListOfClubDinghies(GenericCsvData, DataListOfClubDinghies):
    def read(self) -> ListOfClubDinghies:
        list_of_boats = self.read_and_return_object_of_type(
            ListOfClubDinghies, file_identifier=LIST_OF_CLUB_DINGHIES_FILE_ID
        )

        return list_of_boats

    def write(self, list_of_boats: ListOfClubDinghies):
        self.write_object(list_of_boats, file_identifier=LIST_OF_CLUB_DINGHIES_FILE_ID)


class CsvDataListOfVolunteersAtEventWithPatrolBoats(
    GenericCsvData, DataListOfVolunteersAtEventWithPatrolBoats
):
    def read(self, event_id: str) -> ListOfVolunteersWithIdAtEventWithPatrolBoatsId:
        people_and_boats = self.read_and_return_object_of_type(
            ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
            file_identifier=LIST_OF_PATROL_BOATS_AND_VOLUNTEERS_FILE_ID,
            additional_file_identifiers=event_id,
        )

        return people_and_boats

    def write(
        self,
        people_and_boats: ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
        event_id: str,
    ):
        self.write_object(
            people_and_boats,
            file_identifier=LIST_OF_PATROL_BOATS_AND_VOLUNTEERS_FILE_ID,
            additional_file_identifiers=event_id,
        )


class CsvDataListOfCadetAtEventWithClubDinghies(
    GenericCsvData, DataListOfCadetAtEventWithClubDinghies
):
    def read(self, event_id: str) -> ListOfCadetAtEventWithIdAndClubDinghies:
        people_and_boats = self.read_and_return_object_of_type(
            ListOfCadetAtEventWithIdAndClubDinghies,
            file_identifier=LIST_OF_CLUB_DINGHIES_AND_CADETS_FILE_ID,
            additional_file_identifiers=event_id,
        )

        return people_and_boats

    def write(
        self, people_and_boats: ListOfCadetAtEventWithIdAndClubDinghies, event_id: str
    ):
        self.write_object(
            people_and_boats,
            file_identifier=LIST_OF_CLUB_DINGHIES_AND_CADETS_FILE_ID,
            additional_file_identifiers=event_id,
        )
