from typing import Union

from app.logic.events.group_allocation.render_allocation_form import display_form_allocate_cadets_at_event
from app.logic.events.group_allocation.parse_allocation_form import update_data_given_allocation_form
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

from app.logic.events.events_in_state import get_event_from_state


def display_form_allocate_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    return display_form_allocate_cadets_at_event(event)


def post_form_allocate_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    if interface.last_button_pressed() == BACK_BUTTON_LABEL:
        return previous_form(interface)

    update_data_given_allocation_form(interface)

    return interface.get_new_form_given_function(display_form_allocate_cadets)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_allocate_cadets)


