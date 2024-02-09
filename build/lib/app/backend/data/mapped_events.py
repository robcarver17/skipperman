from app.data_access.data import data
from app.objects.events import Event
from app.objects.mapped_wa_event_no_ids import MappedWAEventNoIDs
from app.objects.mapped_wa_event_with_ids import MappedWAEventWithIDs
from app.objects.master_event import MasterEvent


def load_master_event(
    event: Event,
) -> MasterEvent:
    return data.data_master_event.read(event.id)


def save_master_event(event: Event, master_event: MasterEvent):
    data.data_master_event.write(master_event=master_event, event_id=event.id)


def save_mapped_wa_event_with_ids(
    mapped_wa_event_data_with_ids: MappedWAEventWithIDs,
    event: Event,
):
    data.data_mapped_wa_event_with_cadet_ids.write(
        mapped_wa_event_with_ids=mapped_wa_event_data_with_ids, event_id=event.id
    )


def load_existing_mapped_wa_event_with_ids(
    event: Event,
) -> MappedWAEventWithIDs:
    return data.data_mapped_wa_event_with_cadet_ids.read(event_id=event.id)


def save_mapped_wa_event_with_no_ids(
    mapped_wa_event_data_with_no_ids: MappedWAEventNoIDs,
    event: Event,
):
    data.data_mapped_wa_event_with_no_ids.write(
        mapped_wa_event_with_no_ids=mapped_wa_event_data_with_no_ids, event_id=event.id
    )


def load_mapped_wa_event_with_no_ids(
    event: Event,
) -> MappedWAEventNoIDs:
    return data.data_mapped_wa_event_with_no_ids.read(event.id)


