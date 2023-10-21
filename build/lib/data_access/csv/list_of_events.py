import pandas as pd
from app.data_access import GenericCsvData
from app.data_access import DataListOfEvents

from app.objects import ListOfEvents


class CsvDataListOfEvents(GenericCsvData, DataListOfEvents):
    def read(self) -> ListOfEvents:
        path_and_filename = self.path_and_filename
        try:
            df = pd.read_csv(path_and_filename)
        except FileNotFoundError:
            return ListOfEvents.create_empty()

        list_of_events = ListOfEvents.from_df_of_str(df)

        return list_of_events

    def write(self, list_of_events: ListOfEvents):
        df = list_of_events.to_df_of_str()
        path_and_filename = self.path_and_filename

        df.to_csv(path_and_filename, index=False)

    @property
    def path_and_filename(self):
        return self.get_path_and_filename_for_named_csv_file("list_of_events")
