import pandas as pd
from data_access.csv.generic_csv_data import GenericCsvData
from objects.wa_event_mapping import WAEventMapping
from data_access.classes.wa_event_mapping import DataWAEventMapping


class CsvDataWAEventMapping(GenericCsvData, DataWAEventMapping):
    def read(self) -> WAEventMapping:
        path_and_filename = self.path_and_filename
        try:
            df = pd.read_csv(path_and_filename)
        except FileNotFoundError:
            return WAEventMapping.create_empty()

        wa_event_mapping = WAEventMapping.from_df(df)

        return wa_event_mapping

    def write(self, wa_event_mapping: WAEventMapping):
        df = wa_event_mapping.to_df()
        path_and_filename = self.path_and_filename

        df.to_csv(path_and_filename, index=False)

    @property
    def path_and_filename(self):
        return self.get_path_and_filename_for_named_csv_file("wa_event_mapping")
