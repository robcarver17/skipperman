from typing import Union

from app.backend.qualifications_and_ticks.ticksheets import get_list_of_all_groups_at_event
from app.backend.security.user_access import get_list_of_groups_volunteer_can_see
from app.frontend.shared.qualification_and_tick_state_storage import update_state_for_group_name
from app.objects.events import Event

from app.backend.security.logged_in_user import get_volunteer_id_of_logged_in_user_or_superuser_CHANGE_TO_VOLUNTEER
from app.objects.abstract_objects.abstract_text import Heading

from app.objects.abstract_objects.abstract_lines import ListOfLines, Line, _______________

from app.objects.abstract_objects.abstract_buttons import Button, BACK_BUTTON_LABEL, \
    get_nav_bar_with_just_main_menu_and_back_button

from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.instructors.ENTRY3_choose_level import display_form_choose_level_for_group_at_event

def display_form_choose_group_for_event(interface: abstractInterface) -> Form:
    event = get_event_from_state(interface)
    group_buttons = get_group_buttons(interface=interface, event=event)
    navbar = get_nav_bar_with_just_main_menu_and_back_button()
    header = Line(Heading("Tick sheets and reports for instructors: Event: %s; Select group" % str(event), centred=False, size=4))
    lines_inside_form = ListOfLines(
        [
            navbar,
            _______________,
            header,
            _______________,
            _______________,
            group_buttons

        ]
    )

    return Form(lines_inside_form)


def get_group_buttons(interface: abstractInterface, event: Event) -> Line:
    if event_is_empty_of_groups(interface=interface, event=event):
        return Line(Heading("No groups defined at this event yet"))

    volunteer_id = get_volunteer_id_of_logged_in_user_or_superuser_CHANGE_TO_VOLUNTEER(interface)
    list_of_groups = get_list_of_groups_volunteer_can_see(interface=interface,
                                                          event=event,
                                                          volunteer_id=volunteer_id)

    if len(list_of_groups)==0:
        return Line(Heading("The user doesn't have right to see any ticksheets for event %s; must be skipper, admin, SI for event, or DI/AI/RCL2 for a group" % str(event), centred=False, size=4))

    list_with_buttons = [Button(group.name, tile=True) for group in list_of_groups]

    return Line(list_with_buttons)

def event_is_empty_of_groups(interface: abstractInterface, event: Event) -> bool:
    return len(get_list_of_all_groups_at_event(interface=interface, event=event))==0


def post_form_choose_group_for_event(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed==BACK_BUTTON_LABEL:
        ## no change to stage required
        return previous_form(interface)
    else:  ## must be a group
        return action_when_group_button_clicked(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(post_form_choose_group_for_event)


def action_when_group_button_clicked(interface: abstractInterface) -> NewForm:
    group_name_selected = interface.last_button_pressed()
    update_state_for_group_name(interface=interface, group_name=group_name_selected)

    return form_for_view_level(interface)


def form_for_view_level(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_choose_level_for_group_at_event)

