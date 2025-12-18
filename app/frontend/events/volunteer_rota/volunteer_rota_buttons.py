from typing import List

from app.objects.volunteers import SORT_BY_SURNAME, SORT_BY_FIRSTNAME
from app.data_access.configuration.fixed import ADD_KEYBOARD_SHORTCUT
from app.frontend.events.volunteer_rota.button_values import (
    last_button_was_copy_previous_role,
    last_button_pressed_was_copyover_button,
    last_button_pressed_was_copyfill_button,
)
from app.frontend.events.volunteer_rota.rota_state import SortParameters
from app.frontend.forms.swaps import is_ready_to_swap

from app.frontend.events.volunteer_rota.swapping import (
    cancel_swap_button,
)
from app.frontend.shared.buttons import (
    get_button_value_given_type_and_attributes,
    get_attributes_from_button_pressed_of_known_type,
)
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    cancel_menu_button,
    save_menu_button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.utilities.exceptions import arg_not_passed

from app.frontend.shared.buttons import sort_button_type


def get_header_buttons_for_rota(interface: abstractInterface):
    if is_ready_to_swap(interface):
        return ButtonBar([cancel_swap_button, help_button])
    else:
        return ButtonBar(
            [
                cancel_menu_button,
                save_menu_button,
                add_volunteer_button,
                access_copy_menu,
                download_matrix_button,
                quick_report_button,
                update_most_common_role_button,
                help_button,
            ]
        )


quick_report_button = Button("Quick report", nav_button=True)
update_most_common_role_button = Button("Update most common role", nav_button=True)

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


def get_sort_parameters_from_buttons(button_pressed: str) -> SortParameters:
    sort_by_volunteer_name = arg_not_passed
    sort_by_day = arg_not_passed
    sort_by_location = False
    attributes = get_attributes_from_button_pressed_of_known_type(
        value_of_button_pressed=button_pressed,
        type_to_check=sort_button_type,
        collapse_singleton=False,
    )  ## ensures a list always returned

    first_attribute = attributes[0]
    if first_attribute == sort_by_location_marker:
        sort_by_location = True
    elif first_attribute == sort_by_day_marker:
        day_name_to_sort_by = attributes[1]
        sort_by_day = Day[day_name_to_sort_by]
    elif first_attribute == sort_by_name_marker:
        sort_by = attributes[1]
        sort_by_volunteer_name = sort_by
    else:
        raise Exception("Unknown sort button %s pressed" % button_pressed)

    sort_parameters = SortParameters(
        sort_by_day=sort_by_day,
        sort_by_location=sort_by_location,
        sort_by_volunteer_name=sort_by_volunteer_name,
    )
    print(sort_parameters)

    return sort_parameters


def get_all_volunteer_sort_buttons():
    name_sort_buttons = get_volunteer_name_sort_buttons()

    return [sort_by_cadet_location_button] + name_sort_buttons


sort_by_location_marker = "SortByLocation"

SORT_BY_CADET_LOCATION = "Sort by cadet location"
sort_by_cadet_location_button = Button(
    SORT_BY_CADET_LOCATION,
    nav_button=True,
    value=get_button_value_given_type_and_attributes(
        sort_button_type, sort_by_location_marker
    ),
)

sort_by_name_marker = "SortByVolName"


def get_volunteer_name_sort_buttons() -> List[Button]:
    return [
        Button(
            sort_by,
            nav_button=True,
            value=get_button_value_given_type_and_attributes(
                sort_button_type, sort_by_name_marker, sort_by
            ),
        )
        for sort_by in all_volunteer_name_sort_types
    ]


all_volunteer_name_sort_types = [SORT_BY_SURNAME, SORT_BY_FIRSTNAME]


APPLY_FILTER_BUTTON_LABEL = "Apply filters"
CLEAR_FILTERS_BUTTON_LABEL = "Clear all filters"
ADD_NEW_VOLUNTEER_BUTTON_LABEL = "Add new volunteer to rota"
apply_filter_button = Button(APPLY_FILTER_BUTTON_LABEL, nav_button=True)
clear_filter_button = Button(CLEAR_FILTERS_BUTTON_LABEL, nav_button=True)
add_volunteer_button = Button(
    ADD_NEW_VOLUNTEER_BUTTON_LABEL, nav_button=True, shortcut=ADD_KEYBOARD_SHORTCUT
)
access_copy_menu = Button(
    "Copy and/or overwrite roles from first available day", nav_button=True
)
download_matrix_button = Button(
    "Download spreadsheet of volunteer information", nav_button=True
)


help_button = HelpButton("volunteer_rota_help")


sort_by_day_marker = "SortByDay"


def get_buttons_for_days_at_event(event: Event, ready_to_swap: bool):
    if ready_to_swap:
        return event.days_in_event_as_list_of_string()
    else:
        return [
            Line([button_for_day(day), " (click to sort group/role)"])
            for day in event.days_in_event()
        ]


def button_for_day(day: Day) -> Button:
    return Button(day.name, value=button_value_for_day(day))


def button_value_for_day(day: Day):
    return get_button_value_given_type_and_attributes(
        sort_button_type, sort_by_day_marker, day.name
    )


## COPYS
def last_button_pressed_was_copy_button(copy_button: str):
    return (
        last_button_was_copy_previous_role(copy_button)
        or last_button_pressed_was_copyover_button(copy_button)
        or last_button_pressed_was_copyfill_button(copy_button)
    )
