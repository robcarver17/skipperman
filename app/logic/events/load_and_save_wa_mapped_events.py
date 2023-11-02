from app.data_access.api.generic_api import GenericDataApi
from app.objects.events import Event
from app.objects.mapped_wa_event_with_id_and_status import (
    MappedWAEventWithoutDuplicatesAndWithStatus,
)
from app.objects.mapped_wa_event_with_ids import MappedWAEventWithIDs


def load_mapped_wa_event_data_without_duplicates(
    data: GenericDataApi, event: Event
) -> MappedWAEventWithoutDuplicatesAndWithStatus:

    return data.data_mapped_wa_event_without_duplicates_and_with_status.read(
        event.id
    )


def save_mapped_wa_event_data_without_duplicates(
    data: GenericDataApi,
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
    data: GenericDataApi,
):
    data.data_mapped_wa_event_with_cadet_ids.write(
        mapped_wa_event_with_ids=mapped_wa_event_data_with_ids, event_id=event.id
    )


def load_existing_mapped_wa_event_with_ids(
    event: Event, data: GenericDataApi
) -> MappedWAEventWithIDs:
    return data.data_mapped_wa_event_with_cadet_ids.read(event_id=event.id)
