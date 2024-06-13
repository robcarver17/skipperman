
from app.backend.clothing import is_cadet_with_id_already_at_event_with_clothing, add_new_cadet_with_clothing_to_event

from app.backend.cadets import  cadet_name_from_id
from app.backend.wa_import.update_cadets_at_event import get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active, \
    list_of_cadet_ids_at_event_and_in_mapped_data_for_event

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
):
    ## rest of the time is a post call

    event =get_event_from_state(interface)
    list_of_ids = list_of_cadet_ids_at_event_and_in_mapped_data_for_event(event=event, interface=interface, include_mapped_data=False)

    for cadet_id in list_of_ids:
        process_update_to_cadet_clothing_data(interface=interface, event=event, cadet_id=cadet_id)



def process_update_to_cadet_clothing_data(
    interface: abstractInterface, event: Event, cadet_id: str
):
    cadet_already_at_event = is_cadet_with_id_already_at_event_with_clothing(
        interface=interface,
        event=event, cadet_id=cadet_id
    )

    if cadet_already_at_event:
        return

    else:
        return process_update_to_cadet_new_to_event_with_clothing(
            event=event, cadet_id=cadet_id, interface=interface
        )



def process_update_to_cadet_new_to_event_with_clothing(
        interface: abstractInterface, event: Event, cadet_id: str
):

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
        return

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
            cadet_id: str):

    clothing_size_from_registration = relevant_row.get_item(CADET_T_SHIRT_SIZE, '')
    add_new_cadet_with_clothing_to_event(interface=interface, event=event, cadet_id=cadet_id, size=clothing_size_from_registration)
    interface._DONT_CALL_DIRECTLY_USE_FLUSH_save_stored_items()
    interface.log_error("Added clothing for cadet %s" % cadet_name_from_id(interface=interface, cadet_id=cadet_id))

