from app.data_access.csv.generic_csv_data import GenericCsvData
from app.data_access.resolve_paths_and_filenames import EVENT_FILE_IDENTIFIER

from app.objects.events import ListOfEvents


class CsvDataListOfEvents(GenericCsvData):
    def read(self) -> ListOfEvents:
        return self.read_and_return_object_of_type(
            ListOfEvents, file_identifier=EVENT_FILE_IDENTIFIER
        )

    def write(self, list_of_events: ListOfEvents):
        self.write_object(list_of_events, file_identifier=EVENT_FILE_IDENTIFIER)
