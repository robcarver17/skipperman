from typing import Union

from app.frontend.events.volunteer_rota.parse_volunteer_table import (
    save_volunteer_matrix_and_return_filename,
    action_if_volunteer_button_pressed,
    action_if_location_button_pressed,
    action_if_volunteer_skills_button_pressed,
    update_if_make_available_button_pressed,
    update_if_make_unavailable_button_pressed,
    update_if_remove_role_button_pressed,
    update_filters,
    save_all_information_in_rota_page,
)
from app.frontend.events.volunteer_rota.copying import update_if_copy_button_pressed
from app.frontend.events.volunteer_rota.post_form_actions import \
    is_a_form_change_that_does_not_change_underyling_data_but_changes_state, \
    is_a_form_change_that_changes_underlying_data, is_a_form_change_that_returns_a_new_form_and_does_not_change_data
from app.frontend.events.volunteer_rota.volunteer_targets import (
    save_targets_button,
    save_volunteer_targets,
)


from app.frontend.form_handler import button_error_and_back_to_initial_state_form

from app.frontend.events.volunteer_rota.swapping import update_if_swap_button_pressed, \
    last_button_pressed_was_swap_button
from app.frontend.events.volunteer_rota.add_volunteer_to_rota import (
    display_form_add_new_volunteer_to_rota_at_event,
)
from app.frontend.events.volunteer_rota.button_values import *

from app.frontend.events.volunteer_rota.rota_state import (
    save_sorts_to_state,
    get_sorts_and_filters_from_state,
    clear_all_filters,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.frontend.shared.events_state import get_event_from_state

from app.frontend.events.volunteer_rota.render_volunteer_table import (
    get_volunteer_table,
)
from app.frontend.events.volunteer_rota.elements_in_volunteer_rota_page import (
    get_filters_and_buttons,
)
from app.frontend.events.volunteer_rota.preamble_to_rota_page import (
    get_preamble_before_table,
)
from app.frontend.events.volunteer_rota.volunteer_rota_buttons import *


def display_form_view_for_volunteer_rota(interface: abstractInterface) -> Form:
    sorts_and_filters = get_sorts_and_filters_from_state(interface)
    event = get_event_from_state(interface)

    preamble_before_table = get_preamble_before_table(interface=interface, event=event)
    volunteer_table = get_volunteer_table(
        event=event, interface=interface, sorts_and_filters=sorts_and_filters
    )
    material_around_table = get_filters_and_buttons(
        interface=interface, event=event, sorts_and_filters=sorts_and_filters
    )
    form = Form(
        ListOfLines(
            preamble_before_table
            + [
                _______________,
                material_around_table.before_table,
                _______________,
                volunteer_table,
                _______________,
                material_around_table.after_table,
            ]
        )
    )
    return form


def post_form_view_for_volunteer_rota(
    interface: abstractInterface,
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()
    if is_a_form_change_that_does_not_change_underyling_data_but_changes_state(last_button_pressed):
        return post_form_view_for_volunteer_rota_if_data_unchanged_but_state_changed(interface, last_button_pressed)
    elif is_a_form_change_that_changes_underlying_data(last_button_pressed):
        return post_form_view_for_volunteer_rota_if_data_changed(interface, last_button_pressed)
    elif is_a_form_change_that_returns_a_new_form_and_does_not_change_data(last_button_pressed):
        return post_form_view_for_volunteer_rota_if_new_form_returned(interface, last_button_pressed)
    else:
        print("Triggered none of the rota button checks")
        return button_error_and_back_to_initial_state_form(interface)


def post_form_view_for_volunteer_rota_if_new_form_returned(
        interface: abstractInterface, last_button_pressed: str
) -> Union[Form, NewForm, File]:
    print("New form returned from rota")
    if cancel_menu_button.pressed(last_button_pressed):
        interface.flush_cache_to_store()
        return previous_form(interface)

    ## File download
    elif download_matrix_button.pressed(last_button_pressed):
        filename = save_volunteer_matrix_and_return_filename(interface)
        return File(filename)

    elif add_volunteer_button.pressed(last_button_pressed):
        return add_new_volunteer_form(interface)

    elif last_button_pressed_was_location_button(last_button_pressed):
        return action_if_location_button_pressed(
            interface=interface, location_button=last_button_pressed
        )

    elif last_button_pressed_was_skill_button(last_button_pressed):
        return action_if_volunteer_skills_button_pressed(
            interface=interface, volunteer_skills_button=last_button_pressed
        )
    else:
        print("Missing button")
        return button_error_and_back_to_initial_state_form(interface)

def post_form_view_for_volunteer_rota_if_data_unchanged_but_state_changed(
        interface: abstractInterface,last_button_pressed:str
) -> Union[Form, NewForm, File]:
    print("Change state returned in rota")
    ## SORTS - DO NOT CHANGE UNDERLYING DATA
    if is_button_sort_order(last_button_pressed):
        sort_parameters = get_sort_parameters_from_buttons(last_button_pressed)
        save_sorts_to_state(
            interface=interface, sort_parameters=sort_parameters
        )
    elif clear_filter_button.pressed(last_button_pressed):
        clear_all_filters(interface)

    elif apply_filter_button.pressed(last_button_pressed):
        update_filters(interface)

    elif last_button_pressed_was_volunteer_name_button(last_button_pressed):
        action_if_volunteer_button_pressed(
            interface=interface, volunteer_button=last_button_pressed
        )

    else:
        print("missing button")
        return button_error_and_back_to_initial_state_form(interface)

    ## no need to save flush cache
    return interface.get_new_form_given_function(display_form_view_for_volunteer_rota)


def post_form_view_for_volunteer_rota_if_data_changed(
        interface: abstractInterface, last_button_pressed: str
) -> Union[Form, NewForm, File]:
    print("Changing underlying data")

    if last_button_pressed_was_make_available_button(last_button_pressed):
        update_if_make_available_button_pressed(
            available_button=last_button_pressed, interface=interface
        )

    elif last_button_pressed_was_make_unavailable_button(last_button_pressed):
        update_if_make_unavailable_button_pressed(
            interface=interface, unavailable_button=last_button_pressed
        )

    elif last_button_pressed_was_remove_role_button(last_button_pressed):
        update_if_remove_role_button_pressed(
            interface=interface, remove_button=last_button_pressed
        )

    elif last_button_pressed_was_copy_button(last_button_pressed):
        update_if_copy_button_pressed(
            interface=interface, copy_button=last_button_pressed
        )

    elif last_button_pressed_was_swap_button(last_button_pressed):
        update_if_swap_button_pressed(
            interface=interface, swap_button=last_button_pressed
        )

    ## SAVES

    elif save_menu_button.pressed(last_button_pressed):
        save_all_information_in_rota_page(interface)

    elif save_targets_button.pressed(last_button_pressed):
        save_volunteer_targets(interface)

    else:
        print("button not found")
        return button_error_and_back_to_initial_state_form(interface)

    interface.save_cache_to_store_without_clearing()

    return interface.get_new_form_given_function(display_form_view_for_volunteer_rota)


def add_new_volunteer_form(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_add_new_volunteer_to_rota_at_event
    )


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_view_for_volunteer_rota
    )
