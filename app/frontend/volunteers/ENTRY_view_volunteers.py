
from typing import Union

from app.data_access.configuration.fixed import ADD_KEYBOARD_SHORTCUT
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.buttons import (
    get_button_value_for_volunteer_selection,
    is_button_volunteer_selection,
    volunteer_from_button_pressed,
    get_button_value_for_sort_order,
    is_button_sort_order,
    sort_order_from_button_pressed,
)
from app.frontend.volunteers.add_volunteer import display_form_add_volunteer
from app.frontend.volunteers.update_skills_from_csv import (
    display_form_refresh_volunteer_skills,
)
from app.frontend.volunteers.view_individual_volunteer import (
    display_form_view_individual_volunteer,
)
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.volunteers import Volunteer, SORT_BY_SURNAME, SORT_BY_FIRSTNAME
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    Button,
    ButtonBar,
    HelpButton,
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.backend.volunteers.list_of_volunteers import (
    get_sorted_list_of_volunteers,
)
from app.frontend.shared.volunteer_state import update_state_for_specific_volunteer
from app.objects.abstract_objects.abstract_tables import Table, RowInTable


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

    elif refresh_skills_button.pressed(button_pressed):
        return interface.get_new_form_given_function(
            display_form_refresh_volunteer_skills
        )

    elif is_button_sort_order(button_pressed):
        ## no change to stage required, just sort order
        sort_order = sort_order_from_button_pressed(button_pressed)
        return get_form_view_of_volunteers(interface=interface, sort_order=sort_order)

    elif is_button_volunteer_selection(
        button_pressed
    ):  ## must be a volunteer redirect:
        return view_specific_volunteer_form(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)


def add_volunteer_form(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_add_volunteer)


def view_specific_volunteer_form(interface: abstractInterface):
    volunteer = volunteer_from_button_pressed(
        object_store=interface.object_store,
        value_of_button_pressed=interface.last_button_pressed(),
    )
    update_state_for_specific_volunteer(interface=interface, volunteer=volunteer)
    return interface.get_new_form_given_function(display_form_view_individual_volunteer)


def get_list_of_volunteers_with_buttons(
    interface: abstractInterface,
    sort_order=SORT_BY_SURNAME,
    similar_volunteer: Volunteer = arg_not_passed,
    exclude_volunteer: Volunteer = arg_not_passed,
) -> Table:
    list_of_volunteers = get_sorted_list_of_volunteers(
        object_store=interface.object_store,
        sort_by=sort_order,
        similar_volunteer=similar_volunteer,
        exclude_volunteer=exclude_volunteer,
    )

    list_with_buttons = [
        row_of_form_for_volunteer_with_buttons(volunteer)
        for volunteer in list_of_volunteers
    ]

    return Table(list_with_buttons)


def row_of_form_for_volunteer_with_buttons(volunteer: Volunteer) -> RowInTable:
    return RowInTable(
        [
            Button(
                str(volunteer),
                value=get_button_value_for_volunteer_selection(volunteer),
            )
        ]
    )


ADD_VOLUNTEER_BUTTON_LABEL = "Add volunteer"
add_button = Button(
    ADD_VOLUNTEER_BUTTON_LABEL, nav_button=True, shortcut=ADD_KEYBOARD_SHORTCUT
)
help_button = HelpButton("view_all_volunteers_help")

REFRESH_SKILLS_BUTTON_LABEL = "Refresh key skills from .csv file"
refresh_skills_button = Button(REFRESH_SKILLS_BUTTON_LABEL, nav_button=True)

nav_buttons = ButtonBar(
    [main_menu_button, add_button, refresh_skills_button, help_button]
)

all_sort_types = [SORT_BY_SURNAME, SORT_BY_FIRSTNAME]
sort_buttons = ButtonBar(
    [
        Button(sort_by, value=get_button_value_for_sort_order(sort_by), nav_button=True)
        for sort_by in all_sort_types
    ]
)
