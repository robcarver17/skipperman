
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.events.patrol_boats.parse_patrol_boat_table import *

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm, )
from app.objects.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL, ButtonBar, Button, SAVE_BUTTON_LABEL
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.logic.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_text import Heading


def display_form_view_for_clothing_requirements(interface: abstractInterface) -> Form:

    event =get_event_from_state(interface)
    title = Heading("Clothing requirements for event %s" % str(event), centred=True, size=4)

    button_bar = get_button_bar_for_clothing_required()

    return Form(
        ListOfLines(
            [
                button_bar,
                title,
                _______________,
                _______________,
            ]
        )
    )

def get_button_bar_for_clothing_required() -> ButtonBar:
    save_button = Button(SAVE_BUTTON_LABEL, nav_button=True)
    back_button = Button(CANCEL_BUTTON_LABEL, nav_button=True)
    return ButtonBar([back_button, save_button])


def post_form_view_for_clothing_requirements(
    interface: abstractInterface
) -> Union[Form, NewForm]:

    last_button_pressed = interface.last_button_pressed()

    if last_button_pressed==CANCEL_BUTTON_LABEL:
        return previous_form(interface)

    ### save

    if last_button_pressed==SAVE_BUTTON_LABEL:
        pass

    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface._save_data_store_cache()
    interface._clear_data_store_cache()

    return display_form_view_for_clothing_requirements(interface)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_view_for_clothing_requirements)

