from objects.mapped_wa_event import MappedWAEvent

class DataMappedWAEvent(object):
    def read(self, event_id: str) -> MappedWAEvent:
        raise NotImplemented

    def write(self, mapped_wa_event: MappedWAEvent, event_id: str):
        raise NotImplemented

