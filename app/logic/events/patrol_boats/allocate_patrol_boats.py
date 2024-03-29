from typing import Union

from app.backend.forms.swaps import is_ready_to_swap
from app.backend.volunteers.patrol_boats import get_summary_list_of_boat_allocations_for_events
from app.data_access.configuration.configuration import WEBLINK_FOR_QUALIFICATIONS
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
    NewForm, Link,
)
from app.objects.abstract_objects.abstract_buttons import Button, BACK_BUTTON_LABEL, ButtonBar
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________, DetailListOfLines
from app.logic.events.events_in_state import get_event_from_state

from app.logic.events.patrol_boats.parse_patrol_boat_table import get_all_copy_boat_buttons_for_boat_allocation
from app.objects.abstract_objects.abstract_text import Heading

SAVE_CHANGES_BUTTON_LABEL = "Save changes"

def display_form_view_for_patrol_boat_allocation(interface: abstractInterface) -> Form:

    event =get_event_from_state(interface)
    title = Heading("Patrol boat allocation for event %s" % str(event), centred=True, size=4)

    summary_of_boat_allocations =  get_summary_list_of_boat_allocations_for_events(event)
    if len(summary_of_boat_allocations)==0:
        summary_of_boat_allocations=""
    else:
        summary_of_boat_allocations = DetailListOfLines(
            ListOfLines([summary_of_boat_allocations]), name='Summary'
        )
    patrol_boat_driver_and_crew_qualifications_table = (
        get_patrol_boat_driver_and_crew_qualifications_table(event))
    if len(patrol_boat_driver_and_crew_qualifications_table)==0:
        patrol_boat_driver_and_crew_qualifications_table = ''
    else:
        patrol_boat_driver_and_crew_qualifications_table = DetailListOfLines(ListOfLines([
            instructions_qual_table,
            patrol_boat_driver_and_crew_qualifications_table
        ]), name = "Qualifications")

    patrol_boat_table = get_patrol_boat_table(event=event, interface=interface)

    save_button = get_save_button(interface)
    back_button = get_back_button_for_boat_allocation(interface)

    return Form(
        ListOfLines(
            [
                ButtonBar([back_button]),
                title,
                _______________,
                _______________,
                summary_of_boat_allocations,
                _______________,
                _______________,
                patrol_boat_driver_and_crew_qualifications_table,
                _______________,
                _______________,
                instructions_table,
                _______________,
                ButtonBar([back_button, save_button]),
                patrol_boat_table,
                ButtonBar([back_button, save_button]),
                _______________,
            ]
        )
    )


def get_save_button(interface: abstractInterface) -> Union[Button, str]:
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        return ""
    else:
        return Button(SAVE_CHANGES_BUTTON_LABEL, nav_button=True)

link = Link(url=
            WEBLINK_FOR_QUALIFICATIONS, string="Qualifications table", open_new_window=True)


instructions_qual_table = ListOfLines([Line(["Tick to specify that a volunteer has PB2 (check don't assume: ", link, " )"])])
instructions_table = ListOfLines([Line(["Save changes after non button actions. Key for buttons - Copy: ",
                                        COPY_SYMBOL1, COPY_SYMBOL2,
                                        "; Swap: ", SWAP_SHORTHAND1, SWAP_SHORTHAND2, ", ",
                                        BOAT_SHORTHAND,' = boat, ',
                                        ROLE_SHORTHAND,' = role, ',
                                        BOAT_AND_ROLE_SHORTHAND,' = boat & role. '
                                        '; Remove: ', REMOVE_SHORTHAND])])


def get_back_button_for_boat_allocation(interface: abstractInterface):
    in_swap_state = is_ready_to_swap(interface)
    if in_swap_state:
        return ""
    else:
        return Button(BACK_BUTTON_LABEL, nav_button=True)


def post_form_view_for_patrol_boat_allocation(
    interface: abstractInterface
) -> Union[Form, NewForm]:

    last_button_pressed = interface.last_button_pressed()

    ## BUTTONS: Back, Save, Copy
    print("BUTTONS %s" % str(get_all_delete_buttons_for_patrol_boat_table(interface)))
    if last_button_pressed==BACK_BUTTON_LABEL:
        return previous_form(interface)

    update_data_from_form_entries_in_allocation_page(interface)
    if last_button_pressed==SAVE_CHANGES_BUTTON_LABEL:
        pass

    elif last_button_pressed == ADD_NEW_BOAT_BUTTON_LABEL:
        update_adding_boat(interface)

    elif (last_button_pressed in
          get_all_delete_buttons_for_patrol_boat_table(interface)):
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

