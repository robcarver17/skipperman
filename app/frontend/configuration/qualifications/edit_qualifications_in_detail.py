from typing import Union, List

from app.OLD_backend.ticks_and_qualifications.edit_qualifications import get_tick_items_as_dict_for_qualification

from app.frontend.configuration.qualifications.edit_qualifications_in_detail_form import table_for_edit_qualification_details, \
    button_for_new_substage, list_of_button_names_for_new_item_in_substage_name_field
from app.frontend.configuration.qualifications.edit_qualifications_in_stage_parse import \
    add_new_substage_to_qualification_from_form, add_new_tick_list_item_from_form, \
    save_edited_values_in_qualifications_form
from app.objects_OLD.abstract_objects.abstract_text import Heading

from app.objects_OLD.abstract_objects.abstract_buttons import ButtonBar, cancel_menu_button, save_menu_button

from app.objects.abstract_objects.abstract_lines import ListOfLines

from app.frontend.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.frontend.shared.qualification_and_tick_state_storage import (
    get_qualification_from_state,
)
from app.objects_OLD.abstract_objects.abstract_form import Form, NewForm
from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface


def display_form_edit_qualification_details(interface: abstractInterface) -> Form:
    qualification = get_qualification_from_state(interface)
    navbar = ButtonBar([cancel_menu_button, save_menu_button])
    heading = Heading(
        "Edit qualification elements for %s" % qualification.name, centred=True, size=5
    )
    table = table_for_edit_qualification_details(
        interface=interface, qualification=qualification
    )
    return Form(ListOfLines([navbar, heading, table]).add_Lines())


def post_form_edit_qualification_details(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()



    if cancel_menu_button.pressed(last_button_pressed):
        return interface.get_new_display_form_for_parent_of_function(
            display_form_edit_qualification_details
        )
    if button_for_new_substage.pressed(last_button_pressed):
        add_new_substage_to_qualification_from_form(interface)
    elif last_button_pressed in get_new_item_in_substage_button_names(interface):
        add_new_tick_list_item_from_form(interface=interface, button_pressed=last_button_pressed)
    elif save_menu_button.pressed(last_button_pressed):
        save_edited_values_in_qualifications_form(interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()
    return display_form_edit_qualification_details(interface)

def get_new_item_in_substage_button_names(interface: abstractInterface) -> List[str]:
    qualification = get_qualification_from_state(interface)
    tick_items_as_dict = get_tick_items_as_dict_for_qualification(
        data_layer=interface.data, qualification=qualification
    )
    return list_of_button_names_for_new_item_in_substage_name_field(
        tick_items_as_dict=tick_items_as_dict
    )


