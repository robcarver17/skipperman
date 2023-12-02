import pandas as pd
from app.data_access.csv.generic_csv_data import GenericCsvData
from app.data_access.classes.cadets_with_groups_for_event import (
    DataListOfCadetsWithGroups,
)
from app.data_access.csv.utils import transform_df_to_str
from app.objects.groups import ListOfCadetIdsWithGroups

LAST_GROUP_ALIAS = "_Last_group"


class CsvDataListOfCadetsWithGroups(GenericCsvData, DataListOfCadetsWithGroups):
    def read_last_groups(self) -> ListOfCadetIdsWithGroups:
        return self.read_groups_for_event(LAST_GROUP_ALIAS)

    def write_last_groups(self, list_of_cadets_with_groups: ListOfCadetIdsWithGroups):
        self.write_groups_for_event(
            event_id=LAST_GROUP_ALIAS,
            list_of_cadets_with_groups=list_of_cadets_with_groups,
        )

    def read_groups_for_event(self, event_id: str) -> ListOfCadetIdsWithGroups:
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        try:
            list_as_df = pd.read_csv(path_and_filename)
        except:
            return ListOfCadetIdsWithGroups.create_empty()
        list_as_df = transform_df_to_str(list_as_df)
        list_of_cadets_with_groups = ListOfCadetIdsWithGroups.from_df_of_str(list_as_df)

        return list_of_cadets_with_groups

    def write_groups_for_event(
        self, event_id: str, list_of_cadets_with_groups: ListOfCadetIdsWithGroups
    ):
        df = list_of_cadets_with_groups.to_df()
        path_and_filename = self.path_and_filename_for_eventid(event_id)

        df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_eventid(self, event_id: str):
        return self.get_path_and_filename_for_named_csv_file(
            "cadets_with_groups_for_event",
            additional_file_identifiers=event_id,
        )
