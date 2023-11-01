from app.logic.data import DataAndInterface
from app.objects import Event
from app.objects import (
    MappedWAEventWithoutDuplicatesAndWithStatus,
)
from app.objects import MappedWAEventWithIDs


def load_mapped_wa_event_data_without_duplicates(
    data_and_interface: DataAndInterface, event: Event
) -> MappedWAEventWithoutDuplicatesAndWithStatus:

    return data_and_interface.data.data_mapped_wa_event_without_duplicates_and_with_status.read(
        event.id
    )


def save_mapped_wa_event_data_without_duplicates(
    data_and_interface: DataAndInterface,
    event: Event,
    wa_event_data_without_duplicates: MappedWAEventWithoutDuplicatesAndWithStatus,
):

    data_and_interface.data.data_mapped_wa_event_without_duplicates_and_with_status.write(
        mapped_wa_event_without_duplicates=wa_event_data_without_duplicates,
        event_id=event.id,
    )


def save_mapped_wa_event_with_ids(
    mapped_wa_event_data_with_ids: MappedWAEventWithIDs,
    event: Event,
    data_and_interface: DataAndInterface,
):
    data = data_and_interface.data
    data.data_mapped_wa_event_with_cadet_ids.write(
        mapped_wa_event_with_ids=mapped_wa_event_data_with_ids, event_id=event.id
    )


def load_existing_mapped_wa_event_with_ids(
    event: Event, data_and_interface: DataAndInterface
) -> MappedWAEventWithIDs:
    data = data_and_interface.data
    return data.data_mapped_wa_event_with_cadet_ids.read(event_id=event.id)
