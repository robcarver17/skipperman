from typing import Union

from app.backend.data.volunteers import DEPRECATED_get_sorted_list_of_volunteers
from app.backend.volunteers.volunteer_allocation import add_identified_volunteer, mark_volunteer_as_skipped, \
    volunteer_for_this_row_and_index_already_identified
from app.backend.volunteers.volunteers import DEPRECATE_verify_volunteer_and_warn
from app.backend.volunteers.volunter_relevant_information import get_volunteer_from_relevant_information, \
    no_volunteer_in_position_at_form

from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.import_wa.shared_state_tracking_and_data import get_and_save_next_row_id_in_mapped_event_data, \
    clear_row_in_state, get_current_row_id
from app.logic.events.volunteer_allocation.add_volunteers_to_event import \
    display_add_volunteers_to_event
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import clear_volunteer_index, \
    get_and_save_next_volunteer_index, get_relevant_information_for_current_volunteer, get_volunteer_index
from app.logic.events.volunteer_allocation.volunteer_selection_form_contents import \
    volunteer_name_is_similar_to_cadet_name, get_footer_buttons_add_or_select_existing_volunteer_form, \
    get_header_text_for_volunteer_selection_form, DEPRECATE_get_dict_of_volunteer_names_and_volunteers
from app.logic.volunteers.add_volunteer import verify_form_with_volunteer_details, VolunteerAndVerificationText, \
    get_add_volunteer_form_with_information_passed, add_volunteer_from_form_to_data
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

from app.logic.events.constants import *

from app.objects.constants import NoMoreData, missing_data, arg_not_passed
from app.objects.relevant_information_for_volunteers import missing_relevant_information
from app.objects.volunteers import Volunteer


### First pass- loop over mapped data and identify volunteers
### Identified volunteer data object with row_id (include row data, volunteer index)


