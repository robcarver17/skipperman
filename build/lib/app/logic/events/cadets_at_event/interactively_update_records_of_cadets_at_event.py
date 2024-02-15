from typing import Union
from app.backend.cadets import cadet_name_from_id
from app.backend.wa_import.update_cadets_at_event import is_cadet_already_at_event, is_cadet_in_mapped_data, \
    get_row_in_mapped_event_for_cadet_id_active_registration_only, add_new_cadet_to_event, \
    get_cadet_at_event_for_cadet_id, mark_cadet_at_event_as_deleted, \
    get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active, any_important_difference_between_cadets_at_event
from app.logic.abstract_logic_api import initial_state_form

from app.logic.events.cadets_at_event.track_cadet_id_in_master_file_update import get_and_save_next_cadet_id_in_event_data

from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.logic.events.constants import (
    USE_ORIGINAL_DATA_BUTTON_LABEL, USE_NEW_DATA_BUTTON_LABEL,
    USE_DATA_IN_FORM_BUTTON_LABEL, WA_UPDATE_CONTROLLER_IN_VIEW_EVENT_STAGE
)

from app.logic.events.events_in_state import get_event_from_state

from app.logic.events.cadets_at_event.update_existing_cadet_at_event_forms import (
    display_form_for_update_to_existing_cadet_at_event
)
from app.logic.events.cadets_at_event.update_existing_cadet_at_event_from_form_entries import update_cadets_at_event_with_new_data, \
    update_cadets_at_event_with_form_data
from app.objects.cadet_at_event import CadetAtEvent, get_cadet_at_event_from_row_in_mapped_event

from app.objects.events import Event
from app.objects.constants import NoMoreData, DuplicateCadets, missing_data
from app.objects.mapped_wa_event import RowInMappedWAEvent


def display_form_interactively_update_cadets_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## might seem pointless, but this function has a more meaningful name
    return iterative_process_updates_to_cadets_at_event(interface=interface)

def iterative_process_updates_to_cadets_at_event(
    interface: abstractInterface
) -> Union[Form, NewForm]:

    print("Looping through updating delta data")
    event = get_event_from_state(interface)

    try:
        cadet_id = get_and_save_next_cadet_id_in_event_data(interface)
    except NoMoreData:
        print("Finished looping")
        ## All imports done, back to controller
        return NewForm(WA_UPDATE_CONTROLLER_IN_VIEW_EVENT_STAGE)

    print("Current cadet id is %s" % cadet_id)

    return process_update_to_cadet_data(
        interface=interface, event=event, cadet_id=cadet_id
    )



def process_update_to_cadet_data(
    interface: abstractInterface, event: Event, cadet_id: str
) -> Form:
    cadet_already_at_event = is_cadet_already_at_event(
        event=event, cadet_id=cadet_id
    )
    cadet_present_in_mapped_event_data = is_cadet_in_mapped_data(
        event=event, cadet_id=cadet_id
    )

    if cadet_present_in_mapped_event_data and cadet_already_at_event:
        return process_update_to_existing_cadet_in_event_data(
            event=event, cadet_id=cadet_id, interface=interface
        )
    elif (
        cadet_present_in_mapped_event_data and not cadet_already_at_event
    ):
        return process_update_to_cadet_new_to_event(
            event=event, cadet_id=cadet_id, interface=interface
        )
    elif (
        cadet_already_at_event and not cadet_present_in_mapped_event_data
    ):
        return process_update_to_deleted_cadet(
            event=event, cadet_id=cadet_id, interface=interface
        )
    else:
        interface.log_error("Cadet ID %d was next ID but now can't find in any file?" % cadet_id)
        return initial_state_form


