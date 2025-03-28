from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.events.patrol_boats.copying import (
    copy_across_all_boats_and_roles,
    copy_across_all_boats,
    overwrite_allocation_across_all_boats,
    overwrite_copy_across_all_boats_and_roles, update_if_copy_button_pressed, )
from app.frontend.events.patrol_boats.copy_buttons import is_copy_button, copy_all_boats_button, \
    copyover_all_boats_button, copy_all_boats_and_roles_button, copyover_all_boats_and_roles_button
from app.frontend.events.patrol_boats.parse_patrol_boat_table import *
from app.frontend.events.patrol_boats.patrol_boat_buttons import (
    add_new_boat_button, is_delete_boat_button, is_delete_volunteer_button,
)
from app.frontend.events.patrol_boats.render_patrol_boat_table import (
    get_patrol_boat_table,
    get_top_material_for_patrol_boat_form,
)
from app.frontend.events.patrol_boats.elements_in_patrol_boat_table import (
    get_bottom_button_bar_for_patrol_boats,
    get_top_button_bar_for_patrol_boats,
)

from app.frontend.events.patrol_boats.swapping import (
    update_if_swap_button_pressed, is_swap_button,
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
    top_button_bar = get_top_button_bar_for_patrol_boats(interface)
    bottom_button_bar = get_bottom_button_bar_for_patrol_boats(interface)
    return Form(
        ListOfLines(
            [
                top_button_bar,
                title,
                _______________,
                top_material,
                _______________,
                patrol_boat_table,
                bottom_button_bar,
                _______________,
            ]
        )
    )


def post_form_view_for_patrol_boat_allocation(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()

    if cancel_menu_button.pressed(last_button_pressed):
        return previous_form(interface)

    if save_menu_button.pressed(last_button_pressed):
        update_data_from_form_entries_in_patrol_boat_allocation_page(interface)

    elif copy_all_boats_button.pressed(last_button_pressed):
        copy_across_all_boats(interface)

    elif copy_all_boats_and_roles_button.pressed(last_button_pressed):
        copy_across_all_boats_and_roles(interface)

    elif copyover_all_boats_button.pressed(last_button_pressed):
        overwrite_allocation_across_all_boats(interface)

    elif copyover_all_boats_and_roles_button.pressed(last_button_pressed):
        overwrite_copy_across_all_boats_and_roles(interface)

    elif add_new_boat_button.pressed(last_button_pressed):
        update_adding_boat(interface)

    elif is_delete_boat_button(last_button_pressed):
        update_if_delete_boat_button_pressed(
            interface=interface, delete_button=last_button_pressed
        )

    elif is_delete_volunteer_button(last_button_pressed):
        update_if_delete_volunteer_button_pressed(
            interface=interface, delete_button=last_button_pressed
        )

    elif is_copy_button(last_button_pressed):
        update_if_copy_button_pressed(
            interface=interface, copy_button=last_button_pressed
        )

    elif is_swap_button(last_button_pressed):
        update_if_swap_button_pressed(
            interface=interface, swap_button=last_button_pressed
        )

    ## exception
    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.save_cache_to_store_without_clearing()

    return interface.get_new_form_given_function(display_form_view_for_patrol_boat_allocation)


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_view_for_patrol_boat_allocation
    )
