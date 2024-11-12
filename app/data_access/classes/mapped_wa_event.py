from app.objects.registration_data import RegistrationDataForEvent


class DataMappedRegistrationData(object):
    def read(self, event_id: str) -> RegistrationDataForEvent:
        raise NotImplemented

    def write(
        self, mapped_wa_event_with_no_ids: RegistrationDataForEvent, event_id: str
    ):
        raise NotImplemented
