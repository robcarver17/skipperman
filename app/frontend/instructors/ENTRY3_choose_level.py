from typing import Union

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.instructors.mark_attendance import display_instructor_attendance
from app.frontend.shared.buttons import get_button_value_given_type_and_attributes, is_button_of_type, \
    get_attributes_from_button_pressed_of_known_type
from app.objects.abstract_objects.abstract_buttons import (
    ButtonBar,
    Button,
    main_menu_button,
    HelpButton,
    back_menu_button,
)

from app.objects.abstract_objects.abstract_text import Heading

from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)

from app.frontend.shared.events_state import get_event_from_state
from app.frontend.shared.qualification_and_tick_state_storage import (
    get_group_from_state,
    update_state_for_qualification_name,
)
from app.backend.qualifications_and_ticks.list_of_qualifications import (
    get_list_of_qualifications,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.instructors.ENTRY_FINAL_view_ticksheets import (
    display_form_view_ticksheets_for_event_and_group,
)


def display_form_choose_level_for_group_at_event(interface: abstractInterface) -> Form:
    event = get_event_from_state(interface)
    group = get_group_from_state(interface)
    level_buttons = get_level_buttons(interface=interface)

    navbar = ButtonBar(
        [main_menu_button, back_menu_button, HelpButton("ticksheets_levels_help")]
    )
    header = Line(
        Heading(
            "Tick sheets and reports for instructors: Event: %s, Group: %s"            % (str(event), str(group)),
            centred=False,
            size=2,
        )
    )

    header2 = Line(
        Heading(
            "Choose qualification for ticksheets",
            centred=False,
            size=4,
        )
    )

    lines_inside_form = ListOfLines(
        [
            navbar,
            _______________,
            header,
            _______________,
            mark_attendance_button,
            _______________,
            header2,
            _______________,
            level_buttons,
        ]
    )
    
    return Form(lines_inside_form)


def get_level_buttons(interface: abstractInterface):
    list_of_levels = get_list_of_qualifications(interface.object_store)
    list_of_level_names = list_of_levels.list_of_names()

    list_with_buttons = [
        Button(level_name, value=value_for_level_button(level_name), tile=True) for level_name in list_of_level_names
    ]

    return Line(list_with_buttons)

mark_attendance_button = Button("Mark attendance", tile=True)

def post_form_choose_level_for_group_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if back_menu_button.pressed(button_pressed):
        ## no change to stage required
        return previous_form(interface)

    elif is_level_button(button_pressed):
        return action_when_level_button_clicked(interface)
    elif mark_attendance_button.pressed(button_pressed):
        return interface.get_new_form_given_function(display_instructor_attendance)
    else:
        return button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_choose_level_for_group_at_event
    )


def action_when_level_button_clicked(interface: abstractInterface) -> NewForm:
    qualification_name_selected = level_name_from_button(interface.last_button_pressed())
    update_state_for_qualification_name(
        interface=interface, qualification_name=qualification_name_selected
    )

    return form_for_view_ticksheets(interface)


def form_for_view_ticksheets(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_view_ticksheets_for_event_and_group
    )



level_select_type = "levelSelect"
def value_for_level_button(level_name:str):
    return get_button_value_given_type_and_attributes(level_select_type, level_name)

def is_level_button(button_pressed:str):
    return is_button_of_type(value_of_button_pressed=button_pressed, type_to_check=level_select_type)

def level_name_from_button(button_pressed:str):
    return get_attributes_from_button_pressed_of_known_type(value_of_button_pressed=button_pressed, type_to_check=level_select_type)

