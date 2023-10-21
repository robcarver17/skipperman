import pandas as pd
from app.data_access import GenericCsvData
from app.data_access import DataListOfCadetsWithGroups

from app.objects import ListOfCadetIdsWithGroups


class CsvDataListOfCadetsWithGroups(GenericCsvData, DataListOfCadetsWithGroups):
    def read(self, event_id: str) -> ListOfCadetIdsWithGroups:
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        try:
            list_as_df = pd.read_csv(path_and_filename)
        except FileNotFoundError:
            return ListOfCadetIdsWithGroups.create_empty()

        list_of_cadets_with_groups = ListOfCadetIdsWithGroups.from_df_of_str(list_as_df)

        return list_of_cadets_with_groups

    def write(
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
