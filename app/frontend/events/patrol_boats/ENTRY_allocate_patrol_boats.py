from app.frontend.events.patrol_boats.copy_menu import (
    display_form_patrol_boat_copy_menu,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.events.patrol_boats.copying import (
    update_if_copy_individual_button_pressed,
)
from app.frontend.events.patrol_boats.copy_buttons import (
    is_copy_individual_volunteer_button,
    access_copy_menu_button,
)
from app.frontend.events.patrol_boats.parse_patrol_boat_table import *
from app.frontend.events.patrol_boats.patrol_boat_buttons import (
    add_new_boat_button,
    is_delete_boat_button,
    is_delete_volunteer_button,
)
from app.frontend.events.patrol_boats.render_patrol_boat_table import (
    get_patrol_boat_table,
    get_top_material_for_patrol_boat_form,
)
from app.frontend.events.patrol_boats.elements_in_patrol_boat_table import (
    get_bottom_button_bar_for_patrol_boats,
    get_top_button_bar_for_patrol_boats,
    quick_report_button,
)

from app.frontend.events.patrol_boats.swapping import (
    update_if_swap_button_pressed,
    is_swap_button,
)
from app.frontend.reporting.rota.report_rota import rota_report_generator
from app.frontend.reporting.shared.create_report import create_generic_report
from app.frontend.shared.warnings_table import (
    save_warnings_from_table,
    is_save_warnings_button_pressed,
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
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_text import Heading


def display_form_view_for_patrol_boat_allocation(interface: abstractInterface) -> Form:
    event = get_event_from_state(interface)
    top_button_bar = get_top_button_bar_for_patrol_boats(interface)
    title = Heading(
        "Patrol boat allocation for event %s" % str(event), centred=True, size=4
    )

    top_material = get_top_material_for_patrol_boat_form(
        interface=interface, event=event
    )
    patrol_boat_table = get_patrol_boat_table(event=event, interface=interface)
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
) -> Union[Form, NewForm, File]:
    last_button_pressed = interface.last_button_pressed()

    if cancel_menu_button.pressed(last_button_pressed):
        interface.flush_cache_to_store()
        return previous_form(interface)

    update_data_from_form_entries_in_patrol_boat_allocation_page(interface)

    ## New form
    if access_copy_menu_button.pressed(last_button_pressed):
        interface.flush_cache_to_store()
        return interface.get_new_form_given_function(display_form_patrol_boat_copy_menu)
    elif quick_report_button.pressed(last_button_pressed):
        return create_quick_report(interface)

    ## remaining options do something and then return current form
    if save_menu_button.pressed(last_button_pressed):
        pass  # already done

    elif is_save_warnings_button_pressed(last_button_pressed):
        pass  # already done

    elif is_copy_individual_volunteer_button(last_button_pressed):
        update_if_copy_individual_button_pressed(
            interface=interface, copy_button=last_button_pressed
        )

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

    elif is_swap_button(last_button_pressed):
        update_if_swap_button_pressed(
            interface=interface, swap_button=last_button_pressed
        )

    ## exception
    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.save_cache_to_store_without_clearing()

    return interface.get_new_form_given_function(
        display_form_view_for_patrol_boat_allocation
    )


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_view_for_patrol_boat_allocation
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
        report_generator=report_generator_with_specific_parameters,
        interface=interface,
        override_print_options={"power_boats_only": True, "output_pdf": False},
    )
