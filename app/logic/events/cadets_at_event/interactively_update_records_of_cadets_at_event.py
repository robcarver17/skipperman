from typing import Union
from app.OLD_backend.cadets import  cadet_name_from_id
from app.OLD_backend.wa_import.update_cadets_at_event import (
    no_important_difference_between_cadets_at_event,
    is_cadet_with_id_already_at_event,
    get_cadet_at_event_for_cadet_id,
    get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active,
    add_new_cadet_to_event,
)

from app.logic.events.cadets_at_event.track_cadet_id_in_state_when_importing import (
    get_and_save_next_cadet_id_in_event_data,
    clear_cadet_id_at_event,
)

from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.logic.events.constants import (
    USE_ORIGINAL_DATA_BUTTON_LABEL,
    USE_NEW_DATA_BUTTON_LABEL,
    USE_DATA_IN_FORM_BUTTON_LABEL,
)

from app.logic.shared.events_state import get_event_from_state

from app.logic.events.cadets_at_event.update_existing_cadet_at_event_forms import (
    display_form_for_update_to_existing_cadet_at_event,
)
from app.logic.events.cadets_at_event.update_existing_cadet_at_event_from_form_entries import (
    update_cadets_at_event_with_new_data,
    update_cadets_at_event_with_form_data,
)
from app.objects.primtive_with_id.cadet_with_id_at_event import (
    CadetWithIdAtEvent,
    get_cadet_at_event_from_row_in_mapped_event,
)

from app.objects.events import Event
from app.objects.exceptions import NoMoreData, DuplicateCadets
from app.objects.mapped_wa_event import RowInMappedWAEvent


def display_form_interactively_update_cadets_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## rest of the time is a post call

    clear_cadet_id_at_event(interface)

    return process_next_cadet_at_event(interface)


def process_next_cadet_at_event(interface: abstractInterface) -> Union[Form, NewForm]:
    print("Looping through updating delta data")
    event = get_event_from_state(interface)

    try:
        cadet_id = get_and_save_next_cadet_id_in_event_data(interface)
    except NoMoreData:
        print("Finished looping")
        clear_cadet_id_at_event(interface)
        return finished_looping_return_to_controller(interface)

    print("Current cadet id is %s" % cadet_id)

    return process_update_to_cadet_data(
        interface=interface, event=event, cadet_id=cadet_id
    )


def process_update_to_cadet_data(
    interface: abstractInterface, event: Event, cadet_id: str
) -> Form:
    cadet_already_at_event = is_cadet_with_id_already_at_event(
        interface=interface, event=event, cadet_id=cadet_id
    )

    print("STATUS: ID %s already at event %s" % (cadet_id, str(cadet_already_at_event)))
    if cadet_already_at_event:
        return process_update_to_existing_cadet_in_event_data(
            event=event, cadet_id=cadet_id, interface=interface
        )
    else:
        return process_update_to_cadet_new_to_event(
            event=event, cadet_id=cadet_id, interface=interface
        )


def process_update_to_cadet_new_to_event(
    interface: abstractInterface, event: Event, cadet_id: str
) -> Form:
    print("New row in master data for cadet with id %s" % cadet_id)

    try:
        relevant_row = get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(
            interface=interface,
            cadet_id=cadet_id,
            event=event,
            raise_error_on_duplicate=True,
        )
    except DuplicateCadets:
        interface.log_error(
            "ACTION REQUIRED: Cadet %s appears more than once in WA file with an active registration - using the first registration found - go to WA and cancel all but one of the registrations please, and then check details here are correct!"
            % cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id)
        )
        relevant_row = get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(
            interface=interface,
            cadet_id=cadet_id,
            event=event,
            raise_error_on_duplicate=False,  ## try again this time allowing duplicates
        )
    except NoMoreData:
        interface.log_error(
            "ACTION REQUIRED: Cadet %s vanished from WA mapping file - contact support"
            % cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id)

        )
        return process_next_cadet_at_event(interface)

    add_new_cadet_to_event(
        interface=interface,
        event=event,
        row_in_mapped_wa_event=relevant_row,
        cadet_id=cadet_id,
    )
    interface.flush_cache_to_store()

    return process_next_cadet_at_event(interface)


def process_update_to_existing_cadet_in_event_data(
    interface: abstractInterface, event: Event, cadet_id: str
) -> Form:
    try:
        relevant_row = get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(
            interface=interface,
            cadet_id=cadet_id,
            event=event,
            raise_error_on_duplicate=True,
        )
    except DuplicateCadets:
        interface.log_error(
            "ACTION REQUIRED: Cadet %s appears more than once in WA file with multiple active registrations - ignoring any possible changes made to registration - go to WA and cancel one of the registrations please!"
            % cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id)
        )
        return process_next_cadet_at_event(interface)
    except NoMoreData:
        ## No rows match cadet ID, so deleted
        interface.log_error(
            "Cadet %s was in WA event data, now appears to be missing in latest file - possible data corruption of WA output or manual hacking - no WA changes will be reflected in data"
            % cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id)
        )
        return process_next_cadet_at_event(interface)

    existing_cadet_at_event = get_cadet_at_event_for_cadet_id(
        interface=interface, event=event, cadet_id=cadet_id
    )

    return process_update_to_existing_cadet_at_event(
        interface=interface,
        row_in_mapped_wa_event=relevant_row,
        existing_cadet_at_event=existing_cadet_at_event,
        event=event,
    )


def process_update_to_existing_cadet_at_event(
    interface: abstractInterface,
    row_in_mapped_wa_event: RowInMappedWAEvent,
    existing_cadet_at_event: CadetWithIdAtEvent,
    event: Event,
) -> Form:
    new_cadet_at_event = get_cadet_at_event_from_row_in_mapped_event(
        row_in_mapped_wa_event=row_in_mapped_wa_event,
        event=event,
        cadet_id=existing_cadet_at_event.cadet_id,
    )

    if no_important_difference_between_cadets_at_event(
        new_cadet_at_event=new_cadet_at_event,
        existing_cadet_at_event=existing_cadet_at_event,
    ):
        ## nothing to do
        return process_next_cadet_at_event(interface)
    else:
        return display_form_for_update_to_existing_cadet_at_event(
            interface=interface,
            new_cadet_at_event=new_cadet_at_event,
            existing_cadet_at_event=existing_cadet_at_event,
            event=event,
        )


def post_form_interactively_update_cadets_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == USE_ORIGINAL_DATA_BUTTON_LABEL:
        ## nothing to do, no change to master file
        print("Using original data - doing nothing")
    elif last_button_pressed == USE_NEW_DATA_BUTTON_LABEL:
        print("using new data")
        update_cadets_at_event_with_new_data(interface)
    elif last_button_pressed == USE_DATA_IN_FORM_BUTTON_LABEL:
        print("Updating from form data")
        update_cadets_at_event_with_form_data(interface)

    return process_next_cadet_at_event(interface)


def finished_looping_return_to_controller(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_form_interactively_update_cadets_at_event
    )
