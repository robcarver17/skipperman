from app.data_access.data import data
from app.objects.wa_event_mapping import ListOfWAEventMaps


def load_wa_event_mapping() -> ListOfWAEventMaps:
    return data.data_wa_event_mapping.read()


def save_wa_event_mapping(wa_event_mapping: ListOfWAEventMaps):
    data.data_wa_event_mapping.write(
        wa_event_mapping,
    )
