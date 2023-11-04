from typing import Callable
from app.logic.events.load_and_save_wa_mapped_events import (
    load_existing_mapped_wa_event_with_ids,
    save_mapped_wa_event_with_ids,
    save_mapped_wa_event_with_no_ids,
)

from app.objects.events import Event
from app.objects.mapped_wa_event_no_ids import MappedWAEventNoIDs
from app.objects.mapped_wa_event_with_ids import (
    MappedWAEventWithIDs,
)

from app.interface.flask.flash import flash_log, flash_error


def update_and_save_mapped_wa_event_data_with_and_without_ids(
    mapped_wa_event_data: MappedWAEventNoIDs,
    event: Event,
):

    existing_mapped_wa_event_with_ids = load_existing_mapped_wa_event_with_ids(
        event=event
    )
    ## Each of these functions does an in place update
    ## offline
    remove_deleted_cadets_from_event(
        mapped_wa_event_data=mapped_wa_event_data,
        existing_mapped_wa_event_with_ids=existing_mapped_wa_event_with_ids,
    )

    update_existing_wa_event_data_with_new_field_data(
        mapped_wa_event_data=mapped_wa_event_data,
        existing_mapped_wa_event_with_ids=existing_mapped_wa_event_with_ids,
    )

    new_mapped_wa_event_data_no_ids = only_new_rows_in_mapped_wa_event_data(
        mapped_wa_event_data=mapped_wa_event_data,
        existing_mapped_wa_event_with_ids=existing_mapped_wa_event_with_ids,
    )
    save_mapped_wa_event_with_ids(
        mapped_wa_event_data_with_ids=existing_mapped_wa_event_with_ids, event=event
    )
    save_mapped_wa_event_with_no_ids(
        mapped_wa_event_data_with_no_ids=new_mapped_wa_event_data_no_ids, event=event
    )


def remove_deleted_cadets_from_event(
    mapped_wa_event_data: MappedWAEventNoIDs,
    existing_mapped_wa_event_with_ids: MappedWAEventWithIDs,
):
    ## in place deletion
    ## Cadets that were in previous file and now missing
    ## Shouldn't happen except for a WA bug
    ## We remove from here, they will be marked as status deleted in next step
    ## If they re-appear then they will be treated as new cadets here, but assuming
    ##   ID is correctly matched any prior data will be kept
    #
    missing_timestamps = existing_timestamps_that_are_missing_from_mapped_wa_event_data(
        mapped_wa_event_data=mapped_wa_event_data,
        existing_mapped_wa_event_with_ids=existing_mapped_wa_event_with_ids,
    )

    existing_mapped_wa_event_with_ids.delete_list_of_rows_with_timestamps(
        missing_timestamps
    )
    if len(missing_timestamps) > 0:
        flash_log(
            "Removed %d rows of existing data that have vanised"
            % len(missing_timestamps)
        )


def existing_timestamps_that_are_missing_from_mapped_wa_event_data(
    mapped_wa_event_data: MappedWAEventNoIDs,
    existing_mapped_wa_event_with_ids: MappedWAEventWithIDs,
) -> list:

    list_of_timestamps_in_existing_data = (
        existing_mapped_wa_event_with_ids.list_of_timestamps()
    )
    list_of_timestamps_in_mapped_data = mapped_wa_event_data.list_of_timestamps()

    missing_timestamps = list(
        set(list_of_timestamps_in_existing_data).difference(
            set(list_of_timestamps_in_mapped_data)
        )
    )

    return missing_timestamps


def update_existing_wa_event_data_with_new_field_data(
    mapped_wa_event_data: MappedWAEventNoIDs,
    existing_mapped_wa_event_with_ids: MappedWAEventWithIDs,
):

    list_of_timestamps_in_existing_data = (
        existing_mapped_wa_event_with_ids.list_of_timestamps()
    )
    list_of_timestamps_in_mapped_data = mapped_wa_event_data.list_of_timestamps()

    timestamps_in_both = list(
        set(list_of_timestamps_in_existing_data).intersection(
            set(list_of_timestamps_in_mapped_data)
        )
    )

    [
        existing_mapped_wa_event_with_ids.update_data_in_row_with_timestamp(
            timestamp=timestamp,
            data=mapped_wa_event_data.get_row_with_timestamp(timestamp),
        )
        for timestamp in timestamps_in_both
    ]

    if len(timestamps_in_both) > 0:
        flash_log(
            "Found %d rows of existing data that may have changed"
            % len(timestamps_in_both)
        )


def only_new_rows_in_mapped_wa_event_data(
    mapped_wa_event_data: MappedWAEventNoIDs,
    existing_mapped_wa_event_with_ids: MappedWAEventWithIDs,
) -> MappedWAEventNoIDs:
    if len(existing_mapped_wa_event_with_ids) == 0:
        ## all new
        return mapped_wa_event_data

    list_of_timestamps_in_existing_wa_event = (
        existing_mapped_wa_event_with_ids.list_of_timestamps()
    )
    list_of_timestamps_in_mapped_data = mapped_wa_event_data.list_of_timestamps()
    new_timestamps = list(
        set(list_of_timestamps_in_mapped_data).difference(
            list_of_timestamps_in_existing_wa_event
        )
    )

    new_rows = mapped_wa_event_data.subset_with_timestamps(new_timestamps)
    if len(new_rows) > 0:
        flash_log("Found %d rows of new data not in previous file(s)" % len(new_rows))

    return new_rows
