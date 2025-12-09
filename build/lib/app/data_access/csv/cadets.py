from app.data_access.csv.generic_csv_data import GenericCsvData
from app.data_access.resolve_paths_and_filenames import (
    IDENTIFIED_CADETS_AT_EVENT_ID,
    CADETS_AT_EVENT_ID,
    CADETS_WITH_GROUPS_ID,
    LIST_OF_CADETS_FILE_ID,
    LIST_OF_CADETS_ON_COMMITTEE,
    ATTENDANCE_FILE_FOR_SPECIFIC_CADET,
    GROUP_NOTES_ID, GROUP_NAMES_ACROSS_EVENTS_FOR_CADETS_PERSISTENT_READ_ONLY,
)
from app.objects.attendance import ListOfRawAttendanceItemsForSpecificCadet

from app.objects.cadets import ListOfCadets
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups
from app.objects.cadet_with_id_at_event import ListOfCadetsWithIDAtEvent
from app.objects.group_notes_at_event import ListOfGroupNotesAtEventWithIds
from app.objects.identified_cadets_at_event import ListOfIdentifiedCadetsAtEvent
from app.objects.committee import ListOfCadetsWithIdOnCommittee
from app.objects.previous_cadet_groups import GroupNamesForEventsAndCadetPersistentVersionWithIds


class CsvDataListOfCadets(GenericCsvData):
    def read(self) -> ListOfCadets:
        list_of_cadets = self.read_and_return_object_of_type(
            ListOfCadets, file_identifier=LIST_OF_CADETS_FILE_ID
        )

        return list_of_cadets

    def write(self, list_of_cadets: ListOfCadets):
        self.write_object(list_of_cadets, file_identifier=LIST_OF_CADETS_FILE_ID)


class CsvDataListOfCadetsOnCommitte(GenericCsvData):
    def read(self) -> ListOfCadetsWithIdOnCommittee:
        list_of_cadets = self.read_and_return_object_of_type(
            ListOfCadetsWithIdOnCommittee, file_identifier=LIST_OF_CADETS_ON_COMMITTEE
        )

        return list_of_cadets

    def write(self, list_of_cadets: ListOfCadetsWithIdOnCommittee):
        self.write_object(list_of_cadets, file_identifier=LIST_OF_CADETS_ON_COMMITTEE)


class CsvDataListOfCadetsWithGroups(GenericCsvData):
    def read(self, event_id: str) -> ListOfCadetIdsWithGroups:
        list_of_cadets_with_groups = self.read_and_return_object_of_type(
            ListOfCadetIdsWithGroups,
            file_identifier=CADETS_WITH_GROUPS_ID,
            additional_file_identifiers=event_id,
        )

        return list_of_cadets_with_groups

    def write(
        self, list_of_cadets_with_groups: ListOfCadetIdsWithGroups, event_id: str
    ):
        self.write_object(
            list_of_cadets_with_groups,
            file_identifier=CADETS_WITH_GROUPS_ID,
            additional_file_identifiers=event_id,
        )


class CsvDataListOfGroupNotesAtEvent(GenericCsvData):
    def read(self) -> ListOfGroupNotesAtEventWithIds:
        return self.read_and_return_object_of_type(
            ListOfGroupNotesAtEventWithIds,
            file_identifier=GROUP_NOTES_ID,
        )

    def write(self, list_of_group_notes_with_ids: ListOfGroupNotesAtEventWithIds):
        self.write_object(list_of_group_notes_with_ids, file_identifier=GROUP_NOTES_ID)


class CsvDataListOfCadetsAtEvent(GenericCsvData):
    def read(self, event_id: str) -> ListOfCadetsWithIDAtEvent:
        list_of_cadets = self.read_and_return_object_of_type(
            ListOfCadetsWithIDAtEvent,
            file_identifier=CADETS_AT_EVENT_ID,
            additional_file_identifiers=event_id,
        )

        return list_of_cadets

    def write(self, list_of_cadets_at_event: ListOfCadetsWithIDAtEvent, event_id: str):
        self.write_object(
            list_of_cadets_at_event,
            file_identifier=CADETS_AT_EVENT_ID,
            additional_file_identifiers=event_id,
        )


class CsvDataListOfIdentifiedCadetsAtEvent(
    GenericCsvData
):
    def read(self, event_id: str) -> ListOfIdentifiedCadetsAtEvent:
        list_of_cadets = self.read_and_return_object_of_type(
            ListOfIdentifiedCadetsAtEvent,
            file_identifier=IDENTIFIED_CADETS_AT_EVENT_ID,
            additional_file_identifiers=event_id,
        )

        return list_of_cadets

    def write(
        self, list_of_cadets_at_event: ListOfIdentifiedCadetsAtEvent, event_id: str
    ):
        self.write_object(
            list_of_cadets_at_event,
            file_identifier=IDENTIFIED_CADETS_AT_EVENT_ID,
            additional_file_identifiers=event_id,
        )


class CsvDataAttendanceAtEventsForSpecificCadet(
    GenericCsvData
):
    def read(
        self, cadet_id: str
    ) -> ListOfRawAttendanceItemsForSpecificCadet:
        return self.read_and_return_object_of_type(
            ListOfRawAttendanceItemsForSpecificCadet,
            file_identifier=ATTENDANCE_FILE_FOR_SPECIFIC_CADET,
            additional_file_identifiers=cadet_id,
        )

    def write(
        self,
        list_of_attendance: ListOfRawAttendanceItemsForSpecificCadet,
        cadet_id: str,
    ):
        if len(list_of_attendance) == 0:
            filename = self.get_path_and_filename_for_named_csv_file(
                ATTENDANCE_FILE_FOR_SPECIFIC_CADET, additional_file_identifiers=cadet_id
            )
            self.delete(filename)
        else:
            self.write_object(
                list_of_attendance,
                file_identifier=ATTENDANCE_FILE_FOR_SPECIFIC_CADET,
                additional_file_identifiers=cadet_id,
            )



class CsvDataListOfGroupNamesForEventsAndCadetPersistentVersion( GenericCsvData):
    def read(self) ->  GroupNamesForEventsAndCadetPersistentVersionWithIds:
        return self.read_and_return_object_of_type(
            GroupNamesForEventsAndCadetPersistentVersionWithIds,
            file_identifier=GROUP_NAMES_ACROSS_EVENTS_FOR_CADETS_PERSISTENT_READ_ONLY,
        )

    def write(self, list_of_groups:  GroupNamesForEventsAndCadetPersistentVersionWithIds):
        self.write_object(list_of_groups, file_identifier=GROUP_NAMES_ACROSS_EVENTS_FOR_CADETS_PERSISTENT_READ_ONLY)
