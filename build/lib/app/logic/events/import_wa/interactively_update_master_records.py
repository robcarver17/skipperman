from typing import Union
from app.backend.cadets import cadet_name_from_id
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.logic.abstract_interface import (
    abstractInterface,
)
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.constants import (
    USE_ORIGINAL_DATA_BUTTON_LABEL,
    USE_DATA_IN_FORM_BUTTON_LABEL,
    USE_NEW_DATA_BUTTON_LABEL,
    CADET_ID,
    WA_VOLUNTEER_EXTRACTION_INITIALISE_IN_VIEW_EVENT_STAGE
)

from app.logic.events.events_in_state import get_event_from_state

from app.backend.load_and_save_wa_mapped_events import load_master_event
from app.logic.events.update_master.update_existing_master_event_data_forms import (
    display_form_for_update_to_existing_row_of_event_data,
)
from app.logic.events.update_master.update_master_from_form_entries import update_mapped_wa_event_data_with_new_data, \
    update_mapped_wa_event_data_with_form_data
from app.logic.events.update_master.track_cadet_id_in_master_file_update import get_current_cadet_id

from app.backend.update_master_event_data import (
    get_row_of_master_event_from_mapped_row_with_idx_and_status,
    add_new_row_to_master_event_data,
    update_row_in_master_event_data, any_important_difference_between_rows, get_row_in_mapped_event_for_cadet_id,
    get_row_in_master_event_for_cadet_id,
)
from app.backend.load_and_save_wa_mapped_events import (
    load_existing_mapped_wa_event_with_ids,
)
from app.objects.events import Event
from app.objects.mapped_wa_event_with_ids import RowInMappedWAEventWithId
from app.objects.master_event import RowInMasterEvent
from app.objects.constants import NoMoreData, missing_data, DuplicateCadets


