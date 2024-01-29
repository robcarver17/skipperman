from typing import Union

from app.objects.volunteers import Volunteer
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import main_menu_button, Button
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.abstract_interface import abstractInterface
from app.backend.volunteers import get_list_of_volunteers, SORT_BY_SURNAME, SORT_BY_FIRSTNAME
from app.logic.volunteers.volunteer_state import update_state_for_specific_volunteer_given_volunteer_as_str
from app.logic.volunteers.constants import *

add_button = Button(ADD_VOLUNTEER_BUTTON_LABEL)
all_sort_types = [SORT_BY_SURNAME, SORT_BY_FIRSTNAME]
sort_buttons = Line([Button(sort_by) for sort_by in all_sort_types])

def display_form_view_of_volunteers(sort_order=SORT_BY_SURNAME) -> Form:
    list_of_volunteers_with_buttons = display_list_of_volunteers_with_buttons(
        sort_order=sort_order
    )

    form_contents = ListOfLines(
        [
            main_menu_button,
            _______________,
            sort_buttons,
            _______________,
            Line("Click on any volunteer to view/edit/delete"),
            _______________,
            add_button,
            _______________,
            list_of_volunteers_with_buttons,
        ]
    )

    form = Form(form_contents)

    return form


def post_form_view_of_volunteers(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed == ADD_VOLUNTEER_BUTTON_LABEL:
        return NewForm(ADD_VOLUNTEER_STAGE)

    elif button_pressed in all_sort_types:
        ## no change to stage required, just sort order
        sort_order = interface.last_button_pressed()
        return display_form_view_of_volunteers(sort_order=sort_order)

    else:  ## must be a volunteer redirect:
        volunteer_selected = interface.last_button_pressed()
        update_state_for_specific_volunteer_given_volunteer_as_str(interface=interface, volunteer_selected=volunteer_selected)
        return NewForm(VIEW_INDIVIDUAL_VOLUNTEER_STAGE)


def display_list_of_volunteers_with_buttons(sort_order=SORT_BY_SURNAME) -> ListOfLines:
    list_of_volunteers = get_list_of_volunteers(sort_by=sort_order)

    list_with_buttons = [
        row_of_form_for_volunteer_with_buttons(volunteer) for volunteer in list_of_volunteers
    ]

    return ListOfLines(list_with_buttons)


def row_of_form_for_volunteer_with_buttons(volunteer: Volunteer) -> Line:
    return Line([Button(str(volunteer))])




