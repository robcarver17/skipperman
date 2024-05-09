from copy import copy
from typing import Union

from app.backend.forms.reorder_form import list_of_button_names_given_group_order, reorderFormInterface
from app.backend.group_allocations.sorting import DEFAULT_SORT_ORDER, SORT_GROUP
from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.events.constants import UPDATE_ALLOCATION_BUTTON_LABEL
from app.logic.events.group_allocation.add_cadet_partner import display_add_cadet_partner
from app.logic.events.group_allocation.store_state import set_day_in_state
from app.logic.events.group_allocation.render_allocation_form import display_form_allocate_cadets_at_event, \
    list_of_all_add_partner_buttons, day_and_cadet_id_given_partner_button
from app.logic.events.group_allocation.parse_allocation_form import update_data_given_allocation_form
from app.logic.events.cadets_at_event.track_cadet_id_in_state_when_importing import save_cadet_id_at_event
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

from app.logic.events.events_in_state import get_event_from_state


def display_form_allocate_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    sort_order = get_current_sort_order(interface=interface)
    return display_form_allocate_cadets_at_event(interface=interface, event=event, sort_order=sort_order)

SORT_ORDER = 'sort_order'

def get_current_sort_order(interface: abstractInterface)-> list:
    event = get_event_from_state(interface)
    default_order = copy(DEFAULT_SORT_ORDER)
    if not event.contains_groups:
        default_order.remove(SORT_GROUP)
    return interface.get_persistent_value(SORT_ORDER, default=DEFAULT_SORT_ORDER)


def post_form_allocate_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    last_button = interface.last_button_pressed()
    if last_button == BACK_BUTTON_LABEL:
        return previous_form(interface)

    ## This also saves the stored data in interface otherwise we don't do it later if add partner button saved
    update_data_given_allocation_form(interface)

    if was_add_partner_button(interface):
        ### SAVE CADET ID TO GET PARTNER FOR
        ## DISPLAY NEW FORM
        day, cadet_id = day_and_cadet_id_given_partner_button(last_button)
        save_cadet_id_at_event(interface=interface, cadet_id=cadet_id)
        set_day_in_state(interface=interface, day=day)
        return interface.get_new_form_given_function(display_add_cadet_partner)

    elif was_reorder_sort_button(interface):
        change_sort_order_and_save(interface)
    elif last_button == UPDATE_ALLOCATION_BUTTON_LABEL:
        ## already saved
        pass
    else:
        return button_error_and_back_to_initial_state_form(interface)

    return interface.get_new_form_given_function(display_form_allocate_cadets)

def was_add_partner_button(interface: abstractInterface)->bool:
    button = interface.last_button_pressed()
    all_partner_buttons = list_of_all_add_partner_buttons(interface)
    return button in all_partner_buttons

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_allocate_cadets)


def was_reorder_sort_button(interface: abstractInterface):
    current_sort_order = get_current_sort_order(interface=interface)
    last_button = interface.last_button_pressed()
    sort_buttons= list_of_button_names_given_group_order(current_sort_order)

    return last_button in sort_buttons

def change_sort_order_and_save(interface: abstractInterface):
    ## Change in order of list
    current_sort_order = get_current_sort_order(interface=interface)
    reorder_form_interface = reorderFormInterface(
        interface, current_order=current_sort_order
    )

    new_sort_order = reorder_form_interface.new_order_of_list()
    save_new_order(interface=interface, new_sort_order=new_sort_order)

def save_new_order(interface: abstractInterface, new_sort_order: list):
    interface.set_persistent_value(SORT_ORDER, new_sort_order)
