from app.logic.events.clothing.automatically_get_clothing_data_from_cadets import update_cadet_clothing_at_event
from app.logic.events.clothing.parse_clothing import save_clothing_data, distribute_colour_groups, clear_all_colours
from app.logic.events.clothing.render_clothing import get_button_bar_for_clothing, get_clothing_table, \
    GET_CLOTHING_FOR_CADETS, sort_buttons_for_clothing, save_sort_order, FILTER_COMMITTEE_BUTTON_LABEL, \
    FILTER_ALL_BUTTON_LABEL, DISTRIBUTE_ACTION_BUTTON_LABEL, set_to_showing_all, set_to_showing_only_committee, CLEAR_ALL_COLOURS
from app.objects.clothing import all_sort_types

from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.events.patrol_boats.parse_patrol_boat_table import *

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm, )
from app.objects.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL, SAVE_BUTTON_LABEL
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.logic.events.events_in_state import get_event_from_state

from app.objects.abstract_objects.abstract_text import Heading


def display_form_view_for_clothing_requirements(interface: abstractInterface) -> Form:

    event =get_event_from_state(interface)
    title = Heading("Clothing requirements for event %s" % str(event), centred=True, size=4)

    button_bar = get_button_bar_for_clothing(interface=interface, event=event)
    clothing_table = get_clothing_table(interface=interface)

    return Form(
        ListOfLines(
            [
                button_bar,
                title,
                _______________,
                sort_buttons_for_clothing,
                clothing_table,
                _______________,
            ]
        )
    )



def post_form_view_for_clothing_requirements(
    interface: abstractInterface
) -> Union[Form, NewForm]:

    last_button_pressed = interface.last_button_pressed()

    if last_button_pressed==CANCEL_BUTTON_LABEL:
        return previous_form(interface)

    ### save
    save_clothing_data(interface)

    if last_button_pressed==SAVE_BUTTON_LABEL:
        pass

    elif last_button_pressed in all_sort_types:
        sort_order = interface.last_button_pressed()
        save_sort_order(interface=interface, sort_order=sort_order)

    elif last_button_pressed==FILTER_ALL_BUTTON_LABEL:
        set_to_showing_all(interface)

    elif last_button_pressed==GET_CLOTHING_FOR_CADETS:
        update_cadet_clothing_at_event(interface)

    elif last_button_pressed==DISTRIBUTE_ACTION_BUTTON_LABEL:
        distribute_colour_groups(interface)

    elif last_button_pressed==CLEAR_ALL_COLOURS:
        clear_all_colours(interface)

    elif last_button_pressed==FILTER_COMMITTEE_BUTTON_LABEL:
        set_to_showing_only_committee(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.save_stored_items()
    interface.clear_stored_items()

    return display_form_view_for_clothing_requirements(interface)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_view_for_clothing_requirements)