def display_form_volunteer_identification(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## this only happens once, the rest of the time is a post call
    print("Reset volunteer row ID")
    clear_row_in_state(interface)

    return process_volunteer_on_next_row_of_event_data(interface)

def process_volunteer_on_next_row_of_event_data(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    print("Looping through identifying master event data volunteers")
    try:
        get_and_save_next_row_id_in_mapped_event_data(interface)
    except NoMoreData:
        clear_row_in_state(interface)
        print("Finished looping - next stage is to add details")
        return goto_add_identified_volunteers_to_event(interface)

    return identify_volunteers_in_specific_row_initialise(interface=interface)



def identify_volunteers_in_specific_row_initialise(interface: abstractInterface) -> NewForm:
    print("Clearing volunteer index")
    clear_volunteer_index(interface)
    return next_volunteer_in_current_row(interface)


def next_volunteer_in_current_row(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        print("next volunteer index")
        get_and_save_next_volunteer_index(interface)
    except NoMoreData:
        clear_volunteer_index(interface)
        return process_volunteer_on_next_row_of_event_data(interface)

    if current_volunteer_already_identified(interface):
        return next_volunteer_in_current_row(interface)
    else:
        return add_specific_volunteer_at_event(interface=interface)

def current_volunteer_already_identified(interface: abstractInterface):
    current_row_id = get_current_row_id(interface)
    current_index =  get_volunteer_index(interface)
    event = get_event_from_state(interface)

    return volunteer_for_this_row_and_index_already_identified(event=event, row_id=current_row_id, volunteer_index=current_index)


def add_specific_volunteer_at_event(interface: abstractInterface)-> Union[Form,NewForm]:
    relevant_information = get_relevant_information_for_current_volunteer(interface)
    volunteer = get_volunteer_from_relevant_information(relevant_information)
    if volunteer is missing_relevant_information:
        return next_volunteer_in_current_row(interface)

    return add_passed_volunteer_at_event(interface=interface, volunteer=volunteer)

def add_passed_volunteer_at_event(interface: abstractInterface, volunteer: Volunteer) -> Union[Form, NewForm]:

    list_of_volunteers = DEPRECATED_get_sorted_list_of_volunteers()
    matched_volunteer_with_id = list_of_volunteers.matching_volunteer(volunteer)

    if matched_volunteer_with_id is missing_data:
        print("Volunteer %s not matched" % str(volunteer))
        return display_volunteer_selection_form(interface=interface, volunteer=volunteer)

    print("Volunteer %s matched id is %s" % (str(volunteer), matched_volunteer_with_id.id))
    return process_identification_when_volunteer_matched(
        interface=interface, volunteer = matched_volunteer_with_id
    )


def process_identification_when_volunteer_matched(interface: abstractInterface, volunteer: Volunteer) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    current_row_id = get_current_row_id(interface)
    current_index =  get_volunteer_index(interface)

    print("Adding volunteer %s as identified for event %s, row_id %s, volunteer index %d" % (str(volunteer), str(event), current_row_id, current_index))
    add_identified_volunteer(volunteer_id=volunteer.id,
                                event=event,
                                row_id = current_row_id,
                             volunteer_index = int(current_index))


    return next_volunteer_in_current_row(interface)

def display_volunteer_selection_form(interface: abstractInterface, volunteer: Volunteer):
    return get_add_or_select_existing_volunteers_form(interface=interface,
                                                                        see_all_volunteers=False,
                                                                        first_time= True,
                                                                        volunteer=volunteer
                                                                        )



def get_add_or_select_existing_volunteers_form(
    interface: abstractInterface,
    see_all_volunteers: bool,
    first_time: bool,
    volunteer: Volunteer = arg_not_passed,

) -> Form:
    print("Generating add/select volunteer form")
    print("Passed volunteer %s" % str(volunteer))
    if volunteer is arg_not_passed:
        ## Form has been filled in, this isn't our first rodeo, get from form
        volunteer_and_text = verify_form_with_volunteer_details(interface=interface)
        volunteer = volunteer_and_text.volunteer
        include_final_button = True
    else:
        ## Volunteer details from WA passed through
        verification_text = DEPRECATE_verify_volunteer_and_warn(volunteer)
        volunteer_and_text = VolunteerAndVerificationText(
            volunteer=volunteer, verification_text=verification_text
        )
        could_be_cadet_not_volunteer = (
            volunteer_name_is_similar_to_cadet_name(interface=interface, volunteer=volunteer))

        verification_issues = len(verification_text) > 0

        if could_be_cadet_not_volunteer or verification_issues:
            if first_time:
                include_final_button = False
            else:
                include_final_button = True
        else:
            include_final_button = True

    cadet_id = get_cadet_id_or_missing_data_for_current_row(interface)
    ## First time, don't include final or all group_allocations
    footer_buttons = get_footer_buttons_add_or_select_existing_volunteer_form(
        volunteer=volunteer,
        see_all_volunteers=see_all_volunteers,
        include_final_button=include_final_button,
        cadet_id=cadet_id,
    )
    header_text = get_header_text_for_volunteer_selection_form(interface=interface,
                                                               volunteer=volunteer)

    return get_add_volunteer_form_with_information_passed(
        volunteer_and_text=volunteer_and_text,
        footer_buttons=footer_buttons,
        header_text=header_text,
    )


def get_cadet_id_or_missing_data_for_current_row(interface: abstractInterface):
    relevant_information = get_relevant_information_for_current_volunteer(interface)

    return relevant_information.identify.cadet_id


def post_form_volunteer_identification(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed in[CHECK_FOR_ME_VOLUNTEER_BUTTON_LABEL, CONFIRM_CHECKED_VOLUNTEER_BUTTON_LABEL, SEE_SIMILAR_VOLUNTEER_ONLY_LABEL]:
        return get_add_or_select_existing_volunteers_form(interface=interface,
                                                                            see_all_volunteers=False,
                                                                            first_time=False
                                                                            )
    elif button_pressed==FINAL_VOLUNTEER_ADD_BUTTON_LABEL:
        return action_when_new_volunteer_to_be_added(interface)

    elif button_pressed==SKIP_VOLUNTEER_BUTTON_LABEL:
        ## next volunteer
        return action_when_skipping_volunteer(interface)

    elif button_pressed==SEE_ALL_VOLUNTEER_BUTTON_LABEL:
        return get_add_or_select_existing_volunteers_form(interface=interface,
                                                                            see_all_volunteers=True,
                                                                            first_time=False
                                                                            )
    else:
        name_of_volunteer = button_pressed
        return action_when_specific_volunteer_selected(name_of_volunteer=name_of_volunteer, interface=interface)


def action_when_new_volunteer_to_be_added(interface: abstractInterface) -> Union[Form, NewForm]:
    volunteer = add_volunteer_from_form_to_data(interface)

    return process_identification_when_volunteer_matched(interface=interface, volunteer=volunteer)


def action_when_skipping_volunteer(interface: abstractInterface) -> NewForm:
    event = get_event_from_state(interface)
    current_row_id = get_current_row_id(interface)
    current_index = get_volunteer_index(interface)

    print("Skipping volunteer row %s id %d as identified for event %s" % (str(current_row_id), current_index, str(event)))

    mark_volunteer_as_skipped(
        event=event,
        row_id=current_row_id,
        volunteer_index=int(current_index))

    return  next_volunteer_in_current_row(interface)


def action_when_specific_volunteer_selected(name_of_volunteer: str, interface: abstractInterface) -> Union[Form, NewForm]:
    dict_of_volunteer_names_and_volunteers= DEPRECATE_get_dict_of_volunteer_names_and_volunteers()
    volunteer = dict_of_volunteer_names_and_volunteers.get(name_of_volunteer, None)
    if volunteer is None:
        raise Exception("Volunteer %s has gone missing!" % name_of_volunteer)

    return process_identification_when_volunteer_matched(interface=interface, volunteer=volunteer)







def goto_add_identified_volunteers_to_event(interface: abstractInterface)-> NewForm:
    return interface.get_new_form_given_function(display_add_volunteers_to_event)


