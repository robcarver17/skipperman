from typing import List

from app.backend.data.mapped_events import *

from app.objects.events import Event
from app.objects.mapped_wa_event import MappedWAEvent
from app.objects.mapped_wa_event_deltas import (
    MappedWAEventListOfDeltaRows, create_list_of_delta_rows
)


def create_deltas_of_mapped_event_data(
    mapped_wa_event_data: MappedWAEvent, event: Event
) -> MappedWAEventListOfDeltaRows:
    existing_mapped_wa_event = load_mapped_wa_event(
        event=event
    )
    delta_rows = create_list_of_delta_rows(original_event=existing_mapped_wa_event,
                                           new_event=mapped_wa_event_data)

    save_mapped_wa_event_delta_rows(
        mapped_wa_event_data_delta_rows=delta_rows, event=event
    )

    return delta_rows

def messaging_for_delta_rows(delta_rows: MappedWAEventListOfDeltaRows) -> List[str]:
    list_of_messages = []
    deleted = delta_rows.count_of_deleted
    if deleted > 0:
        list_of_messages.append(
            "Removed %d rows of existing data that have vanished from WA file"
            % deleted
        )

    changed = delta_rows.count_of_changed
    if changed > 0:
        list_of_messages.append(
            "Found %d rows of existing data that may have changed in WA file"
            % changed
        )

    unchanged = delta_rows.count_of_unchanged
    if unchanged > 0:
        list_of_messages.append(
            "Found %d rows of existing data that have not changed in WA file"
            % unchanged
        )

    new = delta_rows.count_of_new
    if new > 0:
        list_of_messages.append(
            "Found %d rows of new data not in previous file(s)"
            % new
        )

    return list_of_messages

