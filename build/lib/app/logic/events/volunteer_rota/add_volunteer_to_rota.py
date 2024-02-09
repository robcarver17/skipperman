from copy import copy
from typing import Union

from app.backend.data.volunteers import SORT_BY_FIRSTNAME, get_sorted_list_of_volunteers
from app.backend.data.volunteer_allocation import get_list_of_volunteers_at_event, add_volunteer_to_event_with_just_id
from app.logic.abstract_interface import abstractInterface
from app.logic.events.constants import *
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_allocation.volunteer_selection_form_contents import \
    get_dict_of_volunteer_names_and_volunteers
from app.logic.volunteers.add_volunteer import verify_form_with_volunteer_details, VolunteerAndVerificationText, \
    get_add_volunteer_form_with_information_passed, add_volunteer_from_form_to_data
from app.objects.abstract_objects.abstract_buttons import Button, BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.events import Event
from app.objects.volunteers import Volunteer, default_volunteer



def display_form_add_new_volunteer_to_rota_at_event(interface: abstractInterface) -> Union[Form, NewForm]:
    return get_add_or_select_existing_volunteers_form_in_volunteer_rota(
        interface=interface,
        first_time_display=True
    )

def get_add_or_select_existing_volunteers_form_in_volunteer_rota(
    interface: abstractInterface,
    first_time_display: bool = True
) -> Form:
    if first_time_display:
        ## Blank form
        volunteer_and_text = VolunteerAndVerificationText(volunteer=default_volunteer, verification_text="")
        include_final_button = False
    else:
        ## Form has been filled in, this isn't our first rodeo, get from form
        volunteer_and_text = verify_form_with_volunteer_details(interface=interface)
        include_final_button = True

    event = get_event_from_state(interface)
    footer_buttons = get_footer_buttons_add_or_select_existing_volunteer_for_rota(
        include_final_button=include_final_button,
        event=event
    )
    header_text = ListOfLines(["Enter the details of a new volunteer to be added, or select an existing volunteer"])

    return get_add_volunteer_form_with_information_passed(
        volunteer_and_text=volunteer_and_text,
        footer_buttons=footer_buttons,
        header_text=header_text,
    )


def post_form_add_new_volunteer_to_rota_at_event(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed==CHECK_VOLUNTEER_BUTTON_LABEL:
        return get_add_or_select_existing_volunteers_form_in_volunteer_rota(interface=interface,
                                                                            first_time_display=False
                                                                            )
    elif button_pressed==FINAL_VOLUNTEER_ADD_BUTTON_LABEL:
        return action_when_new_volunteer_to_be_added_from_rota(interface)
    elif button_pressed==BACK_BUTTON_LABEL:
        return NewForm(EDIT_VOLUNTEER_ROTA_EVENT_STAGE)
    else:
        name_of_volunteer = button_pressed
        return action_when_specific_volunteer_selected_for_rota(name_of_volunteer=name_of_volunteer, interface=interface)


def action_when_new_volunteer_to_be_added_from_rota(interface: abstractInterface) -> Union[Form, NewForm]:
    volunteer = add_volunteer_from_form_to_data(interface)

    return action_when_volunteer_known_for_rota(volunteer=volunteer, interface=interface)


def action_when_specific_volunteer_selected_for_rota(name_of_volunteer: str, interface: abstractInterface) -> Union[Form, NewForm]:
    dict_of_volunteer_names_and_volunteers= get_dict_of_volunteer_names_and_volunteers()
    volunteer = dict_of_volunteer_names_and_volunteers.get(name_of_volunteer, None)
    if volunteer is None:
        raise Exception("Volunteer %s has gone missing!" % name_of_volunteer)

    return action_when_volunteer_known_for_rota(volunteer=volunteer, interface=interface)


def action_when_volunteer_known_for_rota(volunteer: Volunteer, interface: abstractInterface) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    add_volunteer_to_event_with_just_id(volunteer_id=volunteer.id, event_id=event.id)

    return NewForm(EDIT_VOLUNTEER_ROTA_EVENT_STAGE)

def get_footer_buttons_add_or_select_existing_volunteer_for_rota(
        event: Event,
    include_final_button: bool = False,

) -> ListOfLines:
    main_buttons = get_list_of_main_buttons_in_rota(include_final_button)

    volunteer_buttons = get_list_of_volunteer_buttons_in_rota(event
    )

    return ListOfLines([main_buttons, volunteer_buttons])


def get_list_of_main_buttons_in_rota(include_final_button: bool) -> Line:
    check = Button(CHECK_VOLUNTEER_BUTTON_LABEL)
    add = Button(FINAL_VOLUNTEER_ADD_BUTTON_LABEL)
    back = Button(BACK_BUTTON_LABEL)

    if include_final_button:
        main_buttons = Line([back, check,  add])
    else:
        main_buttons = Line([back, check])

    return main_buttons


def get_list_of_volunteer_buttons_in_rota(event: Event) -> Line:
    list_of_volunteers = get_list_of_volunteers_except_those_already_at_event(event)

    volunteer_buttons_line = Line([Button(volunteer.name) for volunteer in list_of_volunteers])

    return volunteer_buttons_line

def get_list_of_volunteers_except_those_already_at_event(event: Event):
    volunteers_at_event =get_list_of_volunteers_at_event(event)
    volunteers_at_event_ids = volunteers_at_event.list_of_volunteer_ids

    master_list_of_volunteers = get_sorted_list_of_volunteers(SORT_BY_FIRSTNAME)
    list_of_volunteers = copy(master_list_of_volunteers)
    for id in volunteers_at_event_ids:
        list_of_volunteers.pop_with_id(id)

    return list_of_volunteers