from typing import Union
from app.backend.cadets import get_list_of_cadets, get_cadet_from_id
from app.logic.volunteers.add_volunteer import add_volunteer_from_form_to_data
from app.logic.events.volunteer_allocation.add_volunteers_to_cadet import process_update_when_volunteer_matched

from app.logic.events.constants import *
from app.logic.events.events_in_state import get_event_from_state
from app.backend.volunteer_allocation import get_list_of_relevant_voluteers, \
    get_relevant_information_for_current_volunteer
from app.logic.events.volunteer_allocation.relevant_information import get_volunteer_from_relevant_information
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import get_current_cadet_id
from app.logic.abstract_interface import abstractInterface

from app.logic.volunteers.add_volunteer import verify_volunteer_and_warn, VolunteerAndVerificationText, get_add_volunteer_form_with_information_passed, verify_form_with_volunteer_details
from app.backend.volunteers import get_list_of_volunteers, SORT_BY_SURNAME

from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines

from app.objects.constants import arg_not_passed
from app.objects.volunteers import Volunteer

list_of_cadets = get_list_of_cadets()



#WA_VOLUNTEER_EXTRACTION_SELECTION_IN_VIEW_EVENT_STAGE
def display_form_volunteer_selection_for_cadet_at_event(interface: abstractInterface):
    relevant_information = get_relevant_information_for_current_volunteer(interface)
    volunteer = get_volunteer_from_relevant_information(relevant_information.identify)

    return get_add_or_select_existing_volunteers_form(interface=interface,
                                                      see_all_volunteers=False,
                                                      include_final_button=False,
                                                      volunteer=volunteer
                                                      )


def get_add_or_select_existing_volunteers_form(
    interface: abstractInterface,
    see_all_volunteers: bool,
    include_final_button: bool,
    volunteer: Volunteer = arg_not_passed,
) -> Form:
    print("Generating add/select volunteer form")
    print("Passed volunteer %s" % str(volunteer))
    if volunteer is arg_not_passed:
        ## Form has been filled in, this isn't our first rodeo, get from form
        volunteer_and_text = verify_form_with_volunteer_details(interface=interface)
        volunteer = volunteer_and_text.volunteer
    else:
        ## Volunteer details from WA passed through
        verification_text = verify_volunteer_and_warn(volunteer)
        volunteer_and_text = VolunteerAndVerificationText(
            volunteer=volunteer, verification_text=verification_text
        )

    cadet_id =get_current_cadet_id(interface)
    ## First time, don't include final or all cadets
    footer_buttons = get_footer_buttons_add_or_select_existing_volunteer_form(
        volunteer=volunteer,
        see_all_volunteers=see_all_volunteers,
        include_final_button=include_final_button,
        cadet_id=cadet_id
    )
    # Custom header text
    relevant_information = get_relevant_information_for_current_volunteer(interface)
    relevant_information_for_identification = relevant_information.identify

    status_text = relevant_information_for_identification.self_declared_status
    other_information = relevant_information_for_identification.any_other_information
    if len(status_text)>0:
        status_text = "Registration volunteer status %s" % status_text

    cadet = get_cadet_from_id(relevant_information_for_identification.cadet_id, list_of_cadets=list_of_cadets)
    header_text =ListOfLines([
        "Looks like a potential new volunteer in the WA entry file for cadet %s" % str(cadet),
        status_text,
        other_information,
        ". You can edit them, check their details and then add, or choose an existing volunteer instead. ",
        "(avoid creating duplicates! If the existing volunteer details are wrong, select them for now and edit later). Skip if there is no volunteer for this cadet available here."
        ])

    return get_add_volunteer_form_with_information_passed(
        volunteer_and_text=volunteer_and_text,
        footer_buttons=footer_buttons,
        header_text=header_text,
    )


def get_footer_buttons_add_or_select_existing_volunteer_form(
    volunteer:Volunteer,
        cadet_id: str,
        see_all_volunteers: bool = False, include_final_button: bool = False,

) -> ListOfLines:
    print("Get buttons for %s" % str(volunteer))
    main_buttons = get_list_of_main_buttons(include_final_button)

    volunteer_buttons = get_list_of_volunteer_buttons(
        volunteer=volunteer, see_all_volunteers=see_all_volunteers,
        cadet_id=cadet_id
    )

    return ListOfLines([main_buttons, volunteer_buttons])


