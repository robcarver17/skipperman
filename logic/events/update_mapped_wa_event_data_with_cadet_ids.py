from logic.data_and_interface import DataAndInterface
from logic.events.add_cadet_ids_to_mapped_wa_event_data import (
    add_cadet_ids_to_mapped_wa_event_data,
)
from logic.events.load_and_save_wa_mapped_events import (
    load_existing_mapped_wa_event_with_ids,
    save_mapped_wa_event_with_ids,
)

from objects.events import Event
from objects.mapped_wa_event_no_ids import MappedWAEventNoIDs
from objects.mapped_wa_event_with_ids import (
    MappedWAEventWithIDs,
)


def update_and_save_mapped_wa_event_data_with_cadet_ids(
    data_and_interface: DataAndInterface,
    mapped_wa_event_data: MappedWAEventNoIDs,
    event: Event,
):

    existing_mapped_wa_event_with_ids = load_existing_mapped_wa_event_with_ids(
        data_and_interface=data_and_interface, event=event
    )

    ## Each of these functions does an in place update
    remove_deleted_cadets_from_event(
        mapped_wa_event_data=mapped_wa_event_data,
        existing_mapped_wa_event_with_ids=existing_mapped_wa_event_with_ids,
    )

    update_existing_wa_event_data_with_new_field_data(
        mapped_wa_event_data=mapped_wa_event_data,
        existing_mapped_wa_event_with_ids=existing_mapped_wa_event_with_ids,
    )

    add_new_rows_to_event(
        data_and_interface=data_and_interface,
        mapped_wa_event_data=mapped_wa_event_data,
        existing_mapped_wa_event_with_ids=existing_mapped_wa_event_with_ids,
    )

    save_mapped_wa_event_with_ids(
        mapped_wa_event_data_with_ids=existing_mapped_wa_event_with_ids,
        event=event,
        data_and_interface=data_and_interface,
    )

    return existing_mapped_wa_event_with_ids


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


def add_new_rows_to_event(
    data_and_interface: DataAndInterface,
    mapped_wa_event_data: MappedWAEventNoIDs,
    existing_mapped_wa_event_with_ids: MappedWAEventWithIDs,
):

    ## New rows not in previous file
    new_mapped_wa_event_data = only_new_rows_in_mapped_wa_event_data(
        mapped_wa_event_data=mapped_wa_event_data,
        existing_mapped_wa_event_with_ids=existing_mapped_wa_event_with_ids,
    )

    ## add IDS to those
    new_mapped_wa_event_data_with_ids = add_cadet_ids_to_mapped_wa_event_data(
        mapped_wa_event_data=new_mapped_wa_event_data,
        data_and_interface=data_and_interface,
    )

    existing_mapped_wa_event_with_ids.add_new_rows(new_mapped_wa_event_data_with_ids)


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

    return new_rows
