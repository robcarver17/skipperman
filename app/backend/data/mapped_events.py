from typing import List

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.data_access.storage_layer.api import DataLayer

from app.data_access.data import DEPRECATED_data
from app.objects.constants import missing_data
from app.objects.events import Event
from app.objects.mapped_wa_event import MappedWAEvent, RowInMappedWAEvent

def get_row_in_mapped_event_data_given_id(interface: abstractInterface, event: Event, row_id: str) -> RowInMappedWAEvent:
    mapped_data = MappedEventsData(interface.data)

    return mapped_data.get_row_with_rowid(event=event, row_id=row_id)


def save_mapped_wa_event(
    interface: abstractInterface,
    mapped_wa_event_data: MappedWAEvent,
    event: Event,
):
    mapped_events_data = MappedEventsData(interface.data)
    mapped_events_data.save_mapped_wa_event(mapped_wa_event_data=mapped_wa_event_data,event=event)

class MappedEventsData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def get_row_with_rowid(self, event: Event, row_id:str)  -> RowInMappedWAEvent:
        mapped_data = self.get_mapped_wa_event(event)
        try:
            row_data = mapped_data.get_row_with_rowid(row_id)
        except:
            return missing_data

        return row_data

    def get_list_of_row_ids_for_event(self, event: Event) -> List[str]:
        mapped_event = self.get_mapped_wa_event(event)
        return mapped_event.list_of_row_ids()

    def save_mapped_wa_event(self, mapped_wa_event_data: MappedWAEvent, event: Event,):
        self.data_api.save_mapped_wa_event(mapped_wa_event_data=mapped_wa_event_data, event=event)

    def get_mapped_wa_event(self, event: Event) -> MappedWAEvent:
        return self.data_api.get_mapped_wa_event(event)

def DEPRECCATE_save_mapped_wa_event(
    mapped_wa_event_data: MappedWAEvent,
    event: Event,
):
    DEPRECATED_data.data_mapped_wa_event.write(
        mapped_wa_event=mapped_wa_event_data, event_id=event.id
    )


def DEPRECATE_load_mapped_wa_event(
    event: Event,
) -> MappedWAEvent:
    return DEPRECATED_data.data_mapped_wa_event.read(event.id)

def DEPRECATE_get_row_in_mapped_event_data_given_id(event: Event, row_id: str) -> RowInMappedWAEvent:
    mapped_data = DEPRECATE_load_mapped_wa_event(event)
    try:
        row_data = mapped_data.get_row_with_rowid(row_id)
    except:
        return missing_data

    return row_data