def get_list_of_main_buttons(include_final_button: bool) -> Line:
    check = Button(CHECK_VOLUNTEER_BUTTON_LABEL)
    add = Button(FINAL_VOLUNTEER_ADD_BUTTON_LABEL)
    skip = Button(SKIP_VOLUNTEER_BUTTON_LABEL)

    if include_final_button:
        main_buttons = Line([check, skip, add])
    else:
        main_buttons = Line([check, skip])

    return main_buttons


def get_list_of_volunteer_buttons(volunteer: Volunteer, cadet_id: str, see_all_volunteers: bool = False) -> Line:
    if see_all_volunteers:
        list_of_volunteers = get_list_of_volunteers(SORT_BY_SURNAME)
        extra_button = SEE_SIMILAR_VOLUNTEER_ONLY_LABEL
    else:
        ## similar volunteers with option to see more
        list_of_volunteers = get_list_of_relevant_voluteers(volunteer=volunteer, cadet_id=cadet_id)

        extra_button = SEE_ALL_VOLUNTEER_BUTTON_LABEL

    all_labels = [extra_button] + list_of_volunteers

    return Line([Button(str(label)) for label in all_labels])

def get_dict_of_volunteer_names_and_volunteers():
    list_of_volunteers = get_list_of_volunteers()
    return dict([(str(volunteer), volunteer) for volunteer in list_of_volunteers])

### POST: WA_VOLUNTEER_EXTRACTION_SELECTION_IN_VIEW_EVENT_STAGE
def post_form_volunteer_selection_for_cadet_at_event(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed==CHECK_VOLUNTEER_BUTTON_LABEL or button_pressed==SEE_SIMILAR_VOLUNTEER_ONLY_LABEL:
        return get_add_or_select_existing_volunteers_form(interface=interface,
                                                          see_all_volunteers=False,
                                                          include_final_button=True
                                                          )
    elif button_pressed==FINAL_VOLUNTEER_ADD_BUTTON_LABEL:
        return action_when_new_volunteer_to_be_added(interface)
    elif button_pressed==SKIP_VOLUNTEER_BUTTON_LABEL:
        ## next volunteer
        return action_when_skipping_volunteer()

    elif button_pressed==SEE_ALL_VOLUNTEER_BUTTON_LABEL:
        return get_add_or_select_existing_volunteers_form(interface=interface,
                                                          see_all_volunteers=True,
                                                          include_final_button=True
                                                          )
    else:
        name_of_volunteer = button_pressed
        return action_when_specific_volunteer_selected(name_of_volunteer=name_of_volunteer, interface=interface)

def action_when_new_volunteer_to_be_added(interface: abstractInterface) -> Union[Form, NewForm]:
    volunteer = add_volunteer_from_form_to_data(interface)

    return action_when_volunteer_known(volunteer=volunteer, interface=interface)

def action_when_specific_volunteer_selected(name_of_volunteer: str, interface: abstractInterface) -> Union[Form, NewForm]:
    dict_of_volunteer_names_and_volunteers=get_dict_of_volunteer_names_and_volunteers()
    volunteer = dict_of_volunteer_names_and_volunteers.get(name_of_volunteer, None)
    if volunteer is None:
        raise Exception("Volunteer %s has gone missing!" % name_of_volunteer)

    return action_when_volunteer_known(volunteer=volunteer, interface=interface)

def action_when_volunteer_known(volunteer: Volunteer, interface: abstractInterface) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    cadet_id = get_current_cadet_id(interface)
    relevant_information = get_relevant_information_for_current_volunteer(interface)

    return process_update_when_volunteer_matched(volunteer=volunteer,
                                          interface=interface,
                                          event=event,
                                          cadet_id=cadet_id,
                                          relevant_information=relevant_information)

def action_when_skipping_volunteer() -> NewForm:
    return NewForm(WA_VOLUNTEER_EXTRACTION_ADD_VOLUNTEERS_TO_CADET_LOOP_IN_VIEW_EVENT_STAGE)