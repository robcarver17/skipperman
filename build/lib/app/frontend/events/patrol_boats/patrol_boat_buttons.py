from typing import Tuple

from app.backend.patrol_boats.list_of_patrol_boats import get_patrol_boat_from_id
from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id

from app.objects.volunteers import Volunteer

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.data_access.configuration.fixed import REMOVE_SHORTHAND, ADD_KEYBOARD_SHORTCUT
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.day_selectors import Day
from app.objects.patrol_boats import PatrolBoat
from app.frontend.shared.buttons import get_attributes_from_button_pressed_of_known_type, is_button_of_type, get_button_value_given_type_and_attributes


def generic_button_name_for_volunteer_in_boat_at_event_on_day(
    button_type: str, day: Day, volunteer_id: str
) -> str:
    return get_button_value_given_type_and_attributes(
        button_type,
        day.name,
        volunteer_id
    )


def get_day_and_volunteer_given_button_of_type(
    interface: abstractInterface, button_name: str, button_type: str
) -> Tuple[Day, Volunteer]:
    day_name, volunteer_id  = get_attributes_from_button_pressed_of_known_type(
        value_of_button_pressed=button_name,
        type_to_check=button_type
    )

    volunteer = get_volunteer_from_id(
        object_store=interface.object_store, volunteer_id=volunteer_id
    )

    return Day[day_name], volunteer

def get_day_and_patrol_boat_given_button_of_type(
    interface: abstractInterface, button_name: str, button_type: str
) -> Tuple[Day, PatrolBoat]:
    day_name, patrol_boat_id  = get_attributes_from_button_pressed_of_known_type(
        value_of_button_pressed=button_name,
        type_to_check=button_type
    )

    patrol_boat =  get_patrol_boat_from_id(object_store=interface.object_store, boat_id=patrol_boat_id)
    return Day[day_name], patrol_boat

delete_button_type = "deleteBoatButton"

def delete_button_for_boat_value(boat_at_event: PatrolBoat) -> str:
    return get_button_value_given_type_and_attributes(delete_button_type, boat_at_event.name)


def from_delete_button_name_to_boat_name(button_name: str) -> str:
    return get_attributes_from_button_pressed_of_known_type(value_of_button_pressed=button_name, type_to_check=delete_button_type)

def is_delete_boat_button(button_name:str):
    return is_button_of_type(type_to_check=delete_button_type,value_of_button_pressed=button_name)


def get_remove_volunteer_button(day: Day, volunteer_id: str) -> Button:
    return Button(
        label=DELETE_VOLUNTEER_BUTTON_LABEL,
        value=get_remove_volunteer_button_name(day=day, volunteer_id=volunteer_id),
    )

remove_button_type = "removeVolunteer"

def get_remove_volunteer_button_name(day: Day, volunteer_id: str) -> str:
    return generic_button_name_for_volunteer_in_boat_at_event_on_day(
        button_type=remove_button_type, day=day, volunteer_id=volunteer_id
    )


def from_volunter_remove_button_name_to_volunteer_and_day(
    interface: abstractInterface,
    button_name: str,
) -> Tuple[Volunteer, Day]:
    day, volunteer = get_day_and_volunteer_given_button_of_type(
        interface=interface, button_name=button_name,
        button_type=remove_button_type
    )

    return volunteer, day

def is_delete_volunteer_button(button_value: str):
    return is_button_of_type(value_of_button_pressed=button_value, type_to_check=remove_button_type)


DELETE_BOAT_BUTTON_LABEL = "Remove boat from rota"
DELETE_VOLUNTEER_BUTTON_LABEL = REMOVE_SHORTHAND

ADD_NEW_BOAT_BUTTON_LABEL = "Add new boat"
add_new_boat_button = Button(ADD_NEW_BOAT_BUTTON_LABEL, shortcut=ADD_KEYBOARD_SHORTCUT)
