from typing import Union, List

from app.data_access.store.object_store import ObjectStore

from app.backend.qualifications_and_ticks.list_of_qualifications import (
    get_list_of_qualifications,
    update_list_of_qualifications,
    add_new_qualification,
    modify_qualification,
)

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.configuration.qualifications.edit_qualifications_in_detail import (
    display_form_edit_qualification_details,
)
from app.frontend.configuration.generic_list_modifier import (
    display_form_edit_generic_list,
    post_form_edit_generic_list,
    BACK_BUTTON_PRESSED,
    BUTTON_NOT_KNOWN,
    edit_button_returned_from_generic_modifier,
)
from app.frontend.shared.qualification_and_tick_state_storage import (
    update_state_for_qualification_name,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.qualifications import Qualification, ListOfQualifications

header_text = "List of qualifications and ticks: add, edit, re-order. Re-ordering or clicking edit button will cancel any other changes made since saving."


def display_form_config_qualifications_page(interface: abstractInterface) -> Form:
    list_of_qualifications = get_list_of_qualifications(
        interface.object_store
    ).list_of_names()

    return display_form_edit_generic_list(
        existing_list=list_of_qualifications,
        header_text=header_text,
        include_edit_button=True,
    )


def post_form_config_qualifications_page(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    list_of_qualifications = get_list_of_qualifications(interface.object_store)

    interface.lock_cache()

    generic_list_output = post_form_edit_generic_list(
        existing_list=list_of_qualifications,
        interface=interface,
        header_text=header_text,
        adding_function=add_new_qualification,
        modifying_function=modify_qualification,
        save_function=save_from_ordinary_list_of_qualifications,
    )

    if generic_list_output is BACK_BUTTON_PRESSED:
        return interface.get_new_display_form_for_parent_of_function(
            post_form_config_qualifications_page
        )

    if edit_button_returned_from_generic_modifier(generic_list_output):
        update_state_for_qualification_name(
            interface=interface, qualification_name=generic_list_output.entry_name
        )
        return interface.get_new_form_given_function(
            display_form_edit_qualification_details
        )
    elif generic_list_output is BUTTON_NOT_KNOWN:
        return button_error_and_back_to_initial_state_form(interface)

    interface.save_changes_in_cached_data_to_disk()

    return interface.get_new_form_given_function(
        display_form_config_qualifications_page
    )


def save_from_ordinary_list_of_qualifications(
    object_store: ObjectStore, new_list: List[Qualification]
):
    update_list_of_qualifications(
        object_store=object_store,
        updated_list_of_qualifications=ListOfQualifications(new_list),
    )