def process_update_to_cadet_new_to_event(
        interface: abstractInterface, event: Event, cadet_id: str
) -> Form:

    print("New row in master data for cadet with id %s" % cadet_id)

    try:
        relevant_row = get_row_in_mapped_event_for_cadet_id_active_registration_only(
            cadet_id=cadet_id, event=event
        )
    except DuplicateCadets:
        interface.log_error(
            "ACTION REQUIRED: Cadet %s appears more than once in WA file with an active registration - ignoring for now - go to WA and cancel one of the registrations please!"
            % cadet_name_from_id(cadet_id)
        )
        return iterative_process_updates_to_cadets_at_event(interface)

    if relevant_row is missing_data:
        ## There is a new row, but it's cancelled already so ignore it
        return iterative_process_updates_to_cadets_at_event(interface)

    add_new_cadet_to_event(
        event=event, row_in_mapped_wa_event=relevant_row,
        cadet_id=cadet_id
    )

    return iterative_process_updates_to_cadets_at_event(interface)



def process_update_to_deleted_cadet(
        interface: abstractInterface, event: Event, cadet_id: str
) -> Form:

    existing_cadet_at_event = get_cadet_at_event_for_cadet_id(
        event=event, cadet_id=cadet_id
    )
    if not existing_cadet_at_event.is_deleted():
        interface.log_message(
            "Cadet %s was in WA event data, now appears to be missing or cancelled in latest file - marked as deleted"
            % cadet_name_from_id(cadet_id)
        )
        mark_cadet_at_event_as_deleted(cadet_id=cadet_id, event=event)
    else:
        print("Cadet %s already marked as deleted" % cadet_name_from_id(cadet_id))

    return iterative_process_updates_to_cadets_at_event(interface)



def process_update_to_existing_cadet_in_event_data(
    interface: abstractInterface, event: Event, cadet_id: str
) -> Form:

    try:
        relevant_row = get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(
            cadet_id=cadet_id, event=event
        )
    except DuplicateCadets:
        interface.log_error(
            "ACTION REQUIRED: Cadet %s appears more than once in WA file with an active registration - ignoring all registrations for now - go to WA and cancel one of the registrations please!"
            % cadet_name_from_id(cadet_id)
        )
        return iterative_process_updates_to_cadets_at_event(interface)

    existing_cadet_at_event = get_cadet_at_event_for_cadet_id(
        event=event, cadet_id=cadet_id
    )

    return process_update_to_existing_cadet_at_event(
        interface=interface,
        row_in_mapped_wa_event=relevant_row,
        existing_cadet_at_event =existing_cadet_at_event,
        event=event
    )


def process_update_to_existing_cadet_at_event(
    interface: abstractInterface,
    row_in_mapped_wa_event: RowInMappedWAEvent,
    existing_cadet_at_event: CadetAtEvent,
        event: Event
) -> Form:
    new_cadet_at_event = (
        get_cadet_at_event_from_row_in_mapped_event(
            row_in_mapped_wa_event=row_in_mapped_wa_event,
            event=event,
            cadet_id=existing_cadet_at_event.cadet_id
        )
    )

    if not any_important_difference_between_cadets_at_event(
        new_cadet_at_event = new_cadet_at_event,
        existing_cadet_at_event=existing_cadet_at_event
    ):
        ## nothing to do
        print("No change to %s" % (str(existing_cadet_at_event)))
        return iterative_process_updates_to_cadets_at_event(interface)
    else:
        print("Data has changed displaying form")
        return display_form_for_update_to_existing_cadet_at_event(
            new_cadet_at_event=new_cadet_at_event,
            existing_cadet_at_event=existing_cadet_at_event,
            event=event)


def post_form_interactively_update_cadets_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == USE_ORIGINAL_DATA_BUTTON_LABEL:
        ## nothing to do, no change to master file
        print("Using original data")
    elif last_button_pressed == USE_NEW_DATA_BUTTON_LABEL:
        print("using new data")
        update_cadets_at_event_with_new_data(interface)
    elif last_button_pressed == USE_DATA_IN_FORM_BUTTON_LABEL:
        print("Updating from form data")
        update_cadets_at_event_with_form_data(interface)

    return iterative_process_updates_to_cadets_at_event(interface)


