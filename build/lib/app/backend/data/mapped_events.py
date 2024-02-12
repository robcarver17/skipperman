from app.data_access.data import data
from app.objects.events import Event
from app.objects.mapped_wa_event import MappedWAEvent
from app.objects.mapped_wa_event_deltas import MappedWAEventListOfDeltaRows
from app.objects.master_event import MasterEvent


def load_master_event(
    event: Event,
) -> MasterEvent:
    return data.data_master_event.read(event.id)


def save_master_event(event: Event, master_event: MasterEvent):
    data.data_master_event.write(master_event=master_event, event_id=event.id)


def save_mapped_wa_event_delta_rows(
    mapped_wa_event_data_delta_rows: MappedWAEventListOfDeltaRows,
    event: Event,
):
    data.data_mapped_wa_event_with_deltas.write(
        mapped_wa_event_with_ids=mapped_wa_event_data_delta_rows, event_id=event.id
    )


def load_existing_mapped_wa_event_with_ids(
    event: Event,
) -> MappedWAEvent:
    return data.data_mapped_wa_event_with_deltas.read(event_id=event.id)


def save_mapped_wa_event_with_no_ids(
    mapped_wa_event_data_with_no_ids: MappedWAEvent,
    event: Event,
):
    data.data_mapped_wa_event.write(
        mapped_wa_event_with_no_ids=mapped_wa_event_data_with_no_ids, event_id=event.id
    )


def load_mapped_wa_event(
    event: Event,
) -> MappedWAEvent:
    return data.data_mapped_wa_event.read(event.id)


