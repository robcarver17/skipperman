from typing import Union

from app.frontend.shared.events_state import update_state_for_specific_event_given_event_description

from app.OLD_backend.events import DEPRECATE_confirm_event_exists_given_description
from app.backend.events.list_of_events import all_sort_types_for_event_list, sort_buttons_for_event_list
from app.OLD_backend.ticks_and_qualifications.ticksheets import get_list_of_events_entitled_to_see

from app.objects.abstract_objects.abstract_text import Heading

from app.frontend.events.ENTRY_view_events import display_given_list_of_events_with_buttons
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import main_menu_button, ButtonBar
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________, Line
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.backend.security.logged_in_user import get_volunteer_id_of_logged_in_user_or_superuser_CHANGE_TO_VOLUNTEER
from app.objects.events import SORT_BY_START_DSC
from app.frontend.instructors.ENTRY2_choose_group import display_form_choose_group_for_event
def display_form_main_instructors_page(interface: abstractInterface) -> Form:
    return display_form_main_instructors_page_sort_order_passed(interface=interface, sort_by=SORT_BY_START_DSC)

def display_form_main_instructors_page_sort_order_passed(interface: abstractInterface,  sort_by: str) -> Form:
    event_buttons = get_event_buttons(interface=interface, sort_by=sort_by)
    navbar = ButtonBar([main_menu_button])
    sort_buttons = sort_buttons_for_event_list
    header = Line(Heading("Tick sheets and reports for instructors: Select event", centred=False, size=4))
    lines_inside_form = ListOfLines(
        [
            navbar,
            _______________,
            header,
            _______________,
            sort_buttons,
            _______________,
            event_buttons

        ]
    )

    return Form(lines_inside_form)

def post_form_main_instructors_page(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if button_pressed in all_sort_types_for_event_list:
        ## no change to stage required
        sort_by = interface.last_button_pressed()
        return display_form_main_instructors_page_sort_order_passed(interface=interface, sort_by=sort_by)
    else:  ## must be an event
        return action_when_event_button_clicked(interface)


def action_when_event_button_clicked(interface: abstractInterface) -> NewForm:
    event_description_selected = interface.last_button_pressed()
    DEPRECATE_confirm_event_exists_given_description(event_description_selected)
    update_state_for_specific_event_given_event_description(
        interface=interface, event_description=event_description_selected)

    return form_for_view_event(interface)


def form_for_view_event(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_choose_group_for_event)


def get_event_buttons(interface: abstractInterface, sort_by: str) -> Line:
    volunteer_id = get_volunteer_id_of_logged_in_user_or_superuser_CHANGE_TO_VOLUNTEER(interface)
    list_of_events = get_list_of_events_entitled_to_see(interface=interface, volunteer_id=volunteer_id, sort_by=sort_by)
    return display_given_list_of_events_with_buttons(list_of_events)

