import pandas as pd
from app.data_access.csv.generic_csv_data import GenericCsvData
from app.data_access.classes.cadets import DataListOfCadetsWithGroups
from app.objects.utils import transform_df_to_str
from app.objects.groups import ListOfCadetIdsWithGroups

CADETS_WITH_GROUPS_ID= "cadets_with_groups_for_event"

class CsvDataListOfCadetsWithGroups(GenericCsvData, DataListOfCadetsWithGroups):

    def read_groups_for_event(self, event_id: str) -> ListOfCadetIdsWithGroups:
        list_of_cadets_with_groups = self.read_and_return_object_of_type(
            ListOfCadetIdsWithGroups,
            file_identifier=CADETS_WITH_GROUPS_ID,
            additional_file_identifiers=event_id
        )

        return list_of_cadets_with_groups

    def write_groups_for_event(
        self, event_id: str, list_of_cadets_with_groups: ListOfCadetIdsWithGroups
    ):
        self.write_object(list_of_cadets_with_groups,
                          file_identifier=CADETS_WITH_GROUPS_ID,
                          additional_file_identifiers=event_id)