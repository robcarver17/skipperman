from app.data_access.csv.generic_csv_data import GenericCsvData
from app.data_access.resolve_paths_and_filenames import (
    MAPPED_REGISTRATION_DATA_FILE_ID,
)

from app.objects.registration_data import RegistrationDataForEvent
from app.data_access.classes.mapped_wa_event import (
    DataMappedRegistrationData,
)


class CsvDataMappedRegistrationData(GenericCsvData, DataMappedRegistrationData):
    def read(self, event_id: str) -> RegistrationDataForEvent:
        registration_data = self.read_and_return_object_of_type(
            RegistrationDataForEvent,
            file_identifier=MAPPED_REGISTRATION_DATA_FILE_ID,
            additional_file_identifiers=event_id,
        )

        return registration_data

    def write(self, mapped_wa_event: RegistrationDataForEvent, event_id: str):

        self.write_object(
            mapped_wa_event,
            file_identifier=MAPPED_REGISTRATION_DATA_FILE_ID,
            additional_file_identifiers=event_id,
        )
