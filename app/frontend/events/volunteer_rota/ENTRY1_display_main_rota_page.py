from typing import Union

from app.frontend.events.volunteer_rota.copy_menu import (
    display_form_volunteer_copy_menu,
)
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
from app.frontend.events.volunteer_rota.post_form_actions import (
    is_a_form_change_that_changes_state,
    is_a_form_change_that_changes_underlying_data,
    is_a_form_change_that_returns_a_new_form,
)
from app.frontend.events.volunteer_rota.volunteer_targets_and_group_notes import (
    save_targets_button,
    save_volunteer_targets,
)


from app.frontend.form_handler import button_error_and_back_to_initial_state_form

from app.frontend.events.volunteer_rota.swapping import (
    update_if_swap_button_pressed,
    last_button_pressed_was_swap_button,
)
from app.frontend.events.volunteer_rota.add_volunteer_to_rota import (
    display_form_add_new_volunteer_to_rota_at_event,
)
from app.frontend.events.volunteer_rota.button_values import *

from app.frontend.events.volunteer_rota.rota_state import (
    save_sorts_to_state,
    get_sorts_and_filters_from_state,
    clear_all_filters,
)
from app.frontend.reporting.rota.report_rota import rota_report_generator
from app.frontend.reporting.shared.create_report import create_generic_report
from app.frontend.shared.buttons import is_button_sort_order
from app.frontend.shared.warnings_table import (
    save_warnings_from_table,
    is_save_warnings_button_pressed,
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
from app.frontend.events.volunteer_rota.volunteer_targets_and_group_notes import (
    save_group_notes_button,
    save_group_notes_from_form,
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
    if cancel_menu_button.pressed(last_button_pressed):
        interface.flush_cache_to_store()
        return previous_form(interface)

    save_all_information_across_forms(interface)

    if is_a_form_change_that_changes_state(last_button_pressed):
        return post_form_view_for_volunteer_rota_if_state_changed(
            interface, last_button_pressed
        )
    elif is_a_form_change_that_changes_underlying_data(last_button_pressed):
        return post_form_view_for_volunteer_rota_if_data_changed(
            interface, last_button_pressed
        )
    elif is_a_form_change_that_returns_a_new_form(last_button_pressed):
        return post_form_view_for_volunteer_rota_if_new_form_returned(
            interface, last_button_pressed
        )
    else:
        print("Triggered none of the rota button checks")
        return button_error_and_back_to_initial_state_form(interface)


def post_form_view_for_volunteer_rota_if_new_form_returned(
    interface: abstractInterface, last_button_pressed: str
) -> Union[Form, NewForm, File]:
    print("New form returned from rota")

    ## File download
    if download_matrix_button.pressed(last_button_pressed):
        filename = save_volunteer_matrix_and_return_filename(interface)
        return File(filename)

    if quick_report_button.pressed(last_button_pressed):
        return create_quick_report(interface)

    if add_volunteer_button.pressed(last_button_pressed):
        return add_new_volunteer_form(interface)

    elif last_button_pressed_was_location_button(last_button_pressed):
        return action_if_location_button_pressed(
            interface=interface, location_button=last_button_pressed
        )

    elif last_button_pressed_was_skill_button(last_button_pressed):
        return action_if_volunteer_skills_button_pressed(
            interface=interface, volunteer_skills_button=last_button_pressed
        )
    elif access_copy_menu.pressed(last_button_pressed):
        return interface.get_new_form_given_function(display_form_volunteer_copy_menu)
    else:
        print("Missing button")
        return button_error_and_back_to_initial_state_form(interface)


def post_form_view_for_volunteer_rota_if_state_changed(
    interface: abstractInterface, last_button_pressed: str
) -> Union[Form, NewForm, File]:
    print("Change state returned in rota")

    ## SORTS - DO NOT CHANGE UNDERLYING DATA
    if is_button_sort_order(last_button_pressed):
        sort_parameters = get_sort_parameters_from_buttons(last_button_pressed)
        save_sorts_to_state(interface=interface, sort_parameters=sort_parameters)
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
        pass  ## already saved

    elif save_targets_button.pressed(last_button_pressed):
        pass

    elif save_group_notes_button.pressed(last_button_pressed):
        pass

    elif is_save_warnings_button_pressed(last_button_pressed):
        pass

    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.save_cache_to_store_without_clearing()

    return interface.get_new_form_given_function(display_form_view_for_volunteer_rota)


def save_all_information_across_forms(interface: abstractInterface):
    save_all_information_in_rota_page(interface)
    save_volunteer_targets(interface)
    save_group_notes_from_form(interface)
    save_warnings_from_table(interface)

    interface.save_cache_to_store_without_clearing()


def add_new_volunteer_form(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_add_new_volunteer_to_rota_at_event
    )


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_view_for_volunteer_rota
    )


def create_quick_report(interface: abstractInterface) -> File:
    report_generator_with_specific_parameters = (
        rota_report_generator.add_specific_parameters_for_type_of_report(
            interface.object_store
        )
    )
    interface.log_error(
        "Quick reports are generated with current report parameters: do not get published to web. To publish or change parameters to go Reporting menu option."
    )
    return create_generic_report(
        report_generator=report_generator_with_specific_parameters, interface=interface,
        override_print_options=dict(publish_to_public=False),
        override_additional_options={"power_boats_only": False},
        ignore_stored_print_option_values_and_use_default=True
    )
