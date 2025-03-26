from typing import Union

from app.frontend.events.group_allocation.ENTRY_allocate_cadets_to_groups import (
    display_form_allocate_cadets,
)
from app.frontend.events.import_data.ENTRY_import_choose import (
    display_form_choose_import_source,
)

from app.frontend.events.registration_details.ENTRY_edit_registration_details import (
    display_form_edit_registration_details,
)
from app.frontend.events.view_individual_event_form import get_event_form_for_event, group_allocation_button, \
    edit_registration_button, volunteer_rota_button, patrol_boat_allocation_button, food_button, clothing_button, \
    import_registration_data_button
from app.frontend.events.volunteer_rota.ENTRY1_display_main_rota_page import (
    display_form_view_for_volunteer_rota,
)
from app.frontend.events.patrol_boats.ENTRY_allocate_patrol_boats import (
    display_form_view_for_patrol_boat_allocation,
)
from app.frontend.events.food.ENTRY_food import display_form_view_for_food_requirements
from app.frontend.events.clothing.ENTRY_clothing import (
    display_form_view_for_clothing_requirements,
)

from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_lines import (
    Line,
)
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    back_menu_button,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.form_handler import button_error_and_back_to_initial_state_form

from app.frontend.shared.events_state import get_event_from_state


def display_form_view_individual_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    form = get_event_form_for_event(event, interface=interface)

    return form


def post_form_view_individual_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set

    last_button_pressed = interface.last_button_pressed()
    if back_menu_button.pressed(last_button_pressed):
        return previous_form(interface)

    elif import_registration_data_button.pressed(last_button_pressed):
        return form_to_upload_event_file(interface)

    elif group_allocation_button.pressed(last_button_pressed):
        return form_to_do_cadet_allocation(interface)

    elif edit_registration_button.pressed(last_button_pressed):
        return form_to_edit_registration_details(interface)

    elif volunteer_rota_button.pressed(last_button_pressed):
        return form_to_do_volunteer_rota(interface)

    elif patrol_boat_allocation_button.pressed(last_button_pressed):
        return form_to_allocate_patrol_boats(interface)

    elif food_button.pressed(last_button_pressed):
        return form_to_allocate_food(interface)

    elif clothing_button.pressed(last_button_pressed):
        return form_to_do_clothing(interface)

    else:
        button_error_and_back_to_initial_state_form(interface)


def row_of_form_for_event_with_buttons(event) -> Line:
    return Line(Button(str(event)))


def form_to_upload_event_file(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_choose_import_source)


def form_to_do_cadet_allocation(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_allocate_cadets)


def form_to_edit_registration_details(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_edit_registration_details)


def form_to_do_volunteer_rota(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_view_for_volunteer_rota
    )  ## check rota before going to form


def form_to_allocate_patrol_boats(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_view_for_patrol_boat_allocation
    )


def form_to_allocate_food(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_view_for_food_requirements
    )


def form_to_do_clothing(interface: abstractInterface):
    return interface.get_new_form_given_function(
        display_form_view_for_clothing_requirements
    )


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        post_form_view_individual_event
    )


