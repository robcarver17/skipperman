from typing import Union

from app.backend.merch import is_cadet_with_id_already_at_event_with_clothing, add_new_cadet_with_clothing_to_event

from app.backend.cadets import  cadet_name_from_id
from app.backend.wa_import.update_cadets_at_event import        get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active

from app.logic.events.cadets_at_event.track_cadet_id_in_state_when_importing import \
    get_and_save_next_cadet_id_in_event_data, clear_cadet_id_at_event
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.data_access.configuration.field_list import CADET_T_SHIRT_SIZE
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

from app.logic.events.events_in_state import get_event_from_state


from app.objects.events import Event
from app.objects.constants import NoMoreData, DuplicateCadets
from app.objects.mapped_wa_event import RowInMappedWAEvent


def update_cadet_clothing_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## rest of the time is a post call

    clear_cadet_id_at_event(interface)

    return process_next_cadet_clothing_at_event(interface)


def process_next_cadet_clothing_at_event(
    interface: abstractInterface
) -> Union[Form, NewForm]:

    event = get_event_from_state(interface)

    try:
        cadet_id = get_and_save_next_cadet_id_in_event_data(interface)
    except NoMoreData:
        clear_cadet_id_at_event(interface)
        return finished_looping_return_to_controller(interface)

    print("Current cadet id is %s" % cadet_id)

    return process_update_to_cadet_clothing_data(
        interface=interface, event=event, cadet_id=cadet_id
    )



def process_update_to_cadet_clothing_data(
    interface: abstractInterface, event: Event, cadet_id: str
) -> Form:
    cadet_already_at_event = is_cadet_with_id_already_at_event_with_clothing(
        interface=interface,
        event=event, cadet_id=cadet_id
    )

    print("STATUS: ID %s already at event %s" % (cadet_id, str(cadet_already_at_event)))
    if cadet_already_at_event:
        ## WE DON'T DELETE clothing IF A CADET IS UPDATED AND EG CANCELLED
        ## INSTEAD WE MASK clothing WITH REGISTRATION DETAILS
        ## SO NO ACTION REQUIRED FOR EXISTING CADETS
        return process_next_cadet_clothing_at_event(interface)

    else:
        return process_update_to_cadet_new_to_event_with_clothing(
            event=event, cadet_id=cadet_id, interface=interface
        )



def process_update_to_cadet_new_to_event_with_clothing(
        interface: abstractInterface, event: Event, cadet_id: str
) -> Form:

    print("New row in master data for cadet with id %s" % cadet_id)

    try:
        relevant_row = get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(
            interface=interface,
            cadet_id=cadet_id, event=event,
            raise_error_on_duplicate=True
        )
    except DuplicateCadets:
        interface.log_error(
            "ACTION REQUIRED: Cadet %s appears more than once in WA file with an active registration - using the first registration found - go to WA and cancel all but one of the registrations please, and then check details here are correct!"
            % cadet_name_from_id(cadet_id=cadet_id, interface=interface)
        )
        relevant_row = get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(
            interface=interface,
            cadet_id=cadet_id, event=event,
            raise_error_on_duplicate=False ## try again this time allowing duplicates
        )
    except NoMoreData:
        interface.log_error(
            "ACTION REQUIRED: Cadet %s vanished from WA mapping file - contact support"
            % cadet_name_from_id(cadet_id=cadet_id, interface=interface)
        )
        return process_next_cadet_clothing_at_event(interface)

    return process_new_cadet_clothing_requirements(
        interface=interface,
        event=event,
        relevant_row=relevant_row,
        cadet_id=cadet_id
    )


def process_new_cadet_clothing_requirements(
        interface: abstractInterface,
        relevant_row: RowInMappedWAEvent,
                                                       event: Event,
            cadet_id: str) -> Form:

    clothing_size_from_registration = relevant_row.get_item(CADET_T_SHIRT_SIZE, '')
    add_new_cadet_with_clothing_to_event(interface=interface, event=event, cadet_id=cadet_id, size=clothing_size_from_registration)
    interface.save_stored_items()

    return process_next_cadet_clothing_at_event(interface)


def finished_looping_return_to_controller(interface: abstractInterface)-> NewForm:
    ## works even if no volunteers at event
    return interface.get_new_display_form_for_parent_of_function(update_cadet_clothing_at_event)

def post_update_cadet_clothing_at_event_SHOULD_NEVER_BE_CALLED(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## rest of the time is a post call

    raise
