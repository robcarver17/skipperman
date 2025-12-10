from app.data_access.csv.generic_csv_data import GenericCsvData

from app.data_access.csv.resolve_paths_and_filenames import (
    LIST_OF_PATROL_BOATS_FILE_ID,
    LIST_OF_CLUB_DINGHIES_FILE_ID,
    LIST_OF_PATROL_BOATS_AND_VOLUNTEERS_FILE_ID,
    LIST_OF_CLUB_DINGHIES_AND_CADETS_FILE_ID,
    PATROL_BOAT_LABELS,
    LIST_OF_CLUB_DINGHIES_AND_VOLUNTEERS_FILE_ID,
)
from app.objects.club_dinghies import ListOfClubDinghies, ListOfClubDinghyLimits
from app.objects.volunteers_and_cades_at_event_with_club_boat_with_ids import (
    ListOfCadetAtEventWithIdAndClubDinghies, ListOfVolunteerAtEventWithIdAndClubDinghies,
)
from app.objects.patrol_boats import ListOfPatrolBoats, ListOfPatrolBoatLabelsAtEvents
from app.objects.patrol_boats_with_volunteers_with_id import (
    ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
)


class CsvDataListOfPatrolBoats(GenericCsvData):
    def read(self) -> ListOfPatrolBoats:
        list_of_boats = self.read_and_return_object_of_type(
            ListOfPatrolBoats, file_identifier=LIST_OF_PATROL_BOATS_FILE_ID
        )

        return list_of_boats

    def write(self, list_of_boats: ListOfPatrolBoats):
        self.write_object(list_of_boats, file_identifier=LIST_OF_PATROL_BOATS_FILE_ID)


class CsvDataListOfClubDinghies(GenericCsvData):
    def read(self) -> ListOfClubDinghies:
        list_of_boats = self.read_and_return_object_of_type(
            ListOfClubDinghies, file_identifier=LIST_OF_CLUB_DINGHIES_FILE_ID
        )

        return list_of_boats

    def write(self, list_of_boats: ListOfClubDinghies):
        self.write_object(list_of_boats, file_identifier=LIST_OF_CLUB_DINGHIES_FILE_ID)


class CsvDataListOfVolunteersAtEventWithPatrolBoats(
    GenericCsvData
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
    GenericCsvData
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


class CsvDataListOfVolunteersAtEventWithClubDinghies(
    GenericCsvData
):
    def read(self, event_id: str) -> ListOfVolunteerAtEventWithIdAndClubDinghies:
        return self.read_and_return_object_of_type(
            ListOfVolunteerAtEventWithIdAndClubDinghies,
            file_identifier=LIST_OF_CLUB_DINGHIES_AND_VOLUNTEERS_FILE_ID,
            additional_file_identifiers=event_id,
        )

    def write(
        self,
        list_of_volunteers_at_event_with_club_dinghies: ListOfVolunteerAtEventWithIdAndClubDinghies,
        event_id: str,
    ):
        self.write_object(
            list_of_volunteers_at_event_with_club_dinghies,
            file_identifier=LIST_OF_CLUB_DINGHIES_AND_VOLUNTEERS_FILE_ID,
            additional_file_identifiers=event_id,
        )


from app.data_access.csv.resolve_paths_and_filenames import CLUB_BOAT_LIMIT_CSV


class CsvDataListOfClubDinghyLimits(GenericCsvData):
    def read(self) -> ListOfClubDinghyLimits:
        list_of_boats = self.read_and_return_object_of_type(
            ListOfClubDinghyLimits, file_identifier=CLUB_BOAT_LIMIT_CSV
        )

        return list_of_boats

    def write(self, list_of_boats: ListOfClubDinghyLimits):
        self.write_object(list_of_boats, file_identifier=CLUB_BOAT_LIMIT_CSV)


class CsvDataListOfPatrolBoatLabelsAtEvent(
    GenericCsvData
):
    def read(self) -> ListOfPatrolBoatLabelsAtEvents:
        return self.read_and_return_object_of_type(
            ListOfPatrolBoatLabelsAtEvents, file_identifier=PATROL_BOAT_LABELS
        )

    def write(self, list_of_patrol_boat_labels: ListOfPatrolBoatLabelsAtEvents):
        self.write_object(
            list_of_patrol_boat_labels, file_identifier=PATROL_BOAT_LABELS
        )
