from typing import Union

from app.frontend.events.group_allocation.change_sort_order import (
    display_change_sort_order,
)
from app.frontend.shared.club_dinghies import (
    update_limits_button,
    update_club_boat_limits_for_event_from_form,
)
from app.frontend.shared.club_boats_instructors import (
    is_club_dinghy_instructor_button,
    handle_club_dinghy_instructor_allocation_button_pressed,
)
from app.frontend.events.group_allocation.previous_events import (
    is_event_picker_button,
    save_event_selection_from_form,
)
from app.frontend.reporting.allocations.report_group_allocations import (
    allocation_report_generator,
)
from app.frontend.reporting.boats.report_boats import boat_report_generator
from app.frontend.reporting.shared.create_report import create_generic_report
from app.frontend.shared.buttons import (
    cadet_from_button_pressed,
    is_button_cadet_selection,
)
from app.frontend.shared.cadet_state import (
    update_state_for_specific_cadet,
    get_cadet_from_state,
)

from app.frontend.events.group_allocation.add_unregistered_cadet import (
    display_add_unregistered_cadet_from_allocation_form,
)

from app.frontend.shared.buttons import (
    is_button_day_select,
    get_day_from_button_pressed,
)
from app.frontend.shared.cadet_state import (
    clear_cadet_state,
    is_cadet_set_in_state,
)

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.events.group_allocation.add_cadet_partner import (
    display_add_cadet_partner,
)
from app.frontend.events.group_allocation.store_state import (
    set_day_in_state,
    clear_day_in_state,
    get_current_sort_order,
)
from app.frontend.events.group_allocation.render_allocation_form import (
    display_form_allocate_cadets_at_event,
    add_button,
    sort_order_change_button,
    quick_group_report_button,
    quick_spotters_report_button,
)
from app.frontend.events.group_allocation.buttons import (
    reset_day_button,
    is_make_available_button,
    was_remove_partner_button,
    get_cadet_given_add_partner_button_name,
    was_add_partner_button,
)
from app.frontend.events.group_allocation.input_fields import (
    guess_boat_button,
)
from app.frontend.events.group_allocation.parse_allocation_form import (
    update_data_given_allocation_form,
    make_cadet_available_on_current_day,
    remove_partnership_for_cadet_from_group_allocation_button,
    guess_boat_classes_in_allocation_form,
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
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

from app.frontend.shared.events_state import get_event_from_state


def display_form_allocate_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    sort_order = get_current_sort_order(interface=interface)
    return display_form_allocate_cadets_at_event(
        interface=interface, event=event, sort_order=sort_order
    )


def post_form_allocate_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    last_button = interface.last_button_pressed()
    if cancel_menu_button.pressed(last_button):
        return previous_form(interface)

    save_all_information_in_forms_on_page(interface)

    if button_clicked_returns_new_form(last_button):
        return post_form_allocate_cadets_returns_new_form(interface, last_button)
    elif button_clicked_changes_state(last_button):
        return post_form_allocate_cadets_when_changing_state(interface, last_button)
    elif button_clicked_changes_data(last_button):
        return post_form_allocate_cadets_when_changing_data(interface, last_button)
    else:
        return button_error_and_back_to_initial_state_form(interface)


def button_clicked_returns_new_form(last_button: str):
    return (
        add_button.pressed(last_button)
        or was_add_partner_button(last_button)
        or sort_order_change_button.pressed(last_button)
        or quick_group_report_button.pressed(last_button)
        or quick_spotters_report_button.pressed(last_button)
    )


def button_clicked_changes_state(last_button: str):
    return is_button_cadet_selection(last_button) or is_button_day_select(last_button)


def button_clicked_changes_data(last_button: str):
    return (
        save_menu_button.pressed(last_button)
        or update_limits_button.pressed(last_button)
        or is_event_picker_button(last_button)
        or is_make_available_button(last_button)
        or was_remove_partner_button(last_button)
        or guess_boat_button.pressed(last_button)
    )


def post_form_allocate_cadets_returns_new_form(
    interface: abstractInterface, last_button: str
) -> Union[File, Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    if add_button.pressed(last_button):
        return interface.get_new_form_given_function(
            display_add_unregistered_cadet_from_allocation_form
        )

    elif was_add_partner_button(last_button):
        cadet = get_cadet_given_add_partner_button_name(
            object_store=interface.object_store, button=last_button
        )
        update_state_for_specific_cadet(interface=interface, cadet=cadet)
        return interface.get_new_form_given_function(display_add_cadet_partner)

    elif sort_order_change_button.pressed(last_button):
        return interface.get_new_form_given_function(display_change_sort_order)

    elif quick_group_report_button.pressed(last_button):
        return create_quick_group_report(interface)

    elif quick_spotters_report_button.pressed(last_button):
        return create_quick_spotters_report(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)


def post_form_allocate_cadets_when_changing_state(
    interface: abstractInterface, last_button: str
) -> Union[Form, NewForm, File]:
    if is_button_cadet_selection(last_button):
        cadet_button_clicked(interface)

    elif is_button_day_select(last_button):
        change_day_and_save(interface=interface, day_button=last_button)

    else:
        return button_error_and_back_to_initial_state_form(interface)

    return display_form_allocate_cadets(interface)


def post_form_allocate_cadets_when_changing_data(
    interface: abstractInterface, last_button: str
) -> Union[Form, NewForm]:
    ## save existing form changes first, might be overwritten later by button actions
    
    if save_menu_button.pressed(last_button):
        pass  # already saved

    elif update_limits_button.pressed(last_button):
        pass  ## alredy saved

    elif is_event_picker_button(last_button):
        pass  ## already saved

    elif is_make_available_button(last_button):
        make_cadet_available_on_current_day(
            interface=interface, add_availability_button_name=last_button
        )

    elif was_remove_partner_button(last_button):
        remove_partnership_for_cadet_from_group_allocation_button(interface)

    elif guess_boat_button.pressed(last_button):
        guess_boat_classes_in_allocation_form(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_and_clear()

    return display_form_allocate_cadets(interface)


def save_all_information_in_forms_on_page(interface: abstractInterface):
    
    update_data_given_allocation_form(interface)
    update_club_boat_limits_for_event_from_form(interface)
    save_event_selection_from_form(interface)

    interface.flush_and_clear()


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_allocate_cadets
    )


def change_day_and_save(interface: abstractInterface, day_button: str):
    if reset_day_button.pressed(day_button):
        clear_day_in_state(interface)
        return

    day = get_day_from_button_pressed(day_button)
    set_day_in_state(interface=interface, day=day)


def cadet_button_clicked(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    cadet = cadet_from_button_pressed(
        object_store=interface.object_store, value_of_button_pressed=last_button
    )

    if is_cadet_set_in_state(interface):
        selected_cadet = get_cadet_from_state(interface)
        if selected_cadet == cadet:
            clear_cadet_state(interface)
            return

    update_state_for_specific_cadet(interface=interface, cadet=cadet)


def create_quick_group_report(interface: abstractInterface) -> File:
    report_generator_with_specific_parameters = (
        allocation_report_generator.add_specific_parameters_for_type_of_report(
            interface.object_store,
            event=get_event_from_state(interface)
        )
    )
    interface.log_error(
        "Quick reports are generated with current report parameters: do not get published to web. To publish or change parameters to go Reporting menu option."
    )
    return create_generic_report(
        report_generator=report_generator_with_specific_parameters,
        interface=interface,
        override_print_options=dict(publish_to_public=False),
        ignore_stored_print_option_values_and_use_default=True,
    )


def create_quick_spotters_report(interface: abstractInterface) -> File:
    report_generator_with_specific_parameters = (
        boat_report_generator.add_specific_parameters_for_type_of_report(
            interface.object_store,
            event=get_event_from_state(interface)
        )
    )
    interface.log_error(
        "Quick reports are generated with current report parameters: do not get published to web. To publish or change parameters to go Reporting menu option."
    )
    return create_generic_report(
        report_generator=report_generator_with_specific_parameters,
        interface=interface,
        override_print_options=dict(publish_to_public=False),
        ignore_stored_print_option_values_and_use_default=True,
    )
