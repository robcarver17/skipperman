from app.data_access.data import data
from app.objects.events import Event
from app.objects.mapped_wa_event_with_id_and_status import (
    MappedWAEventWithoutDuplicatesAndWithStatus,
)
from app.objects.mapped_wa_event_with_ids import MappedWAEventWithIDs
from app.objects.mapped_wa_event_no_ids import MappedWAEventNoIDs


def load_mapped_wa_event_data_without_duplicates(
    event: Event,
) -> MappedWAEventWithoutDuplicatesAndWithStatus:

    return data.data_mapped_wa_event_without_duplicates_and_with_status.read(event.id)


def save_mapped_wa_event_data_without_duplicates(
    event: Event,
    wa_event_data_without_duplicates: MappedWAEventWithoutDuplicatesAndWithStatus,
):

    data.data_mapped_wa_event_without_duplicates_and_with_status.write(
        mapped_wa_event_without_duplicates=wa_event_data_without_duplicates,
        event_id=event.id,
    )


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
