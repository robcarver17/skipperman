from app.objects import (
    MappedWAEventWithoutDuplicatesAndWithStatus,
)
from app.objects import MappedWAEventWithIDs


class DataMappedWAEventWithIDs(object):
    def read(self, event_id: str) -> MappedWAEventWithIDs:
        raise NotImplemented

    def write(self, mapped_wa_event_with_ids: MappedWAEventWithIDs, event_id: str):
        raise NotImplemented


class DataMappedWAEventWithoutDuplicatesAndWithStatus(object):
    def read(self, event_id: str) -> MappedWAEventWithoutDuplicatesAndWithStatus:
        raise NotImplemented

    def write(
        self,
        mapped_wa_event_without_duplicates: MappedWAEventWithoutDuplicatesAndWithStatus,
        event_id: str,
    ):
        raise NotImplemented
