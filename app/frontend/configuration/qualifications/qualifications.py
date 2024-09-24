from typing import Union, List

from app.OLD_backend.configuration import (
    load_list_of_qualifications,
    save_list_of_qualifications,
    add_new_qualification_given_string_and_return_list,
    delete_qualification_given_string_and_return_list,
    modify_qualification_given_string_and_return_list,
)

from app.frontend.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.frontend.configuration.qualifications.edit_qualifications_in_detail import (
    display_form_edit_qualification_details,
)
from app.frontend.configuration.generic_list_modifier import (
    display_form_edit_generic_list,
    post_form_edit_generic_list,
    BACK_BUTTON_PRESSED,
    BUTTON_NOT_KNOWN,
    edit_button_pressed,
)
from app.frontend.shared.qualification_and_tick_state_storage import (
    update_state_for_qualification_name,
)
from app.objects_OLD.abstract_objects.abstract_form import Form, NewForm
from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface
from app.objects_OLD.qualifications import Qualification, ListOfQualifications

header_text = "List of qualifications: add, edit, re-order"


def display_form_config_qualifications_page(interface: abstractInterface) -> Form:
    list_of_qualifications = load_list_of_qualifications(interface)

    return display_form_edit_generic_list(
        existing_list=list_of_qualifications,
        header_text=header_text,
        include_edit_button=True,
    )


def post_form_config_qualifications_page(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    list_of_qualifications = load_list_of_qualifications(interface)

    generic_list_output = post_form_edit_generic_list(
        existing_list=list_of_qualifications,
        interface=interface,
        header_text=header_text,
        deleting_function=delete_qualification_given_string_and_return_list,
        adding_function=add_new_qualification_given_string_and_return_list,
        modifying_function=modify_qualification_given_string_and_return_list,
        save_function=save_from_ordinary_list_of_qualifications,
    )

    if generic_list_output is BACK_BUTTON_PRESSED:
        return interface.get_new_display_form_for_parent_of_function(
            post_form_config_qualifications_page
        )
    elif edit_button_pressed(generic_list_output):
        update_state_for_qualification_name(
            interface=interface, qualification_name=generic_list_output.entry_name
        )
        return interface.get_new_form_given_function(
            display_form_edit_qualification_details
        )
    elif generic_list_output is BUTTON_NOT_KNOWN:
        return button_error_and_back_to_initial_state_form(interface)

    return display_form_config_qualifications_page(interface=interface)


def save_from_ordinary_list_of_qualifications(
    interface: abstractInterface, new_list: List[Qualification]
):
    save_list_of_qualifications(
        interface=interface, list_of_qualifications=ListOfQualifications(new_list)
    )
