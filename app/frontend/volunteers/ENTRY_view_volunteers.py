from typing import Union

from app.frontend.volunteers.add_volunteer import display_form_add_volunteer
from app.frontend.volunteers.view_individual_volunteer import (
    display_form_view_individual_volunteer,
)
from app.objects_OLD.primtive_with_id.volunteers import Volunteer
from app.objects_OLD.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects_OLD.abstract_objects.abstract_buttons import (
    main_menu_button,
    Button,
    ButtonBar,
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface
from app.OLD_backend.data.volunteers import SORT_BY_SURNAME, SORT_BY_FIRSTNAME
from app.OLD_backend.volunteers.volunteers import get_sorted_list_of_volunteers
from app.frontend.shared.volunteer_state import (
    update_state_for_specific_volunteer_given_volunteer_as_str,
)
from app.objects_OLD.abstract_objects.abstract_tables import Table, RowInTable

ADD_VOLUNTEER_BUTTON_LABEL = "Add volunteer"
add_button = Button(ADD_VOLUNTEER_BUTTON_LABEL, nav_button=True)
all_sort_types = [SORT_BY_SURNAME, SORT_BY_FIRSTNAME]
sort_buttons = ButtonBar(
    [Button(sort_by, nav_button=True) for sort_by in all_sort_types]
)

nav_buttons = ButtonBar([main_menu_button, add_button])


def display_form_view_of_volunteers(interface: abstractInterface) -> Form:
    ## simple wrap function as display can only take interface

    return get_form_view_of_volunteers(interface=interface, sort_order=SORT_BY_SURNAME)


def get_form_view_of_volunteers(interface: abstractInterface, sort_order: str) -> Form:
    list_of_volunteers_with_buttons = get_list_of_volunteers_with_buttons(
        interface=interface, sort_order=sort_order
    )

    form_contents = ListOfLines(
        [
            nav_buttons,
            _______________,
            sort_buttons,
            _______________,
            Line("Click on any volunteer to view/edit"),
            _______________,
            list_of_volunteers_with_buttons,
        ]
    )

    form = Form(form_contents)

    return form


def post_form_view_of_volunteers(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if add_button.pressed(button_pressed):
        return add_volunteer_form(interface)

    elif button_pressed in all_sort_types:
        ## no change to stage required, just sort order
        sort_order = interface.last_button_pressed()
        return get_form_view_of_volunteers(interface=interface, sort_order=sort_order)

    else:  ## must be a volunteer redirect:
        return view_specific_volunteer_form(interface)


def add_volunteer_form(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_add_volunteer)


def view_specific_volunteer_form(interface: abstractInterface):
    volunteer_selected_as_str = interface.last_button_pressed()
    update_state_for_specific_volunteer_given_volunteer_as_str(
        interface=interface, volunteer_selected=volunteer_selected_as_str
    )
    return interface.get_new_form_given_function(display_form_view_individual_volunteer)


def get_list_of_volunteers_with_buttons(
    interface: abstractInterface, sort_order=SORT_BY_SURNAME
) -> Table:
    list_of_volunteers = get_sorted_list_of_volunteers(
        data_layer=interface.data, sort_by=sort_order
    )

    list_with_buttons = [
        row_of_form_for_volunteer_with_buttons(volunteer)
        for volunteer in list_of_volunteers
    ]

    return Table(list_with_buttons)


def row_of_form_for_volunteer_with_buttons(volunteer: Volunteer) -> RowInTable:
    return RowInTable([Button(str(volunteer))])

