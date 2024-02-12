from app.objects.master_event import (
    MasterEvent,
)
from app.objects.mapped_wa_event_deltas import MappedWAEventListOfDeltaRows
from app.objects.mapped_wa_event import MappedWAEvent


class DataMappedWAEvent(object):
    def read(self, event_id: str) -> MappedWAEvent:
        raise NotImplemented

    def write(self, mapped_wa_event_with_no_ids: MappedWAEvent, event_id: str):
        raise NotImplemented


class DataMappedWAEventDeltaRows(object):
    def read(self, event_id: str) -> MappedWAEventListOfDeltaRows:
        raise NotImplemented

    def write(self, mapped_wa_event_with_ids: MappedWAEventListOfDeltaRows, event_id: str):
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
