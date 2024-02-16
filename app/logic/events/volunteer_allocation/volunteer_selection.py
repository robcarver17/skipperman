
from typing import Union

from app.backend.volunteers.volunteer_allocation import add_identified_volunteer, mark_volunteer_as_skipped
from app.logic.events.import_wa.shared_state_tracking_and_data import get_current_row_id
from app.logic.events.volunteer_allocation.volunteer_selection_form_contents import \
    get_header_text_for_volunteer_selection_form, get_footer_buttons_add_or_select_existing_volunteer_form, \
    get_dict_of_volunteer_names_and_volunteers, volunteer_name_is_similar_to_cadet_name
from app.logic.volunteers.add_volunteer import add_volunteer_from_form_to_data


from app.logic.events.constants import *
from app.logic.events.events_in_state import get_event_from_state
from app.backend.volunteers.volunter_relevant_information import get_volunteer_from_relevant_information
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import \
    get_relevant_information_for_current_volunteer, get_volunteer_index
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.logic.volunteers.add_volunteer import VolunteerAndVerificationText, get_add_volunteer_form_with_information_passed, verify_form_with_volunteer_details
from app.backend.volunteers.volunteers import verify_volunteer_and_warn

from app.objects.abstract_objects.abstract_form import Form, NewForm

from app.objects.constants import arg_not_passed
from app.objects.events import Event
from app.objects.volunteers import Volunteer


#WA_VOLUNTEER_IDENTIFICATION_SELECTION_IN_VIEW_EVENT_STAGE
def display_form_volunteer_selection_at_event(interface: abstractInterface):
    relevant_information = get_relevant_information_for_current_volunteer(interface)
    volunteer = get_volunteer_from_relevant_information(relevant_information.identify)

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
        verification_text = verify_volunteer_and_warn(volunteer)
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


### POST: WA_VOLUNTEER_IDENTIFICATION_SELECTION_IN_VIEW_EVENT_STAGE
def post_form_volunteer_selection(interface: abstractInterface) -> Union[Form, NewForm]:
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

    return action_when_volunteer_known(volunteer=volunteer, interface=interface)


def action_when_skipping_volunteer(interface: abstractInterface) -> NewForm:
    event = get_event_from_state(interface)
    current_row_id = get_current_row_id(interface)
    current_index = get_volunteer_index(interface)

    mark_volunteer_as_skipped(
        event=event,
        row_id=current_row_id,
        volunteer_index=int(current_index))

    return next_volunteer_in_row(interface)



def action_when_specific_volunteer_selected(name_of_volunteer: str, interface: abstractInterface) -> Union[Form, NewForm]:
    dict_of_volunteer_names_and_volunteers= get_dict_of_volunteer_names_and_volunteers()
    volunteer = dict_of_volunteer_names_and_volunteers.get(name_of_volunteer, None)
    if volunteer is None:
        raise Exception("Volunteer %s has gone missing!" % name_of_volunteer)

    return action_when_volunteer_known(volunteer=volunteer, interface=interface)

def action_when_volunteer_known(volunteer: Volunteer, interface: abstractInterface) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    current_row_id = get_current_row_id(interface)
    current_index =  get_volunteer_index(interface)

    print("Adding volunteer %s as identified for event %s" % (str(volunteer), str(event)))
    add_identified_volunteer(volunteer_id=volunteer.id,
                                event=event,
                                row_id = current_row_id,
                             volunteer_index = int(current_index))


    return next_volunteer_in_row(interface)

def next_volunteer_in_row(interface:abstractInterface)-> NewForm:
    return interface.get_new_display_form_for_parent_of_function(display_form_volunteer_selection_at_event)




