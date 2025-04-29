from copy import copy
from dataclasses import dataclass
from typing import Union, Callable

from app.frontend.shared.buttons import get_button_value_given_type_and_attributes, \
    get_attributes_from_button_pressed_of_known_type, is_button_of_type
from app.objects.abstract_objects.abstract_tables import Table, RowInTable

from app.frontend.forms.form_utils import yes_no_radio, is_radio_yes_or_no
from app.frontend.forms.reorder_form import (
    UP,
    DOWN,
    get_button_name_to_move_in_list,
    modify_list_given_button_name, is_button_arrow_button,
)
from app.data_access.configuration.fixed import (
    SAVE_KEYBOARD_SHORTCUT,
    ADD_KEYBOARD_SHORTCUT,
)
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    textInput,
    radioInput,
)
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    cancel_menu_button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.objects.abstract_objects.abstract_text import up_arrow, down_arrow, Heading
from app.objects.utilities.exceptions import MISSING_FROM_FORM
from app.objects.utilities.utils import has_hidden_attribute, is_protected_object

ADD_ENTRY_TEXT_FIELD = "add_entry_text_field"
SAVE_ENTRY_BUTTON_LABEL = "Save edits to existing"
ADD_ENTRY_BUTTON_LABEL = "Add new entry"


def row_for_new_entries() -> RowInTable:
    text_input = textInput(
        input_name=ADD_ENTRY_TEXT_FIELD, input_label="New entry", value=""
    )

    return RowInTable([text_input, add_button])


def get_row_for_existing_entry(entry, include_edit_button: bool = False) -> RowInTable:
    protected = is_protected_object(entry)
    if protected:
        line = [
            "Protected - cannot edit: %s" % entry.name,
        ]
    else:
        line = [
            text_box_for_entry(entry),
        ]

    if include_edit_button:
        line.append(edit_contents_button(entry))
    if has_hidden_attribute(entry):
        line.append(hide_button_for_entry(entry))

    line.append(Line([up_button_for_entry(entry), down_button_for_entry(entry)]))

    return RowInTable(line)


def get_object_from_form(interface: abstractInterface, existing_object):
    new_name = interface.value_from_form(text_box_name(existing_object))

    object_class = existing_object.__class__
    if has_hidden_attribute(existing_object):
        is_hidden = is_radio_yes_or_no(
            interface=interface, input_name=hidden_box_name(existing_object)
        )

        if is_hidden is MISSING_FROM_FORM:
            print("hidden missing frrom form for %s" % str(existing_object))
            is_hidden = existing_object.hidden

        return object_class(name=new_name, hidden=is_hidden)
    else:
        return object_class(new_name)


BACK_BUTTON_PRESSED = object()
BUTTON_NOT_KNOWN = object()
REORDER_PRESSED = object()
SAVE_OR_ADD_PRESSED = object()

def display_form_edit_generic_list(
    existing_list: list,
    header_text: str,
    include_edit_button: bool = False,
    function_for_existing_entry_row: Callable = get_row_for_existing_entry,
) -> Union[Form, NewForm]:
    existing_entries = rows_for_existing_entries(
        function_for_existing_entry_row=function_for_existing_entry_row,
        existing_list=existing_list,
        include_edit_button=include_edit_button,
    )
    new_entries = row_for_new_entries()
    existing_entries.append(new_entries)

    navbar = ButtonBar([cancel_menu_button, save_button, help_button])

    return Form(
        [
            ListOfLines(
                [
                    navbar,
                    Heading(header_text, centred=True, size=4),
                    _______________,
                    existing_entries,
                    _______________,
                    navbar,
                ]
            )
        ]
    )


save_button = Button(
    SAVE_ENTRY_BUTTON_LABEL,
    nav_button=True,
    shortcut=SAVE_KEYBOARD_SHORTCUT,
)

add_button = Button(
    ADD_ENTRY_BUTTON_LABEL, nav_button=True, shortcut=ADD_KEYBOARD_SHORTCUT
)

help_button = HelpButton("configuration_help")


def rows_for_existing_entries(
    existing_list: list,
    function_for_existing_entry_row: Callable = get_row_for_existing_entry,
    include_edit_button: bool = False,
) -> Table:
    return Table(
        [
            function_for_existing_entry_row(
                entry, include_edit_button=include_edit_button
            )
            for entry in existing_list
        ]
    )


def up_button_for_entry(entry):
    return Button(label=up_arrow, value=get_button_name_to_move_in_list(str(entry), UP))


def down_button_for_entry(entry):
    return Button(
        label=down_arrow, value=get_button_name_to_move_in_list(str(entry), DOWN)
    )


def text_box_for_entry(entry) -> textInput:
    return textInput(
        value=str(entry), input_label="Edit name", input_name=text_box_name(entry)
    )


def hide_button_for_entry(entry) -> radioInput:
    return yes_no_radio(
        input_name=hidden_box_name(entry),
        input_label="Hide in dropdown lists",
        default_to_yes=entry.hidden,
    )


EDIT_NAME_FLAG = "edit"
HIDE_BUTTON_FLAG = "hide"


def text_box_name(entry) -> str:
    return EDIT_NAME_FLAG + "_" + str(entry)


def hidden_box_name(entry) -> str:
    return HIDE_BUTTON_FLAG + "_" + str(entry)

