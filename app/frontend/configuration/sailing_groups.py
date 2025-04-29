from typing import Union, List

from app.frontend.forms.form_utils import is_radio_yes_or_no
from app.objects.abstract_objects.abstract_tables import RowInTable

from app.objects.abstract_objects.abstract_lines import Line

from app.objects.utilities.exceptions import arg_not_passed, MISSING_FROM_FORM

from app.objects.groups import Group, ListOfGroups, all_locations_for_input

from app.data_access.store.object_store import ObjectStore

from app.backend.groups.list_of_groups import (
    get_list_of_groups,
    update_list_of_groups,
    modify_sailing_group,
    add_new_sailing_group_given_name,
)
from app.frontend.configuration.generic_list_modifier import (
    BACK_BUTTON_PRESSED,
    BUTTON_NOT_KNOWN,
    up_button_for_entry,
    down_button_for_entry,
    text_box_name,
    hide_button_for_entry,
    display_form_edit_generic_list,
    post_form_edit_generic_list,
    hidden_box_name,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    textInput,
    dropDownInput,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface


header_text = "List of sailing groups: add, edit, re-order. Re-ordering will cancel any other changes made since saving."


def display_form_config_sailing_groups(interface: abstractInterface) -> Form:
    list_of_groups = get_list_of_groups(interface.object_store)

    return display_form_edit_generic_list(
        existing_list=list_of_groups,
        header_text=header_text,
        function_for_existing_entry_row=get_row_for_existing_entry,
    )


def post_form_config_sailing_groups(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    list_of_groups = get_list_of_groups(interface.object_store)

    generic_list_output = post_form_edit_generic_list(
        existing_list=list_of_groups,
        interface=interface,
        header_text=header_text,
        adding_function=add_new_sailing_group_given_name,
        modifying_function=modify_sailing_group,
        save_function=save_from_ordinary_list_of_groups,
        get_object_from_form_function=get_group_from_form,
    )

    if generic_list_output is BACK_BUTTON_PRESSED:
        return interface.get_new_display_form_for_parent_of_function(
            post_form_config_sailing_groups
        )
    elif generic_list_output is BUTTON_NOT_KNOWN:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return interface.get_new_form_given_function(display_form_config_sailing_groups)


def get_row_for_existing_entry(entry: Group, **kwargs_to_ignore) -> RowInTable:
    if entry.protected:
        return RowInTable(["Protected cannot edit: ", entry.name])
    line = [
        text_box_for_group_name(entry),
        dropdown_for_location(entry),
        hide_button_for_entry(entry),
        Line([up_button_for_entry(entry), down_button_for_entry(entry)]),
    ]

    return RowInTable(line)


dict_of_location_options = dict(
    [(location.name, location.name) for location in all_locations_for_input]
)


def text_box_for_group_name(entry: Group) -> textInput:
    return textInput(
        value=str(entry), input_label="Edit name", input_name=text_box_name(entry)
    )


def location_box_name(entry: Group = arg_not_passed) -> str:
    return LOCATION_FIELD_NAME + "_" + entry.name


def dropdown_for_location(entry: Group) -> dropDownInput:
    default_label = entry.location.name
    location_input = dropDownInput(
        input_label="Location",
        input_name=location_box_name(entry),
        dict_of_options=dict_of_location_options,
        default_label=default_label,
    )
    return location_input


LOCATION_FIELD_NAME = "location"


def get_group_from_form(
    interface: abstractInterface, existing_object, **kwargs_ignored
) -> Group:
    new_group_name = interface.value_from_form(text_box_name(existing_object))
    new_location = interface.value_from_form(location_box_name(existing_object))
    is_hidden = is_radio_yes_or_no(
        interface=interface, input_name=hidden_box_name(existing_object)
    )
    if is_hidden is MISSING_FROM_FORM:
        print("hidden missing for %s" % str(existing_object))
        is_hidden = existing_object.hidden

    new_group = Group(
        name=new_group_name, location=new_location, protected=False, hidden=is_hidden
    )
    return new_group


def save_from_ordinary_list_of_groups(object_store: ObjectStore, new_list: List[Group]):
    update_list_of_groups(
        object_store=object_store, updated_list_of_groups=ListOfGroups(new_list)
    )
