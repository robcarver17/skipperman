from app.objects.registration_data import RegistrationDataForEvent
from app.objects.event_warnings import ListOfEventWarnings

class DataMappedRegistrationData(object):
    def read(self, event_id: str) -> RegistrationDataForEvent:
        raise NotImplemented

    def write(
        self, mapped_wa_event_with_no_ids: RegistrationDataForEvent, event_id: str
    ):
        raise NotImplemented


class DataListOfEventWarnings(object):
    def read(self, event_id: str) -> ListOfEventWarnings:
        raise NotImplemented

    def write(
        self,
        list_of_event_warnings: ListOfEventWarnings,
        event_id: str,
    ):
        raise NotImplemented