edit_button_type="editButton"

def edit_contents_button(entry_name: str) -> Button:
    return Button("Edit", value=name_of_edit_contents_button_name(entry_name))

def name_of_edit_contents_button_name(entry_name: str) -> str:
    return get_button_value_given_type_and_attributes(edit_button_type, entry_name)


def entry_name_from_edit_contents_button(button_pressed: str) -> str:
    return get_attributes_from_button_pressed_of_known_type(value_of_button_pressed=button_pressed,
                                                                  type_to_check=edit_button_type)

def is_edit_button_pressed(button_pressed_str) -> bool:
    print(button_pressed_str)
    return is_button_of_type(value_of_button_pressed=button_pressed_str, type_to_check=edit_button_type)


@dataclass
class EditButtonPressed:
    entry_name: str




def post_form_edit_generic_list(
    interface: abstractInterface,
    existing_list: list,
    header_text: str,
    ## functions need to take string and return new list of objects_OLD
    adding_function: Callable,
    modifying_function: Callable,
    save_function: Callable,
    get_object_from_form_function: Callable = get_object_from_form,
) -> Union[Form, NewForm, object, EditButtonPressed]:
    last_button = interface.last_button_pressed()

    if cancel_menu_button.pressed(last_button):
        return BACK_BUTTON_PRESSED
    elif is_edit_button_pressed(last_button):
        return EditButtonPressed(entry_name_from_edit_contents_button(last_button))
    elif is_button_arrow_button(last_button):
        reorder_list_given_form(
            interface=interface,
            save_function=save_function,
            existing_list=existing_list,
        )
        return REORDER_PRESSED

    add_edits_from_form(
            interface=interface,
            modifying_function=modifying_function,
            existing_list=existing_list,
            get_object_from_form_function=get_object_from_form_function,
        )

    if save_button.pressed(last_button):
        ## already saved
        pass

    elif add_button.pressed(last_button):
        add_new_entry_from_form(interface=interface, adding_function=adding_function)

    else:
        return BUTTON_NOT_KNOWN

    return SAVE_OR_ADD_PRESSED


def edit_button_returned_from_generic_modifier(content):
    return type(content) is EditButtonPressed

def get_list_of_edit_contents_buttons(existing_list):
    return [name_of_edit_contents_button_name(entry) for entry in existing_list]


def get_list_of_arrow_buttons(existing_list: list):
    return [get_button_name_to_move_in_list(entry, UP) for entry in existing_list] + [
        get_button_name_to_move_in_list(entry, DOWN) for entry in existing_list
    ]


def add_new_entry_from_form(interface: abstractInterface, adding_function: Callable):
    name_of_entry_to_add = interface.value_from_form(ADD_ENTRY_TEXT_FIELD)
    if len(name_of_entry_to_add) > 0:
        ## functions need to take string and return new list of objects_OLD
        try:
            adding_function(
                object_store=interface.object_store,
                name_of_entry_to_add=name_of_entry_to_add,
            )
        except Exception as e:
            interface.log_error("Error when adding new entry: %s" % str(e))


def add_edits_from_form(
    interface: abstractInterface,
    modifying_function: Callable,
    existing_list: list,
    get_object_from_form_function: Callable = get_object_from_form,
):
    try:
        add_edits_from_form_without_error_logging(
            interface=interface,
            modifying_function=modifying_function,
            existing_list=existing_list,
            get_object_from_form_function=get_object_from_form_function,
        )

    except Exception as e:
        interface.log_error("Error when modifying: %s" % (str(e)))

        interface.clear_cache()


def add_edits_from_form_without_error_logging(
    interface: abstractInterface,
    modifying_function: Callable,
    existing_list: list,
    get_object_from_form_function: Callable = get_object_from_form,
):
    for existing_object in existing_list:
        edit_specific_object_in_form(
            interface=interface,
            modifying_function=modifying_function,
            existing_object=existing_object,
            get_object_from_form_function=get_object_from_form_function,
        )


def edit_specific_object_in_form(
    interface: abstractInterface,
    modifying_function: Callable,
    existing_object,
    get_object_from_form_function: Callable = get_object_from_form,
):
    protected = is_protected_object(existing_object)
    if protected:
        return

    new_object = get_object_from_form_function(
        interface=interface,
        existing_object=existing_object,
    )

    if new_object == existing_object:
        return

    modifying_function(
        object_store=interface.object_store,
        existing_object=existing_object,
        new_object=new_object,
    )


def reorder_list_given_form(
    interface: abstractInterface,
    save_function: Callable,
    existing_list: list,
):
    try:
        new_list = re_order_return_list(
            button_name=interface.last_button_pressed(), existing_list=existing_list
        )
        save_function(object_store=interface.object_store, new_list=new_list)
    except Exception as e:
        interface.log_error("Error when reordering entry %s: " % str(e))
        new_list = copy(existing_list)

    return new_list


def re_order_return_list(button_name: str, existing_list: list):
    current_list_of_str = [str(item) for item in existing_list]
    new_list_of_str_ordered = modify_list_given_button_name(
        button_name=button_name, current_order=current_list_of_str
    )

    new_list_idx = [
        current_list_of_str.index(str_item) for str_item in new_list_of_str_ordered
    ]
    new_list = [existing_list[idx] for idx in new_list_idx]

    return new_list
