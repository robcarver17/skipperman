from copy import copy

from app.backend.cadets.list_of_cadets import get_cadet_from_id
from app.data_access.store.object_store import ObjectStore
from app.frontend.events.group_allocation.store_state import no_day_set_in_state, get_day_from_state_or_none
from app.frontend.shared.buttons import get_button_value_for_day, get_button_value_for_day_button_with_non_day_value, \
    get_button_value_for_cadet_selection, get_button_value_given_type_and_attributes, \
    get_attributes_from_button_pressed_of_known_type, is_button_of_type

from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.cadets import Cadet
from app.objects.day_selectors import Day
from app.objects.exceptions import missing_data
from app.objects.partners import no_partnership_given_partner_cadet_as_str


def get_day_buttons(interface: abstractInterface) -> Line:
    event = get_event_from_state(interface)
    event_weekdays = copy(event.days_in_event())
    all_buttons  = [get_button_for_specific_day(day) for day in event_weekdays]

    if no_day_set_in_state(interface):
        message = "  Choose day to edit (if you want to allocate cadets to different groups, boats or partners on specific days): "
    else:
        day = get_day_from_state_or_none(interface)
        message = "Currently editing %s: " % day.name
        idx_of_current_day = event_weekdays.index(day)
        all_buttons.pop(idx_of_current_day)
        all_buttons = [reset_day_button] + all_buttons

    return Line([message] + all_buttons)

def get_button_for_specific_day(day: Day):
    return Button(day.name, value = get_button_value_for_day(day))



def button_to_click_on_cadet(cadet: Cadet):
    return Button(str(cadet), value=get_button_value_for_cadet_selection(cadet))



RESET_DAY_BUTTON_LABEL = "Show all day view"
reset_day_button = Button(RESET_DAY_BUTTON_LABEL, value = get_button_value_for_day_button_with_non_day_value(RESET_DAY_BUTTON_LABEL))

MAKE_CADET_AVAILABLE_ON_DAY_BUTTON = "Cadet not sailing today - click to change"

def get_make_available_button(cadet: Cadet):
    return Button(
        label=MAKE_CADET_AVAILABLE_ON_DAY_BUTTON,
        value=make_cadet_available_button_name(cadet),
    )

def make_cadet_available_button_name(cadet: Cadet):
    return get_button_value_given_type_and_attributes(MAKE_CADET_AVAILABLE_ON_DAY_BUTTON, cadet.id)

def get_cadet_from_cadet_available_buttons(object_store: ObjectStore, button_str:str):
    cadet_id = cadet_id_from_cadet_available_buttons(button_str)
    cadet = get_cadet_from_id(object_store=object_store, cadet_id=cadet_id)

    return cadet

def cadet_id_from_cadet_available_buttons(button_str: str):
    return get_attributes_from_button_pressed_of_known_type(value_of_button_pressed=button_str, type_to_check=MAKE_CADET_AVAILABLE_ON_DAY_BUTTON)

def is_make_available_button(button_str:str):
    return is_button_of_type(type_to_check=MAKE_CADET_AVAILABLE_ON_DAY_BUTTON, value_of_button_pressed=button_str)


def get_button_for_partnership_cell(cadet: Cadet, potential_partner_to_be_added_or_missing_data: str,  current_partner_name: str):
    if potential_partner_to_be_added_or_missing_data is missing_data:
        if no_partnership_given_partner_cadet_as_str(current_partner_name):
            return ""
        else:
            button = Button(
                value = button_name_for_delete_partner(cadet),
                label = "Remove partnership"
            )

    else:
        button= Button(
            value=button_name_for_add_partner(cadet),
            label="Add %s as new cadet" % potential_partner_to_be_added_or_missing_data,
        )

    return button

add_button_partner_type="addPartner"
delete_partner_button_type= "deletePartner"

def button_name_for_add_partner(cadet: Cadet):
    return get_button_value_given_type_and_attributes(add_button_partner_type, cadet.id )


def button_name_for_delete_partner(cadet: Cadet):
    return get_button_value_given_type_and_attributes(delete_partner_button_type, cadet.id )

def was_remove_partner_button(buttone) -> bool:
    return is_button_of_type(type_to_check=delete_partner_button_type, value_of_button_pressed=buttone)

def was_add_partner_button(buttone) -> bool:
    return is_button_of_type(type_to_check=add_button_partner_type, value_of_button_pressed=buttone)


def get_cadet_given_remove_partner_button_name(object_store: ObjectStore, button:str):
    cadet_id = get_attributes_from_button_pressed_of_known_type(value_of_button_pressed=button, type_to_check=delete_partner_button_type)
    return get_cadet_from_id(object_store=object_store, cadet_id=cadet_id)

def get_cadet_given_add_partner_button_name(object_store: ObjectStore,button:str):
    cadet_id = get_attributes_from_button_pressed_of_known_type(value_of_button_pressed=button, type_to_check=add_button_partner_type)
    return get_cadet_from_id(object_store=object_store, cadet_id=cadet_id)

