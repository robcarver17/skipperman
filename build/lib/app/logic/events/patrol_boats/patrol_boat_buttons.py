from typing import List, Tuple, Callable

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.dinghies import load_list_of_patrol_boats_at_event, load_list_of_patrol_boats_at_event_from_cache
from app.OLD_backend.rota.patrol_boats import (
    get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day,
)
from app.data_access.configuration.fixed import REMOVE_SHORTHAND, ADD_KEYBOARD_SHORTCUT
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.primtive_with_id.patrol_boats import PatrolBoat


def get_list_of_generic_buttons_for_each_volunteer_day_combo(
    interface: abstractInterface, event: Event, button_name_function: Callable
) -> List[str]:
    list_of_button_names = []
    for day in event.weekdays_in_event():
        list_of_volunteer_ids = (
            get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day(
                interface=interface, event=event, day=day
            )
        )
        for volunteer_id in list_of_volunteer_ids:
            list_of_button_names.append(
                button_name_function(day=day, volunteer_id=volunteer_id)
            )
    return list_of_button_names


def generic_button_name_for_volunteer_in_boat_at_event_on_day(
    button_type: str, day: Day, volunteer_id: str
) -> str:
    return "%s_%s_%s" % (button_type, day.name, volunteer_id)


def get_button_type_day_volunteer_id_given_button_str(
    copy_both_button: str,
) -> Tuple[str, Day, str]:
    splitter = copy_both_button.split("_")
    button_type, day_name, volunteer_id = splitter

    return button_type, Day[day_name], volunteer_id


def delete_button_for_boat_value(boat_at_event: PatrolBoat) -> str:
    return "DELETE_" + str(boat_at_event)


def from_delete_button_name_to_boat_name(button_name: str) -> str:
    boat_name = button_name.split("_")[1]
    return boat_name


def list_of_delete_buttons_in_patrol_boat_table(
    interface: abstractInterface, event: Event
) -> List[str]:
    list_of_boats_at_event = load_list_of_patrol_boats_at_event_from_cache(
        cache=interface.cache, event=event
    )
    return [
        delete_button_for_boat_value(boat_at_event)
        for boat_at_event in list_of_boats_at_event
    ]


def get_remove_volunteer_button(day: Day, volunteer_id: str) -> Button:
    return Button(
        label=DELETE_VOLUNTEER_BUTTON_LABEL,
        value=get_remove_volunteer_button_name(day=day, volunteer_id=volunteer_id),
    )


def get_remove_volunteer_button_name(day: Day, volunteer_id: str) -> str:
    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        button_type="removeVolunteer", day=day, volunteer_id=volunteer_id
    )


def from_volunter_remove_button_name_to_volunteer_id_and_day(
    button_name: str,
) -> Tuple[str, Day]:
    __, day, volunteer_id = get_button_type_day_volunteer_id_given_button_str(
        button_name
    )

    return volunteer_id, day


def get_all_remove_volunteer_button_names(
    interface: abstractInterface, event: Event
) -> List[str]:
    return get_list_of_generic_buttons_for_each_volunteer_day_combo(
        interface=interface,
        event=event,
        button_name_function=get_remove_volunteer_button_name,
    )


DELETE_BOAT_BUTTON_LABEL = "Remove boat from rota"
DELETE_VOLUNTEER_BUTTON_LABEL = REMOVE_SHORTHAND
COPY_ALL_BOATS_BUTTON_LABEL = (
    "Copy and fill all boats from earliest allocated boat across days"
)
COPYOVER_ALL_BOATS_BUTTON_LABEL = (
    "Copy, fill and overwrite all boats from earliest allocated boat"
)
COPY_BOATS_AND_ROLES_BUTTON_LABEL = (
    "Copy and fill all boats and roles from earliest allocated boat and role"
)
COPYOVER_BOATS_AND_ROLES_BUTTON_LABEL = (
    "Copy, fill and overwrite all boats and roles from earliest allocated boat and role"
)
copy_all_boats_button = Button(COPY_ALL_BOATS_BUTTON_LABEL, nav_button=True)
copyover_all_boats_button = Button(COPYOVER_ALL_BOATS_BUTTON_LABEL, nav_button=True)
copy_all_boats_and_roles_button = Button(
    COPY_BOATS_AND_ROLES_BUTTON_LABEL, nav_button=True
)
copyover_all_boats_and_roles_button = Button(
    COPYOVER_BOATS_AND_ROLES_BUTTON_LABEL, nav_button=True
)
ADD_NEW_BOAT_BUTTON_LABEL = "Add new boat"
add_new_boat_button=Button(ADD_NEW_BOAT_BUTTON_LABEL, shortcut=ADD_KEYBOARD_SHORTCUT)
