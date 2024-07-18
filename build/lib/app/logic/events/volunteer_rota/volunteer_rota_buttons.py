from typing import List

from app.OLD_backend.forms.swaps import is_ready_to_swap
from app.logic.shared.events_state import get_event_from_state
from app.logic.events.volunteer_rota.swapping import get_list_of_swap_buttons, cancel_swap_button
from app.logic.events.volunteer_rota.button_values import get_list_of_day_button_values, \
    get_list_of_make_available_button_values, get_list_of_copy_overwrite_buttons_for_individual_volunteers, \
    get_list_of_copy_fill_buttons_for_individual_volunteers, get_list_of_remove_role_buttons, \
    get_list_of_make_unavailable_buttons, list_of_all_copy_previous_roles_buttons, \
    get_dict_of_volunteer_name_buttons_and_volunteer_ids, list_of_all_location_button_names, list_of_all_skills_buttons
from app.logic.volunteers.ENTRY_view_volunteers import all_sort_types as all_volunteer_name_sort_types
from app.objects.abstract_objects.abstract_buttons import Button, ButtonBar, cancel_menu_button, save_menu_button, \
    HelpButton
from app.objects.abstract_objects.abstract_interface import abstractInterface


def was_volunteer_name_sort_button_pressed(interface: abstractInterface):
    all_buttons = get_volunteer_name_sort_buttons()

    return any([button.pressed(interface.last_button_pressed()) for button in all_buttons])

def get_all_volunteer_sort_buttons():
    name_sort_buttons = get_volunteer_name_sort_buttons()

    return [sort_by_cadet_location_button] + name_sort_buttons


SORT_BY_CADET_LOCATION = "Sort by cadet location"
sort_by_cadet_location_button = Button(SORT_BY_CADET_LOCATION, nav_button=True)


def get_volunteer_name_sort_buttons() -> List[Button]:
    return [
        Button(sort_by, nav_button=True) for sort_by in all_volunteer_name_sort_types
    ]


APPLY_FILTER_BUTTON_LABEL = "Apply filters"
CLEAR_FILTERS_BUTTON_LABEL = "Clear all filters"
COPY_ALL_ROLES_BUTTON_LABEL = "Copy from earliest allocated role to fill empty roles"
COPY_ALL_FIRST_ROLE_BUTTON_LABEL = (
    "Copy from earliest allocated role to fill empty and overwrite existing roles"
)
ADD_NEW_VOLUNTEER_BUTTON_LABEL = "Add new volunteer to rota"
apply_filter_button = Button(APPLY_FILTER_BUTTON_LABEL, nav_button=True)
clear_filter_button = Button(CLEAR_FILTERS_BUTTON_LABEL, nav_button=True)
add_volunteer_button = Button(ADD_NEW_VOLUNTEER_BUTTON_LABEL, nav_button=True)
copy_all_roles_button = Button(COPY_ALL_ROLES_BUTTON_LABEL, nav_button=True)
copy_all_first_role_button = Button(COPY_ALL_FIRST_ROLE_BUTTON_LABEL, nav_button=True)
download_matrix_button = Button(
    "Download spreadsheet of volunteer information", nav_button=True
)


def get_header_buttons_for_rota(interface: abstractInterface):
    if is_ready_to_swap(interface):
        return ButtonBar([cancel_swap_button, help_button])
    else:
        return ButtonBar(
            [
                cancel_menu_button,
                save_menu_button,
                add_volunteer_button,
                copy_all_roles_button,
                copy_all_first_role_button,
                download_matrix_button,
                help_button,
            ]
        )

def get_buttons_after_rota_table_if_swapping():
    return ButtonBar([cancel_swap_button, help_button])

def get_buttons_after_rota_table_if_not_swapping():
    return ButtonBar(
        [
            cancel_menu_button,
            save_menu_button,
            add_volunteer_button,
            help_button,
        ]
    )

help_button = HelpButton("volunteer_rota_help")

def last_button_pressed_was_volunteer_name_button(interface: abstractInterface) -> bool:
    last_button = interface.last_button_pressed()

    return last_button in get_list_of_volunteer_name_buttons(interface)


def get_list_of_volunteer_name_buttons(interface: abstractInterface) -> list:
    event = get_event_from_state(interface)
    volunteer_name_buttons_dict = get_dict_of_volunteer_name_buttons_and_volunteer_ids(
        interface=interface, event=event
    )
    list_of_volunteer_name_buttons = list(volunteer_name_buttons_dict.keys())

    return list_of_volunteer_name_buttons


def last_button_pressed_was_day_sort_button(interface: abstractInterface):
    return interface.last_button_pressed() in get_all_day_sort_buttons(interface)


def get_all_day_sort_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)

    return get_list_of_day_button_values(event)


def last_button_pressed_was_location_button(interface: abstractInterface)->bool:
    return interface.last_button_pressed() in get_all_location_buttons(interface)


def get_all_location_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_location_buttons = list_of_all_location_button_names(
        interface=interface, event=event
    )

    return all_location_buttons


def last_button_pressed_was_skill_button(interface: abstractInterface):
    return interface.last_button_pressed() in get_all_skill_buttons(interface)


def get_all_skill_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_skill_buttons = list_of_all_skills_buttons(interface=interface, event=event)

    return all_skill_buttons


def get_all_copy_previous_role_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_copy_previous_role_buttons = list_of_all_copy_previous_roles_buttons(
        interface=interface, event=event
    )

    return all_copy_previous_role_buttons


def get_all_copy_overwrite_individual_role_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)

    return get_list_of_copy_overwrite_buttons_for_individual_volunteers(
        interface=interface, event=event
    )


def get_all_copy_fill_individual_role_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)

    return get_list_of_copy_fill_buttons_for_individual_volunteers(
        interface=interface, event=event
    )


def last_button_pressed_was_make_available_button(interface: abstractInterface):
    return interface.last_button_pressed() in get_all_make_available_buttons(interface)


def get_all_make_available_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)
    all_buttons = get_list_of_make_available_button_values(
        interface=interface, event=event
    )

    return all_buttons


def last_button_pressed_was_copy_button(interface: abstractInterface):
    return interface.last_button_pressed() in get_all_copy_buttons(interface)


def get_all_copy_buttons(interface: abstractInterface):
    return (
        get_all_copy_overwrite_individual_role_buttons(interface)
        + get_all_copy_fill_individual_role_buttons(interface)
        + [COPY_ALL_ROLES_BUTTON_LABEL, COPY_ALL_FIRST_ROLE_BUTTON_LABEL]
        + get_all_copy_previous_role_buttons(interface)
    )


def last_button_pressed_was_swap_button(interface: abstractInterface):
    if cancel_swap_button.pressed(interface.last_button_pressed()):
        return True
    else:
        return interface.last_button_pressed() in get_all_swap_buttons(interface)


def get_all_swap_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)
    return get_list_of_swap_buttons(interface=interface, event=event)



def last_button_pressed_was_remove_role_button(interface: abstractInterface):
    return interface.last_button_pressed() in get_all_remove_role_buttons(interface)


def get_all_remove_role_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)
    return get_list_of_remove_role_buttons(interface=interface, event=event)


def last_button_pressed_was_make_unavailable_button(interface: abstractInterface):
    return interface.last_button_pressed() in get_all_make_unavailable_buttons(interface)


def get_all_make_unavailable_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)
    return get_list_of_make_unavailable_buttons(interface=interface, event=event)