def display_form_interactively_update_master_records(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return iterative_process_updates_to_master_event_data(interface)


def iterative_process_updates_to_master_event_data(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    print("Looping through updating master event data")

    event = get_event_from_state(interface)

    try:
        cadet_id = get_and_save_next_cadet_id(interface)
    except NoMoreData:
        print("Finished looping")
        return NewForm(WA_VOLUNTEER_EXTRACTION_INITIALISE_IN_VIEW_EVENT_STAGE)

    print("Current cadet id is %s" % cadet_id)

    return process_update_to_cadet_in_event_data(
        interface=interface, event=event, cadet_id=cadet_id
    )


def process_update_to_cadet_in_event_data(
    interface: abstractInterface, event: Event, cadet_id: str
) -> Form:
    cadet_already_present_in_master_data = is_cadet_already_in_master_data(
        event=event, cadet_id=cadet_id
    )
    cadet_present_in_mapped_event_data = is_cadet_present_in_mapped_event_data(
        event=event, cadet_id=cadet_id
    )

    if cadet_present_in_mapped_event_data and cadet_already_present_in_master_data:
        ## consider duplicates
        return process_update_to_existing_cadet_in_event_data(
            event=event, cadet_id=cadet_id, interface=interface
        )
    elif (
        cadet_present_in_mapped_event_data and not cadet_already_present_in_master_data
    ):
        ## consider duplicates
        return process_update_to_cadet_new_to_master_data(
            event=event, cadet_id=cadet_id, interface=interface
        )
    elif (
        not cadet_present_in_mapped_event_data and cadet_already_present_in_master_data
    ):
        return process_update_to_deleted_cadet(
            event=event, cadet_id=cadet_id, interface=interface
        )
    else:
        interface.log_error("Cadet ID %d was next ID but now can't find in any file?")
        return initial_state_form


def process_update_to_existing_cadet_in_event_data(
    interface: abstractInterface, event: Event, cadet_id: str
) -> Form:
    try:
        row_in_mapped_event = get_row_in_mapped_event_for_cadet_id(
            cadet_id=cadet_id, event=event
        )
    except DuplicateCadets:
        interface.log_message(
            "ACTION REQUIRED: Cadet %s appears more than once in WA file with an active registration - ignoring for now - go to WA and cancel one of the registrations please!"
            % cadet_name_from_id(cadet_id)
        )
        return iterative_process_updates_to_master_event_data(interface)

    existing_row_in_master_event = get_row_in_master_event_for_cadet_id(
        event=event, cadet_id=cadet_id
    )

    return process_update_to_existing_row_of_event_data(
        interface=interface,
        row_in_mapped_wa_event_with_id=row_in_mapped_event,
        existing_row_in_master_event=existing_row_in_master_event,
    )


def process_update_to_cadet_new_to_master_data(
    interface: abstractInterface, event: Event, cadet_id: str
) -> Form:
    print("Row in master data for cadet with id %s" % cadet_id)
    try:
        relevant_row = get_row_in_mapped_event_for_cadet_id(
            cadet_id=cadet_id, event=event
        )
    except DuplicateCadets:
        interface.log_message(
            "ACTION REQUIRED: Cadet %s appears more than once in WA file with an active registration - ignoring for now - go to WA and cancel one of the registrations please!"
            % cadet_name_from_id(cadet_id)
        )
        return iterative_process_updates_to_master_event_data(interface)

    add_new_row_to_master_event_data(
        event=event, row_in_mapped_wa_event_with_id=relevant_row
    )

    return iterative_process_updates_to_master_event_data(interface)


def process_update_to_deleted_cadet(
    interface: abstractInterface, event: Event, cadet_id: str
) -> Form:
    existing_row_in_master_event = get_row_in_master_event_for_cadet_id(
        event=event, cadet_id=cadet_id
    )
    if not existing_row_in_master_event.is_deleted():
        interface.log_message(
            "Cadet %s was in WA event data, now appears to be missing or cancelled in latest file - marked as deleted"
            % cadet_name_from_id(cadet_id)
        )
        existing_row_in_master_event.mark_as_deleted()
        update_row_in_master_event_data(
            event=event,
            new_row_in_mapped_wa_event_with_status=existing_row_in_master_event,
        )
    else:
        print("Cadet %s already marked as deleted" % cadet_name_from_id(cadet_id))

    return iterative_process_updates_to_master_event_data(interface)


def is_cadet_already_in_master_data(event: Event, cadet_id: str) -> bool:
    master_event = load_master_event(event)
    cadet_already_present_in_master_data = master_event.is_cadet_id_in_event(cadet_id)

    return cadet_already_present_in_master_data


def is_cadet_present_in_mapped_event_data(event: Event, cadet_id: str) -> bool:
    mapped_event = load_existing_mapped_wa_event_with_ids(event)
    cadet_present = mapped_event.is_cadet_id_in_event(cadet_id)

    return cadet_present


def process_update_to_existing_row_of_event_data(
    interface: abstractInterface,
    row_in_mapped_wa_event_with_id: RowInMappedWAEventWithId,
    existing_row_in_master_event: RowInMasterEvent,
) -> Form:
    new_row_in_mapped_wa_event_with_status = (
        get_row_of_master_event_from_mapped_row_with_idx_and_status(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
        )
    )

    ## CHANGE TO COMPARE ONLY KEY FIELDS
    if not any_important_difference_between_rows(
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
        existing_row_in_master_event=existing_row_in_master_event,
    ):
        ## nothing to do
        print("No change to %s" % (str(existing_row_in_master_event)))
        return iterative_process_updates_to_master_event_data(interface)
    else:
        print("Data has changed displaying form")
        return display_form_for_update_to_existing_row_of_event_data(
            new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
            existing_row_in_master_event=existing_row_in_master_event)


def post_form_interactively_update_master_records(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == USE_ORIGINAL_DATA_BUTTON_LABEL:
        ## nothing to do, no change to master file
        print("Using original data")
    elif last_button_pressed == USE_NEW_DATA_BUTTON_LABEL:
        print("using new data")
        update_mapped_wa_event_data_with_new_data(interface)
    elif last_button_pressed == USE_DATA_IN_FORM_BUTTON_LABEL:
        print("Updating from form data")
        update_mapped_wa_event_data_with_form_data(interface)

    return iterative_process_updates_to_master_event_data(interface)


def get_and_save_next_cadet_id(interface: abstractInterface) -> str:
    current_id = get_current_cadet_id(interface)
    if current_id is missing_data:
        new_id = get_first_cadet_id_in_event_data(interface)
    else:
        new_id = get_next_cadet_id_in_event_data(
            interface=interface, current_id=current_id
        )

    interface.set_persistent_value(CADET_ID, new_id)

    return new_id


def get_first_cadet_id_in_event_data(interface: abstractInterface) -> str:
    event = get_event_from_state(interface)
    list_of_ids = list_of_cadet_ids_in_master_and_mapped_data(event)
    id = list_of_ids[0]

    print("Getting first ID %s from list %s " % (id, list_of_ids))

    return id


def get_next_cadet_id_in_event_data(
    interface: abstractInterface, current_id: str
) -> str:
    event = get_event_from_state(interface)
    list_of_ids = list_of_cadet_ids_in_master_and_mapped_data(event)
    current_index = list_of_ids.index(current_id)

    try:
        new_id = list_of_ids[current_index + 1]
    except:
        raise NoMoreData

    return new_id


def list_of_cadet_ids_in_master_and_mapped_data(event: Event) -> list:
    master_event = load_master_event(event)
    mapped_event = load_existing_mapped_wa_event_with_ids(event)

    master_ids = master_event.list_of_cadet_ids
    mapped_ids = mapped_event.list_of_cadet_ids

    all_ids = list(set(mapped_ids).union(set(master_ids)))
    all_ids.sort()

    return all_ids
