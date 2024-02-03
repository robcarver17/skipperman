from typing import Union
from app.backend.volunteers.volunteer_allocation import any_volunteers_at_event_for_cadet, \
    have_volunteers_been_processed_at_event_for_cadet
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import get_and_save_next_cadet_id, \
    reset_current_cadet_id_store
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.logic.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,

)

from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.constants import *
from app.backend.wa_import.update_master_event_data import get_row_in_master_event_for_cadet_id

from app.objects.events import Event
from app.objects.constants import NoMoreData
from app.objects.mapped_wa_event_with_ids import deleted_status, cancelled_status


def display_form_volunteer_extraction_from_master_records_initalise_loop(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## this only happens once, the rest of the time is a post call
    reset_current_cadet_id_store(interface)

    return display_form_volunteer_extraction_from_master_records_looping(interface)


# WA_VOLUNTEER_EXTRACTION_LOOP_IN_VIEW_EVENT_STAGE
def display_form_volunteer_extraction_from_master_records_looping(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    print("Looping through updating master event data volunteers")

    event = get_event_from_state(interface)

    try:
        cadet_id = get_and_save_next_cadet_id(interface)
    except NoMoreData:
        print("Finished looping")
        return form_with_message_and_finished_button(
            "Finished importing WA data", interface=interface,
            set_stage_name_to_go_to_on_button_press=VIEW_EVENT_STAGE
        )

    print("Current cadet id is %s" % cadet_id)

    return process_volunteer_updates_for_cadet_in_event_data(
        interface=interface, event=event, cadet_id=cadet_id
    )


def process_volunteer_updates_for_cadet_in_event_data(
    interface: abstractInterface, event: Event, cadet_id: str
) -> Form:

    row_in_master_event = get_row_in_master_event_for_cadet_id(
        event=event, cadet_id=cadet_id
    )
    if row_in_master_event.status in [deleted_status, cancelled_status]:
        return iterative_process_volunteer_updates_to_master_event_data_when_cadet_deleted_or_cancelled(
            event=event,
            cadet_id=cadet_id,
            interface=interface
        )
    else:
        return iterative_process_volunteer_updates_to_master_event_data_when_cadet_is_active(
            event=event,
            cadet_id=cadet_id,
            interface=interface
        )



def iterative_process_volunteer_updates_to_master_event_data_when_cadet_deleted_or_cancelled(event: Event, cadet_id: str, interface: abstractInterface)-> Union[Form, NewForm]:
    if any_volunteers_at_event_for_cadet(event=event, cadet_id=cadet_id):
        return NewForm(WA_VOLUNTEER_EXTRACTION_MISSING_CADET_IN_VIEW_EVENT_STAGE)
    else:
        ## fine move on, next volunteer
        return display_form_volunteer_extraction_from_master_records_looping(interface)


def iterative_process_volunteer_updates_to_master_event_data_when_cadet_is_active(event: Event, cadet_id: str, interface: abstractInterface)-> Union[Form, NewForm]:
    volunteers_already_applied_to_cadet = have_volunteers_been_processed_at_event_for_cadet(event=event, cadet_id=cadet_id)
    if volunteers_already_applied_to_cadet:
        ## fine move on, next cadet
        return display_form_volunteer_extraction_from_master_records_looping(interface)
    else:
        ## required to ensure we begin from VOLUNTEER1, then go to VOLUNTEER2
        return NewForm(WA_VOLUNTEER_EXTRACTION_ADD_VOLUNTEERS_TO_CADET_INIT_IN_VIEW_EVENT_STAGE)


def post_form_volunteer_extraction_initialise_from_master_records(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    interface.log_error("Post form should not be reached - contact support")

    return form_with_message_and_finished_button("Post form should not be reached - contact support", interface=interface)

def post_form_volunteer_extraction_from_master_records_looping(
            interface: abstractInterface,
    ) -> Union[Form, NewForm]:
        interface.log_error("Post form should not be reached - contact support")
        return form_with_message_and_finished_button("Post form should not be reached - contact support",
                                                     interface=interface)


