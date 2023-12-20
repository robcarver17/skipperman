from typing import Union

from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.logic.forms_and_interfaces.abstract_form import (
    Form,
    NewForm,
    Line,
    Button,
    ListOfLines,
    main_menu_button, _______________,
)
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.logic.volunteers.backend import get_list_of_volunteers, SORT_BY_SURNAME, SORT_BY_FIRSTNAME, update_state_for_specific_volunteer
from app.logic.volunteers.constants import *

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
        update_state_for_specific_volunteer(interface=interface, volunteer_selected=volunteer_selected)
        return NewForm(VIEW_INDIVIDUAL_VOLUNTEER_STAGE)


def display_list_of_volunteers_with_buttons(sort_order=SORT_BY_SURNAME) -> ListOfLines:
    list_of_volunteers = get_list_of_volunteers(sort_by=sort_order)

    list_with_buttons = [
        row_of_form_for_volunteer_with_buttons(volunteer) for volunteer in list_of_volunteers
    ]

    return ListOfLines(list_with_buttons)


def row_of_form_for_volunteer_with_buttons(volunteer: Volunteer) -> Line:
    return Line([Button(str(volunteer))])


all_sort_types = [SORT_BY_SURNAME, SORT_BY_FIRSTNAME]


add_button = Button(ADD_VOLUNTEER_BUTTON_LABEL)

sort_buttons = Line([Button(sort_by) for sort_by in all_sort_types])


