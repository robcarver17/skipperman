
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.events.patrol_boats.parse_patrol_boat_table import *
from app.logic.events.patrol_boats.render_patrol_boat_table import get_patrol_boat_table, \
    get_top_material_for_patrol_boat_form, \
    get_button_bar_for_patrol_boats, get_back_button_for_boat_allocation, SAVE_CHANGES_BUTTON_LABEL
from app.logic.events.patrol_boats.patrol_boat_dropdowns import ADD_NEW_BOAT_BUTTON_LABEL
from app.logic.events.patrol_boats.swapping import get_all_swap_buttons_for_boat_allocation, \
    update_if_swap_button_pressed

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm, )
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL, ButtonBar
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.logic.events.events_in_state import get_event_from_state

from app.logic.events.patrol_boats.parse_patrol_boat_table import get_all_copy_boat_buttons_for_boat_allocation
from app.objects.abstract_objects.abstract_text import Heading


def display_form_view_for_patrol_boat_allocation(interface: abstractInterface) -> Form:

    event =get_event_from_state(interface)
    title = Heading("Patrol boat allocation for event %s" % str(event), centred=True, size=4)

    top_material = get_top_material_for_patrol_boat_form(interface=interface, event=event)
    patrol_boat_table = get_patrol_boat_table(event=event, interface=interface)
    button_bar = get_button_bar_for_patrol_boats(interface)
    back_button = get_back_button_for_boat_allocation(interface)

    return Form(
        ListOfLines(
            [
                ButtonBar([back_button]),
                title,
                _______________,
                _______________,
                top_material,
                _______________,
                button_bar,
                patrol_boat_table,
                button_bar,
                _______________,
            ]
        )
    )


def post_form_view_for_patrol_boat_allocation(
    interface: abstractInterface
) -> Union[Form, NewForm]:

    last_button_pressed = interface.last_button_pressed()

    ## BUTTONS: Back, Save, Copy
    if last_button_pressed==BACK_BUTTON_LABEL:
        return previous_form(interface)

    update_data_from_form_entries_in_patrol_boat_allocation_page(interface)
    if last_button_pressed==SAVE_CHANGES_BUTTON_LABEL:
        pass

    elif last_button_pressed == ADD_NEW_BOAT_BUTTON_LABEL:
        update_adding_boat(interface)

    elif (last_button_pressed in
          get_all_delete_buttons_for_patrol_boat_table(interface)):
        update_if_delete_boat_button_pressed(interface=interface, delete_button=last_button_pressed)

    elif last_button_pressed in get_all_delete_volunteer_buttons_for_patrol_boat_table(interface):
        update_if_delete_volunteer_button_pressed(interface=interface, delete_button=last_button_pressed)

    elif last_button_pressed in get_all_copy_boat_buttons_for_boat_allocation(interface):
        update_if_copy_button_pressed(interface=interface, copy_button=last_button_pressed)

    elif last_button_pressed in get_all_swap_buttons_for_boat_allocation(interface):
        update_if_swap_button_pressed(interface=interface, swap_button=last_button_pressed)

    ## exception
    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.save_stored_items()
    interface.clear_stored_items()

    return display_form_view_for_patrol_boat_allocation(interface)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(post_form_view_for_patrol_boat_allocation)

