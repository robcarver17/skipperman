from typing import Union

from app.backend.data.qualification import QualificationData
from app.objects.abstract_objects.abstract_buttons import ButtonBar, Button, BACK_BUTTON_LABEL, \
    get_nav_bar_with_just_back_button

from app.objects.abstract_objects.abstract_text import Heading

from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________

from app.logic.events.events_in_state import get_event_from_state
from app.logic.instructors.state_storage import get_group_from_state, update_state_for_qualification, \
    update_state_for_qualification_name

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.instructors.view_ticksheets import display_form_view_ticksheets_for_event_and_group

def display_form_choose_level_for_group_at_event(interface: abstractInterface) -> Form:
    event = get_event_from_state(interface)
    group = get_group_from_state(interface)
    level_buttons = get_level_buttons(interface=interface)
    navbar = get_nav_bar_with_just_back_button()
    header = Line(Heading("Tick sheets and reports for instructors: Event %s, group %s, select level" % (str(event), str(group)), centred=False, size=4))
    lines_inside_form = ListOfLines(
        [
            navbar,
            _______________,
            header,
            _______________,
            _______________,
            level_buttons

        ]
    )

    return Form(lines_inside_form)


def get_level_buttons(interface: abstractInterface):
    qual_data = QualificationData(interface.data)
    list_of_levels = qual_data.load_list_of_qualifications()
    list_of_level_names = list_of_levels.list_of_names()

    list_with_buttons = [Button(level_name, tile=True) for level_name in list_of_level_names]

    return Line(list_with_buttons)




def post_form_choose_level_for_group_at_event(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed == BACK_BUTTON_LABEL:
        ## no change to stage required
        return previous_form(interface)
    else:  ## must be a level
        return action_when_level_button_clicked(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(post_form_choose_level_for_group_at_event)


def action_when_level_button_clicked(interface: abstractInterface) -> NewForm:
    qualification_name_selected = interface.last_button_pressed()
    update_state_for_qualification_name(interface=interface, qualification_name=qualification_name_selected)

    return form_for_view_ticksheets(interface)


def form_for_view_ticksheets(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_view_ticksheets_for_event_and_group)


