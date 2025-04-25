from typing import List

from app.backend.cadets.list_of_cadets import get_cadet_from_id
from app.backend.events.list_of_events import get_event_from_id
from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_buttons import ButtonBar, cancel_menu_button, Button
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.cadets import Cadet
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteers import Volunteer


day_button_type = "dayButton"

def get_button_value_for_day_button_with_non_day_value(value:str):
    return get_button_value_given_type_and_attributes(day_button_type, value)


def get_button_value_for_day(day: Day):
    return get_button_value_given_type_and_attributes(day_button_type, day.name)

def is_button_day_select(value_of_button_pressed: str):
    return is_button_of_type(type_to_check=day_button_type, value_of_button_pressed=value_of_button_pressed)

def get_day_from_button_pressed(value_of_button_pressed:str):
    day_name = get_day_name_or_value_from_button_pressed(value_of_button_pressed)
    return Day[day_name]

def get_day_name_or_value_from_button_pressed(value_of_button_pressed:str):
    attributes = get_attributes_from_button_pressed_of_known_type(value_of_button_pressed=value_of_button_pressed, type_to_check=day_button_type)
    return attributes


sort_button_type = "sortButton"



def get_button_value_for_sort_order(sort_order:str):
    return get_button_value_given_type_and_attributes(sort_button_type, sort_order)

def is_button_sort_order(value_of_button_pressed: str):
    return is_button_of_type(type_to_check=sort_button_type, value_of_button_pressed=value_of_button_pressed)


def sort_order_from_button_pressed(value_of_button_pressed:str):
    attributes = get_attributes_from_button_pressed_of_known_type(value_of_button_pressed=value_of_button_pressed, type_to_check=sort_button_type)
    return attributes

volunteer_button_type="volunteerSelect"



def get_button_value_for_volunteer_selection(volunteer: Volunteer):
    return get_button_value_given_type_and_attributes(volunteer_button_type, volunteer.id)

def is_button_volunteer_selection(value_of_button_pressed: str):
    return is_button_of_type(type_to_check=volunteer_button_type, value_of_button_pressed=value_of_button_pressed)

def volunteer_from_button_pressed(object_store: ObjectStore, value_of_button_pressed:str):
    volunteer_id =volunteer_id_from_button_pressed(value_of_button_pressed)

    return get_volunteer_from_id(object_store=object_store, volunteer_id=volunteer_id)

def volunteer_id_from_button_pressed(value_of_button_pressed:str):
    return get_attributes_from_button_pressed_of_known_type(value_of_button_pressed=value_of_button_pressed, type_to_check=volunteer_button_type)

cadet_button_type = "cadetselect"

def get_button_value_for_cadet_selection(cadet: Cadet):
    return get_button_value_given_type_and_attributes(cadet_button_type, cadet.id)

def is_button_cadet_selection(value_of_button_pressed: str):
    return is_button_of_type(type_to_check=cadet_button_type, value_of_button_pressed=value_of_button_pressed)

def cadet_from_button_pressed(object_store: ObjectStore, value_of_button_pressed:str):
    cadet_id =cadet_id_from_button_pressed(value_of_button_pressed)

    return get_cadet_from_id(object_store=object_store, cadet_id=cadet_id)

def cadet_id_from_button_pressed(value_of_button_pressed:str):
    return get_attributes_from_button_pressed_of_known_type(value_of_button_pressed=value_of_button_pressed, type_to_check=cadet_button_type)

event_button_type = "eventSelect"

def get_button_value_for_event_selection(event: Event):
    return get_button_value_given_type_and_attributes(event_button_type, event.id)

def is_button_event_selection(value_of_button_pressed: str):
    return is_button_of_type(type_to_check=event_button_type, value_of_button_pressed=value_of_button_pressed)

def event_from_button_pressed(object_store: ObjectStore, value_of_button_pressed:str):
    event_id =event_id_from_button_pressed(value_of_button_pressed)

    return get_event_from_id(object_store=object_store, event_id=event_id)

def event_id_from_button_pressed(value_of_button_pressed:str):
    return get_attributes_from_button_pressed_of_known_type(value_of_button_pressed=value_of_button_pressed, type_to_check=event_button_type)




SPLITTER="^"

def get_button_value_given_type_and_attributes(button_type: str, *args):
    return SPLITTER.join([button_type]+list(args))

def get_type_and_attributes_from_button_pressed(value_of_button_pressed: str) -> List[str]:
    return value_of_button_pressed.split(SPLITTER)

def is_button_of_type(value_of_button_pressed:str, type_to_check: str):
    type_of_button = get_type_of_button_pressed(value_of_button_pressed)

    types_match= type_of_button==type_to_check
    return types_match

def get_type_of_button_pressed(value_of_button_pressed:str):
    type_and_attributes = get_type_and_attributes_from_button_pressed(value_of_button_pressed)
    type_of_button = type_and_attributes[0]

    return type_of_button

def get_attributes_from_button_pressed_of_known_type(value_of_button_pressed:str, type_to_check: str, collapse_singleton=True):
    type_and_attributes = get_type_and_attributes_from_button_pressed(value_of_button_pressed)
    type_of_button = type_and_attributes.pop(0)
    if not type_of_button==type_to_check:
        raise Exception("%s not of type %s instead %s" % (value_of_button_pressed, type_to_check, type_of_button))
    if len(type_and_attributes)==1 and collapse_singleton:
        return type_and_attributes[0]

    return type_and_attributes


def get_nav_bar_with_just_cancel_button() -> ButtonBar:
    return ButtonBar([cancel_menu_button])


def break_up_buttons(list_of_buttons: List[Button], first_line: int=3, chunk_size: int = 6) -> ListOfLines:
    first_chunk = list_of_buttons[:first_line]
    rest_of_list = list_of_buttons[first_line:]
    chunks = ['', first_chunk,'', '']
    for i in range(0, len(rest_of_list), chunk_size):
        chunks.append(rest_of_list[i:i + chunk_size])
    return ListOfLines(chunks).add_Lines()
