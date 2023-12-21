from typing import Union
from app.logic.events.volunteer_allocation.backend import any_volunteers_in_data_excluding_no_volunteer, \
    any_volunteers_in_data_including_no_volunteer, get_and_save_next_cadet_id, reset_current_cadet_id_store, \
    clear_volunteer_index
from app.logic.events.volunteer_allocation.volunteer_selection import \
    process_volunteer_updates_to_master_event_data_when_cadet_is_active_and_has_no_existing_volunteers

from app.logic.forms_and_interfaces.abstract_form import Form, NewForm
from app.logic.forms_and_interfaces.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)

from app.logic.events.utilities import get_event_from_state
from app.logic.events.constants import *
from app.logic.events.import_wa.update_existing_master_event_data_forms import (
    get_row_in_master_event_for_cadet_id,
)

from app.objects.events import Event
from app.objects.constants import NoMoreData
from app.objects.mapped_wa_event_with_ids import deleted_status, cancelled_status


def display_form_volunteer_extraction_from_master_records(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## this only happens once, the rest of the time is a post call
    reset_current_cadet_id_store(interface)

    return iterative_process_volunteer_updates_to_master_event_data(interface)


def iterative_process_volunteer_updates_to_master_event_data(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    print("Looping through updating master event data volunteers")

    event = get_event_from_state(interface)

    try:
        cadet_id = get_and_save_next_cadet_id(interface)
    except NoMoreData:
        print("Finished looping")
        return form_with_message_and_finished_button(
            "Finished importing WA data", interface=interface
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



def iterative_process_volunteer_updates_to_master_event_data_when_cadet_deleted_or_cancelled(event: Event, cadet_id: str, interface: abstractInterface)-> Form:
    if any_volunteers_in_data_excluding_no_volunteer(event=event, cadet_id=cadet_id):
        return process_volunteer_updates_to_master_event_data_when_cadet_deleted_or_cancelled_and_volunteers_exist(event=event,
                                                                                                                   cadet_id=cadet_id,
                                                                                                                   interface=interface)
    else:
        ## fine move on, next volunteer
        return iterative_process_volunteer_updates_to_master_event_data(interface)


def process_volunteer_updates_to_master_event_data_when_cadet_deleted_or_cancelled_and_volunteers_exist(event: Event, cadet_id: str, interface: abstractInterface)-> Form:
    #  check to see if VOLUNTEERS are still available ( USE checkboxes - POST Form will need to distinguish between this and add volunteer)
    pass

def iterative_process_volunteer_updates_to_master_event_data_when_cadet_is_active(event: Event, cadet_id: str, interface: abstractInterface)-> Form:
    volunteers_already_applied_to_cadet = any_volunteers_in_data_including_no_volunteer(event=event, cadet_id=cadet_id)
    if volunteers_already_applied_to_cadet:
        ## fine move on, next cadet
        return iterative_process_volunteer_updates_to_master_event_data(interface)
    else:
        ## required to ensure we begin from VOLUNTEER1, then go to VOLUNTEER2
        clear_volunteer_index(interface)
        return process_volunteer_updates_to_master_event_data_when_cadet_is_active_and_has_no_existing_volunteers(
            event=event,
            cadet_id=cadet_id,
            interface=interface
        )


def post_form_volunteer_extraction_from_master_records(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    last_button_pressed = interface.last_button_pressed()

    ### COULD BE CHECKBOXES FOR EXISTING VOLUNTEERS REQUIRING DELETE

    ## OR IF CADETS WITHOUT VOLUNTEERS THEN:

    ## Similar volunteers button
    ## Add volunteer button
    ## SWITCH to show all volunteers

    ## When a volunteer is done, associate with relevant cadet
    ## Process availability (requires another form?)
    ## WHERE IS FOOD STORED?

    """
    CHECK_VOLUNTEER_BUTTON_LABEL = "Check volunteer details entered"
    FINAL_VOLUNTEER_ADD_BUTTON_LABEL = "Yes - these details are correct - add this new volunteer"
    SEE_ALL_VOLUNTEER_BUTTON_LABEL = "Choose from all existing volunteers"
    SEE_SIMILAR_VOLUNTEER_ONLY_LABEL = "See similar volunteers only"
    SKIP_VOLUNTEER_BUTTON_LABEL = "Skip - no volunteer to add for this cadet"
    """

    return iterative_process_volunteer_updates_to_master_event_data(interface)

buttons_relating_to_add_volunteer = [CHECK_VOLUNTEER_BUTTON_LABEL, FINAL_VOLUNTEER_ADD_BUTTON_LABEL,
                                     SEE_ALL_VOLUNTEER_BUTTON_LABEL, SKIP_VOLUNTEER_BUTTON_LABEL,
                                     SEE_SIMILAR_VOLUNTEER_ONLY_LABEL]
