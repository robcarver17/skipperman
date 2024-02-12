from app.objects.master_event import (
    MasterEvent,
)
from app.objects.mapped_wa_event_deltas import MappedWAEventWithIDs
from app.objects.mapped_wa_event import MappedWAEvent


class DataMappedWAEventWithNoIDs(object):
    def read(self, event_id: str) -> MappedWAEvent:
        raise NotImplemented

    def write(self, mapped_wa_event_with_no_ids: MappedWAEvent, event_id: str):
        raise NotImplemented


class DataMappedWAEventWithIDs(object):
    def read(self, event_id: str) -> MappedWAEventWithIDs:
        raise NotImplemented

    def write(self, mapped_wa_event_with_ids: MappedWAEventWithIDs, event_id: str):
        raise NotImplemented


class DataMasterEvent(object):
    def read(self, event_id: str) -> MasterEvent:
        raise NotImplemented

    def write(
        self,
        master_event: MasterEvent,
        event_id: str,
    ):
        raise NotImplemented
