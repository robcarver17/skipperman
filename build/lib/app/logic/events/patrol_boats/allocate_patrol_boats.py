from typing import Union

from app.backend.volunteers.patrol_boats import get_summary_list_of_boat_allocations_for_events
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.events.patrol_boats.parse_patrol_boat_table import get_all_copy_buttons_for_rota, \
    update_if_copy_button_pressed, update_if_save_button_pressed_in_allocation_page
from app.logic.events.patrol_boats.render_patrol_boat_table import get_patrol_boat_table

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import Button, BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.events.events_in_state import get_event_from_state

SAVE_CHANGES_BUTTON_LABEL = "Save changes"

def display_form_view_for_patrol_boat_allocation(interface: abstractInterface) -> Form:

    event =get_event_from_state(interface)
    title = "Patrol boat allocation for event %s" % str(event)

    summary_of_boat_allocations =  get_summary_list_of_boat_allocations_for_events(event)
    patrol_boat_table_with_day_reordering = get_patrol_boat_table(event=event)

    footer_buttons = get_footer_buttons_for_boat_allocation()

    return Form(
        ListOfLines(
            [
                title,
                _______________,
                _______________,
                summary_of_boat_allocations,
                _______________,
                instructions,
                _______________,
                footer_buttons,
                _______________,
                save_button,
                patrol_boat_table_with_day_reordering,
                save_button,
                _______________,
                footer_buttons
            ]
        )
    )

save_button = Button(SAVE_CHANGES_BUTTON_LABEL, big=True)


instructions = ListOfLines(["SAVE CHANGES BEFORE SORTING OR COPYING!"])


def get_footer_buttons_for_boat_allocation():
    return Line([
        Button(BACK_BUTTON_LABEL)
    ])

def post_form_view_for_patrol_boat_allocation(
    interface: abstractInterface
) -> Union[Form, NewForm]:

    last_button_pressed = interface.last_button_pressed()

    ## BUTTONS: Back, Save, Copy

    if last_button_pressed==BACK_BUTTON_LABEL:
        return previous_form(interface)
    elif last_button_pressed==SAVE_CHANGES_BUTTON_LABEL:
        update_if_save_button_pressed_in_allocation_page(interface)
        return display_form_view_for_patrol_boat_allocation(interface)

    elif last_button_pressed in get_all_copy_buttons_for_rota(interface):
        update_if_copy_button_pressed(interface=interface, copy_button=last_button_pressed)
        display_form_view_for_patrol_boat_allocation(interface)

    ## exception
    else:
        return button_error_and_back_to_initial_state_form(interface)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(post_form_view_for_patrol_boat_allocation)

