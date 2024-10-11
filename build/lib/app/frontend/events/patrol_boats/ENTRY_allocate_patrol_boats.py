from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.events.patrol_boats.copying import (
    copy_across_all_boats_and_roles,
    copy_across_all_boats,
    copy_over_across_all_boats,
    copy_over_across_all_boats_and_roles,
)
from app.frontend.events.patrol_boats.parse_patrol_boat_table import *
from app.frontend.events.patrol_boats.patrol_boat_buttons import copy_all_boats_button, copyover_all_boats_button, \
    copy_all_boats_and_roles_button, copyover_all_boats_and_roles_button, add_new_boat_button
from app.frontend.events.patrol_boats.render_patrol_boat_table import (
    get_patrol_boat_table,
    get_top_material_for_patrol_boat_form,
)
from app.frontend.events.patrol_boats.elements_in_patrol_boat_table import get_button_bar_for_patrol_boats

from app.frontend.events.patrol_boats.swapping import (
    get_all_swap_buttons_for_boat_allocation,
    update_if_swap_button_pressed,
)

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    cancel_menu_button,
    save_menu_button,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.frontend.shared.events_state import get_event_from_state

from app.frontend.events.patrol_boats.parse_patrol_boat_table import (
    get_all_copy_boat_buttons_for_boat_allocation,
)
from app.objects.abstract_objects.abstract_text import Heading


def display_form_view_for_patrol_boat_allocation(interface: abstractInterface) -> Form:
    event = get_event_from_state(interface)
    title = Heading(
        "Patrol boat allocation for event %s" % str(event), centred=True, size=4
    )

    top_material = get_top_material_for_patrol_boat_form(
        interface=interface, event=event
    )
    patrol_boat_table = get_patrol_boat_table(event=event, interface=interface)
    button_bar = get_button_bar_for_patrol_boats(interface)

    return Form(
        ListOfLines(
            [
                button_bar,
                title,
                _______________,
                top_material,
                _______________,
                patrol_boat_table,
                button_bar,
                _______________,
            ]
        )
    )


def post_form_view_for_patrol_boat_allocation(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()

    if last_button_pressed == cancel_menu_button.name:
        return previous_form(interface)

    update_data_from_form_entries_in_patrol_boat_allocation_page(interface)

    if last_button_pressed == save_menu_button.name:
        pass
    elif copy_all_boats_button.pressed(last_button_pressed):
        copy_across_all_boats(interface)
    elif copy_all_boats_and_roles_button.pressed(last_button_pressed):
        copy_across_all_boats_and_roles(interface)
    elif copyover_all_boats_button.pressed(last_button_pressed):
        copy_over_across_all_boats(interface)
    elif copyover_all_boats_and_roles_button.pressed(last_button_pressed):
        copy_over_across_all_boats_and_roles(interface)
    elif add_new_boat_button.pressed(last_button_pressed):
        update_adding_boat(interface)

    elif last_button_pressed in get_all_delete_buttons_for_patrol_boat_table(interface):
        update_if_delete_boat_button_pressed(
            interface=interface, delete_button=last_button_pressed
        )

    elif last_button_pressed in get_all_delete_volunteer_buttons_for_patrol_boat_table(
        interface
    ):
        update_if_delete_volunteer_button_pressed(
            interface=interface, delete_button=last_button_pressed
        )

    elif last_button_pressed in get_all_copy_boat_buttons_for_boat_allocation(
        interface
    ):
        update_if_copy_button_pressed(
            interface=interface, copy_button=last_button_pressed
        )

    elif last_button_pressed in get_all_swap_buttons_for_boat_allocation(interface):
        update_if_swap_button_pressed(
            interface=interface, swap_button=last_button_pressed
        )

    ## exception
    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return display_form_view_for_patrol_boat_allocation(interface)




def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_view_for_patrol_boat_allocation
    )
