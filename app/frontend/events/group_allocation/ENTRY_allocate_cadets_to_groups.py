from typing import Union

from app.backend.events.list_of_events import get_list_of_events
from app.frontend.events.group_allocation.add_unregistered_cadet import display_add_unregistered_cadet_from_allocation_form
from app.frontend.forms.reorder_form import (
    list_of_button_names_given_group_order,
    reorderFormInterface,
)
from app.objects.day_selectors import Day
from app.frontend.shared.cadet_state import (
    clear_cadet_state,
    update_state_for_specific_cadet_id,
    is_cadet_set_in_state,
)

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.events.group_allocation.add_cadet_partner import (
    display_add_cadet_partner,
)
from app.frontend.events.group_allocation.store_state import (
    set_day_in_state,
    no_day_set_in_state,
    clear_day_in_state,
    SORT_ORDER,
    get_current_sort_order,
)
from app.frontend.events.group_allocation.render_allocation_form import (
    display_form_allocate_cadets_at_event,
    get_list_of_all_add_partner_buttons,
    list_of_all_day_button_names,
    get_list_of_all_add_cadet_availability_buttons,
    get_list_of_all_cadet_buttons,
    cadet_id_from_cadet_button,
    reset_day_button,
    add_button
)
from app.frontend.events.group_allocation.input_fields import (
    cadet_id_given_partner_button,
)
from app.frontend.events.group_allocation.parse_allocation_form import (
    update_data_given_allocation_form,
    make_cadet_available_on_current_day,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
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
        interface.clear_cache()
        return previous_form(interface)

    elif save_menu_button.pressed(last_button):
        ## This also saves the stored data in interface otherwise we don't do it later if add partner button saved
        update_data_given_allocation_form(interface)
    elif add_button.pressed(last_button):
        return interface.get_new_form_given_function(display_add_unregistered_cadet_from_allocation_form)

    elif was_add_partner_button(interface):
        ### SAVE CADET ID TO GET PARTNER FOR
        ## DISPLAY NEW FORM
        cadet_id = cadet_id_given_partner_button(last_button)
        update_state_for_specific_cadet_id(interface=interface, cadet_id=cadet_id)
        return interface.get_new_form_given_function(display_add_cadet_partner)

    elif last_button in get_list_of_all_add_cadet_availability_buttons(interface):
        make_cadet_available_on_current_day(
            interface=interface, add_availability_button_name=last_button
        )

    elif last_button in get_list_of_all_cadet_buttons(interface):
        cadet_button_clicked(interface)

    elif last_button in list_of_all_day_button_names(interface):
        change_day_and_save(interface=interface, day_button=last_button)

    elif was_reorder_sort_button(interface):
        change_sort_order_and_save(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return interface.get_new_form_given_function(display_form_allocate_cadets)


def was_add_partner_button(interface: abstractInterface) -> bool:
    button = interface.last_button_pressed()
    all_partner_buttons = get_list_of_all_add_partner_buttons(interface)
    return button in all_partner_buttons


def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(
        display_form_allocate_cadets
    )


def was_reorder_sort_button(interface: abstractInterface):
    current_sort_order = get_current_sort_order(interface=interface)
    last_button = interface.last_button_pressed()
    sort_buttons = list_of_button_names_given_group_order(current_sort_order)

    return last_button in sort_buttons


def change_sort_order_and_save(interface: abstractInterface):
    ## Change in order of list
    current_sort_order = get_current_sort_order(interface=interface)
    reorder_form_interface = reorderFormInterface(
        interface, current_order=current_sort_order
    )

    new_sort_order = reorder_form_interface.new_order_of_list()
    save_new_order(interface=interface, new_sort_order=new_sort_order)


def change_day_and_save(interface: abstractInterface, day_button: str):
    if reset_day_button.pressed(day_button):
        clear_day_in_state(interface)
        return

    try:
        day = Day[day_button]
    except:
        raise Exception("Don't recognise day button %s " % day_button)

    set_day_in_state(interface=interface, day=day)


def save_new_order(interface: abstractInterface, new_sort_order: list):
    interface.set_persistent_value(SORT_ORDER, new_sort_order)


def cadet_button_clicked(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    cadet_id = cadet_id_from_cadet_button(last_button)
    if is_cadet_set_in_state(interface):
        clear_cadet_state(interface)
    else:
        print("seeting cadet id to %s" % cadet_id)
        update_state_for_specific_cadet_id(interface=interface, cadet_id=cadet_id)
