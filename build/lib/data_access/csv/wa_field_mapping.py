import pandas as pd
from data_access.csv.generic_csv_data import GenericCsvData
from objects.wa_field_mapping import WAFieldMapping
from data_access.classes.wa_field_mapping import DataWAFieldMapping


class CsvDataWAFieldMapping(GenericCsvData, DataWAFieldMapping):
    def read(self, event_id: str) -> WAFieldMapping:
        path_and_filename = self.path_and_filename_for_eventid(event_id)
        try:
            df = pd.read_csv(path_and_filename)
        except FileNotFoundError:
            return WAFieldMapping.create_empty()

        ## error condition
        wa_field_mapping = WAFieldMapping.from_df(df)

        return wa_field_mapping

    def write(self, event_id: str, wa_field_mapping: WAFieldMapping):
        df = wa_field_mapping.to_df()
        path_and_filename = self.path_and_filename_for_eventid(event_id)

        df.to_csv(path_and_filename, index=False)

    def path_and_filename_for_eventid(self, event_id: str):
        return self.get_path_and_filename_for_named_csv_file(
            "wa_field_mapping", additional_file_identifiers=event_id
        )
