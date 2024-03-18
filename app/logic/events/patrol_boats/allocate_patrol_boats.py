from typing import Union

from app.backend.forms.swaps import is_ready_to_swap
from app.backend.volunteers.patrol_boats import get_summary_list_of_boat_allocations_for_events
from app.data_access.configuration.fixed import COPY_SYMBOL2, SWAP_SHORTHAND1, SWAP_SHORTHAND2, COPY_SYMBOL1, \
    BOAT_SHORTHAND, ROLE_SHORTHAND, BOAT_AND_ROLE_SHORTHAND
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.events.patrol_boats.parse_patrol_boat_table import *
from app.logic.events.patrol_boats.render_patrol_boat_table import get_patrol_boat_table, \
    get_patrol_boat_driver_and_crew_qualifications_table
from app.logic.events.patrol_boats.patrol_boat_buttons import *
from app.logic.events.patrol_boats.patrol_boat_dropdowns import ADD_NEW_BOAT_BUTTON_LABEL
from app.logic.events.patrol_boats.swapping import get_all_swap_buttons_for_boat_allocation, \
    update_if_swap_button_pressed

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import Button, BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.logic.events.events_in_state import get_event_from_state

from build.lib.app.logic.events.patrol_boats.parse_patrol_boat_table import get_all_copy_boat_buttons_for_boat_allocation

SAVE_CHANGES_BUTTON_LABEL = "Save changes"

def display_form_view_for_patrol_boat_allocation(interface: abstractInterface) -> Form:

    event =get_event_from_state(interface)
    title = "Patrol boat allocation for event %s" % str(event)

    summary_of_boat_allocations =  get_summary_list_of_boat_allocations_for_events(event)
    patrol_boat_driver_and_crew_qualifications_table = (
        get_patrol_boat_driver_and_crew_qualifications_table(event))
    patrol_boat_table = get_patrol_boat_table(event=event, interface=interface)

    footer_buttons = get_footer_buttons_for_boat_allocation()
    save_button = get_save_button(interface)

    return Form(
        ListOfLines(
            [
                title,
                _______________,
                _______________,
                summary_of_boat_allocations,
                _______________,
                _______________,
                instructions_qual_table,
                patrol_boat_driver_and_crew_qualifications_table,
                _______________,
                _______________,
                footer_buttons,
                _______________,
                instructions_table,
                _______________,
                save_button,
                patrol_boat_table,
                save_button,
                _______________,
                footer_buttons
            ]
        )
    )


def get_save_button(interface: abstractInterface) -> Union[Button, str]:
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        return ""
    else:
        return Button(SAVE_CHANGES_BUTTON_LABEL, big=True)


instructions_qual_table = ListOfLines(["Tick to specify that a volunteer has PB2 (check - don't assume)"])
instructions_table = ListOfLines([Line(["Save changes after non button actions. Key for buttons - Copy: ",
                                        COPY_SYMBOL1, COPY_SYMBOL2,
                                        " , Swap: ", SWAP_SHORTHAND1, SWAP_SHORTHAND2, ", ",
                                        BOAT_SHORTHAND,' = boat, ',
                                        ROLE_SHORTHAND,' = role, ',
                                        BOAT_AND_ROLE_SHORTHAND,' = boat & role. '
                                        'Remove: ', REMOVE_SHORTHAND])])


def get_footer_buttons_for_boat_allocation():
    return Line([
        Button(BACK_BUTTON_LABEL)
    ])

def post_form_view_for_patrol_boat_allocation(
    interface: abstractInterface
) -> Union[Form, NewForm]:

    last_button_pressed = interface.last_button_pressed()

    ## BUTTONS: Back, Save, Copy
    print("BUTTONS %s" % str(get_all_delete_buttons_for_patrol_boat_table(interface)))
    if last_button_pressed==BACK_BUTTON_LABEL:
        return previous_form(interface)

    elif last_button_pressed==SAVE_CHANGES_BUTTON_LABEL:
        update_if_save_button_pressed_in_allocation_page(interface)

    elif last_button_pressed == ADD_NEW_BOAT_BUTTON_LABEL:
        update_adding_boat(interface)

    elif (last_button_pressed in
          get_all_delete_buttons_for_patrol_boat_table(interface)):
        print("a delete button")
        update_if_delete_boat_button_pressed(interface=interface, delete_button=last_button_pressed)

    elif last_button_pressed in get_all_delete_volunteer_buttons_for_patrol_boat_table(interface):
        update_if_delete_volunteer_button_pressed(interface=interface, delete_button=last_button_pressed)

    elif last_button_pressed in  get_all_copy_boat_buttons_for_boat_allocation(interface):
        update_if_copy_button_pressed(interface=interface, copy_button=last_button_pressed)

    elif last_button_pressed in get_all_swap_buttons_for_boat_allocation(interface):
        update_if_swap_button_pressed(interface=interface, swap_button=last_button_pressed)

    ## exception
    else:
        return button_error_and_back_to_initial_state_form(interface)

    return display_form_view_for_patrol_boat_allocation(interface)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(post_form_view_for_patrol_boat_allocation)

