from app.data_access.csv.generic_csv_data import GenericCsvData
from app.data_access.classes.cadets import DataListOfCadets, DataListOfCadetsWithGroups, DataListOfCadetsAtEvent, DataListOfIdentifiedCadetsAtEvent, DataListOfCadetsOnCommitte
from app.data_access.csv.resolve_csv_paths_and_filenames import IDENTIFIED_CADETS_AT_EVENT_ID, CADETS_AT_EVENT_ID, \
    CADETS_WITH_GROUPS_ID, LIST_OF_CADETS_FILE_ID, LIST_OF_CADETS_ON_COMMITTEE

from app.objects.cadets import ListOfCadets
from app.objects.groups import ListOfCadetIdsWithGroups
from app.objects.cadet_at_event import ListOfCadetsAtEvent, ListOfIdentifiedCadetsAtEvent
from app.objects.committee import ListOfCadetsOnCommittee

class CsvDataListOfCadets(GenericCsvData, DataListOfCadets):
    def read(self) -> ListOfCadets:
        list_of_cadets = self.read_and_return_object_of_type(ListOfCadets, file_identifier=LIST_OF_CADETS_FILE_ID)

        return list_of_cadets

    def write(self, list_of_cadets: ListOfCadets):
        self.write_object(list_of_cadets, file_identifier=LIST_OF_CADETS_FILE_ID)


class CsvDataListOfCadetsOnCommitte(GenericCsvData, DataListOfCadetsOnCommitte):
    def read(self) -> ListOfCadetsOnCommittee:
        list_of_cadets = self.read_and_return_object_of_type(ListOfCadetsOnCommittee, file_identifier=LIST_OF_CADETS_ON_COMMITTEE)

        return list_of_cadets

    def write(self, list_of_cadets: ListOfCadetsOnCommittee):
        self.write_object(list_of_cadets, file_identifier=LIST_OF_CADETS_ON_COMMITTEE)



class CsvDataListOfCadetsWithGroups(GenericCsvData, DataListOfCadetsWithGroups):

    def read_groups_for_event(self, event_id: str) -> ListOfCadetIdsWithGroups:
        list_of_cadets_with_groups = self.read_and_return_object_of_type(
            ListOfCadetIdsWithGroups,
            file_identifier=CADETS_WITH_GROUPS_ID,
            additional_file_identifiers=event_id
        )

        return list_of_cadets_with_groups

    def write_groups_for_event(
        self, list_of_cadets_with_groups: ListOfCadetIdsWithGroups, event_id: str
    ):
        self.write_object(list_of_cadets_with_groups,
                          file_identifier=CADETS_WITH_GROUPS_ID,
                          additional_file_identifiers=event_id)



class CsvDataListOfCadetsAtEvent(GenericCsvData, DataListOfCadetsAtEvent):

    def read(self, event_id: str) -> ListOfCadetsAtEvent:
        list_of_cadets = self.read_and_return_object_of_type(
            ListOfCadetsAtEvent,
            file_identifier=CADETS_AT_EVENT_ID,
            additional_file_identifiers=event_id
        )

        return list_of_cadets

    def write(
        self, list_of_cadets_at_event: ListOfCadetsAtEvent, event_id: str
    ):
        self.write_object(list_of_cadets_at_event,
                          file_identifier=CADETS_AT_EVENT_ID,
                          additional_file_identifiers=event_id)


class CsvDataListOfIdentifiedCadetsAtEvent(GenericCsvData, DataListOfIdentifiedCadetsAtEvent):

    def read(self, event_id: str) -> ListOfIdentifiedCadetsAtEvent:
        list_of_cadets = self.read_and_return_object_of_type(
            ListOfIdentifiedCadetsAtEvent,
            file_identifier=IDENTIFIED_CADETS_AT_EVENT_ID,
            additional_file_identifiers=event_id
        )

        return list_of_cadets

    def write(
        self, list_of_cadets_at_event: ListOfIdentifiedCadetsAtEvent, event_id: str
    ):
        self.write_object(list_of_cadets_at_event,
                          file_identifier=IDENTIFIED_CADETS_AT_EVENT_ID,
                          additional_file_identifiers=event_id)
