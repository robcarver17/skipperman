from typing import Union

from app.frontend.events.volunteer_rota.parse_volunteer_table import (
    save_volunteer_matrix_and_return_filename,
    action_if_volunteer_button_pressed,
    action_if_location_button_pressed,
    action_if_volunteer_skills_button_pressed,
    update_if_make_available_button_pressed,
    update_if_make_unavailable_button_pressed,
    update_if_remove_role_button_pressed, update_filters, save_all_information_in_rota_page,
)
from app.frontend.events.volunteer_rota.copying import update_if_copy_button_pressed
from app.frontend.events.volunteer_rota.volunteer_targets import save_targets_button, save_volunteer_targets

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.frontend.form_handler import button_error_and_back_to_initial_state_form

from app.frontend.events.volunteer_rota.swapping import update_if_swap_button_pressed
from app.frontend.events.volunteer_rota.add_volunteer_to_rota import (
    display_form_add_new_volunteer_to_rota_at_event,
)


from app.frontend.events.volunteer_rota.rota_state import (
    save_sorts_to_state,
    get_sorts_and_filters_from_state,
    clear_all_filters,
)
from app.frontend.events.volunteer_rota.button_values import (
    from_day_button_value_to_day,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    File,
)
from app.objects.abstract_objects.abstract_buttons import (
    cancel_menu_button,
    save_menu_button,
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
from app.frontend.events.volunteer_rota.volunteer_rota_buttons import (
    was_volunteer_name_sort_button_pressed,
    sort_by_cadet_location_button,
    apply_filter_button,
    clear_filter_button,
    add_volunteer_button,
    download_matrix_button,
    last_button_pressed_was_volunteer_name_button,
    last_button_pressed_was_day_sort_button,
    last_button_pressed_was_location_button,
    last_button_pressed_was_skill_button,
    last_button_pressed_was_make_available_button,
    last_button_pressed_was_copy_button,
    last_button_pressed_was_swap_button,
    last_button_pressed_was_remove_role_button,
    last_button_pressed_was_make_unavailable_button,
)


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
        return previous_form(interface)


    ### BUTTONS: HAS TO BE ONE BIG IF
    ## This may reverse what we did before with filter updates, that's fine
    if clear_filter_button.pressed(last_button_pressed):
        clear_all_filters(interface)

    ## File download
    elif download_matrix_button.pressed(last_button_pressed):
        filename = save_volunteer_matrix_and_return_filename(interface)
        return File(filename)

    ## Actions which result in new forms
    elif add_volunteer_button.pressed(last_button_pressed):
        return add_new_volunteer_form(interface)

    elif last_button_pressed_was_volunteer_name_button(interface):
        return action_if_volunteer_button_pressed(
            interface=interface, volunteer_button=last_button_pressed
        )

    elif last_button_pressed_was_location_button(interface):
        return action_if_location_button_pressed(
            interface=interface, location_button=last_button_pressed
        )

    elif last_button_pressed_was_skill_button(interface):
        return action_if_volunteer_skills_button_pressed(
            interface=interface, volunteer_skills_button=last_button_pressed
        )

    ## SORTS
    elif was_volunteer_name_sort_button_pressed(interface):
        save_sorts_to_state(
            interface=interface, sort_by_volunteer_name=last_button_pressed
        )
    elif last_button_pressed_was_day_sort_button(interface):
        sort_by_day = from_day_button_value_to_day(last_button_pressed)
        save_sorts_to_state(interface=interface, sort_by_day=sort_by_day)

    elif sort_by_cadet_location_button.pressed(last_button_pressed):
        save_sorts_to_state(interface=interface, sort_by_location=True)

    ## Updates to form, display form again
    elif last_button_pressed_was_make_available_button(interface):
        update_if_make_available_button_pressed(
            available_button=last_button_pressed, interface=interface
        )

    elif last_button_pressed_was_make_unavailable_button(interface):
        update_if_make_unavailable_button_pressed(
            interface=interface, unavailable_button=last_button_pressed
        )

    elif last_button_pressed_was_remove_role_button(interface):
        update_if_remove_role_button_pressed(
            interface=interface, remove_button=last_button_pressed
        )

    elif last_button_pressed_was_copy_button(interface):
        update_if_copy_button_pressed(
            interface=interface, copy_button=last_button_pressed
        )

    elif last_button_pressed_was_swap_button(interface):
        update_if_swap_button_pressed(
            interface=interface, swap_button=last_button_pressed
        )
    elif save_menu_button.pressed(last_button_pressed):
        save_all_information_in_rota_page(interface)

    elif save_targets_button.pressed(last_button_pressed):
        save_volunteer_targets(interface)

    elif apply_filter_button.pressed(last_button_pressed):
        update_filters(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return display_form_view_for_volunteer_rota(interface=interface)


def add_new_volunteer_form(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_add_new_volunteer_to_rota_at_event
    )


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_view_for_volunteer_rota
    )
