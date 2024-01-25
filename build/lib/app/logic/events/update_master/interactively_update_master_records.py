from typing import Union
from app.backend.cadets import cadet_name_from_id
from app.logic.events.update_master.track_cadet_id_in_master_file_update import get_and_save_next_cadet_id_in_event_data
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.logic.abstract_interface import (
    abstractInterface,
)
from app.logic.abstract_logic_api import initial_state_form
from app.logic.events.constants import (
    WA_VOLUNTEER_EXTRACTION_INITIALISE_IN_VIEW_EVENT_STAGE, USE_ORIGINAL_DATA_BUTTON_LABEL, USE_NEW_DATA_BUTTON_LABEL,
    USE_DATA_IN_FORM_BUTTON_LABEL
)

from app.logic.events.events_in_state import get_event_from_state

from app.logic.events.update_master.update_existing_master_event_data_forms import (
    display_form_for_update_to_existing_row_of_event_data
)
from app.logic.events.update_master.update_master_from_form_entries import update_mapped_wa_event_data_with_new_data, \
    update_mapped_wa_event_data_with_form_data

from app.backend.update_master_event_data import (
    add_new_row_to_master_event_data,
    update_row_in_master_event_data, is_cadet_already_in_master_data, is_cadet_present_in_mapped_event_data,
    any_important_difference_between_rows, get_row_in_mapped_event_for_cadet_id, get_row_in_master_event_for_cadet_id,
)
from app.objects.events import Event
from app.objects.constants import NoMoreData, DuplicateCadets
from app.objects.mapped_wa_event_with_ids import RowInMappedWAEventWithId
from app.objects.master_event import RowInMasterEvent, get_row_of_master_event_from_mapped_row_with_idx_and_status


def display_form_interactively_update_master_records(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## might seem pointless, but this function has a more meaningful name
    return iterative_process_updates_to_master_event_data(interface=interface)

def iterative_process_updates_to_master_event_data(
    interface: abstractInterface
) -> Union[Form, NewForm]:

    print("Looping through updating master event data")
    event = get_event_from_state(interface)

    try:
        cadet_id = get_and_save_next_cadet_id_in_event_data(interface)
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
        return process_update_to_existing_cadet_in_event_data(
            event=event, cadet_id=cadet_id, interface=interface
        )
    elif (
        cadet_present_in_mapped_event_data and not cadet_already_present_in_master_data
    ):
        return process_update_to_cadet_new_to_master_data(
            event=event, cadet_id=cadet_id, interface=interface
        )
    elif (
        cadet_already_present_in_master_data and not cadet_present_in_mapped_event_data
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
            "ACTION REQUIRED: Cadet %s appears more than once in WA file with an active registration - ignoring all registrations for now - go to WA and cancel one of the registrations please!"
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
