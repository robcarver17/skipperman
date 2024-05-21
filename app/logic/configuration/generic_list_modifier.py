from copy import copy
from typing import Union,  Callable

from app.backend.forms.reorder_form import UP, DOWN, get_button_name_to_move_in_list, modify_list_given_button_name
from app.objects.abstract_objects.abstract_form import Form, NewForm, textInput
from app.objects.abstract_objects.abstract_buttons import Button, BACK_CANCEL_BUTTON_LABEL, ButtonBar
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.objects.abstract_objects.abstract_text import  up_arrow, down_arrow, Heading

ADD_ENTRY_TEXT_FIELD = "add_entry_text_field"
SAVE_ENTRY_BUTTON_LABEL = "Save edits to existing and/or add new entry"



def display_form_edit_generic_list(
    existing_list: list,
        header_text: str
) -> Union[Form, NewForm]:

    existing_entries = rows_for_existing_entries(existing_list)
    new_entries = row_for_new_entries()
    navbar = ButtonBar([Button(BACK_CANCEL_BUTTON_LABEL, nav_button=True)])
    footer_buttons = ButtonBar([ Button(SAVE_ENTRY_BUTTON_LABEL, nav_button=True)])

    return Form([
        ListOfLines([
            navbar,
            Heading(header_text, centred=True, size=4),
            _______________,
            existing_entries,
            new_entries,
            _______________,
            footer_buttons
        ])
    ])

def rows_for_existing_entries(existing_list: list) -> ListOfLines:

    return ListOfLines([
        get_row_for_existing_entry(entry) for entry in existing_list
    ])


def get_row_for_existing_entry(entry) -> Line:
    return Line(
        [ text_box_for_entry(entry), up_button_for_entry(entry), down_button_for_entry(entry)]
    )

def up_button_for_entry(entry):
    return Button(label=up_arrow, value = get_button_name_to_move_in_list(str(entry), UP))

def down_button_for_entry(entry):
    return Button(label=down_arrow, value =get_button_name_to_move_in_list(str(entry), DOWN))


def text_box_for_entry(entry)-> textInput:
    return textInput(
        value=str(entry),
        input_label="Edit",
        input_name=text_box_name(entry)
    )

EDIT_FLAG = "edit"
def text_box_name(entry) -> str:
    return EDIT_FLAG+" "+str(entry)


def button_str_for_deletion(entry):
    return "Delete %s" % str(entry)

def deleted_button_name_from_button_str(button_str: str) -> str:
    entry_name = " ".join(button_str.split(" ")[1:])
    return entry_name

def row_for_new_entries() -> Line:
    text_input = textInput(input_name=ADD_ENTRY_TEXT_FIELD,
                           input_label="New entry",
                           value="")

    return Line([text_input])

BACK_BUTTON_PRESSED = object()
BUTTON_NOT_KNOWN = object()

def post_form_edit_generic_list(
    interface: abstractInterface,
        existing_list: list,
        header_text: str,
        ## functions need to take string and return new list of objects
        adding_function: Callable,
        deleting_function: Callable,
        modifying_function: Callable,
        save_function: Callable
) -> Union[Form, NewForm, object]:

    button = interface.last_button_pressed()
    ### Buttons are back; delete button for individual cadet connection; add to add a new connection
    list_of_delete_buttons = get_list_of_delete_entry_buttons(existing_list)
    list_of_arrow_buttons = get_list_of_arrow_buttons(existing_list)

    if button==BACK_CANCEL_BUTTON_LABEL:
        return BACK_BUTTON_PRESSED

    elif button==SAVE_ENTRY_BUTTON_LABEL:
        updated_list = add_new_entry_and_edits_from_form_and_return_updated_list(interface=interface, adding_function=adding_function,
                                                                                 modifying_function=modifying_function, existing_list=existing_list)
    elif button in list_of_delete_buttons:
        updated_list = delete_entry_given_form_and_return_updated_list(interface=interface, deleting_function=deleting_function,
                                                                       existing_list=existing_list)
    elif button in list_of_arrow_buttons:
        updated_list = reorder_list_given_form_and_return_updated_list(interface=interface,
                                                                        save_function=save_function,
                                                                       existing_list=existing_list)
    else:
        return BUTTON_NOT_KNOWN

    interface.save_stored_items()

    ## might want to do more
    return display_form_edit_generic_list(existing_list=updated_list, header_text=header_text)

def get_list_of_delete_entry_buttons(existing_list: list):

    return [button_str_for_deletion(entry) for entry in existing_list]

def get_list_of_arrow_buttons(existing_list: list):

    return [get_button_name_to_move_in_list(entry, UP) for entry in existing_list]+\
            [get_button_name_to_move_in_list(entry, DOWN) for entry in existing_list]


def add_new_entry_and_edits_from_form_and_return_updated_list(interface: abstractInterface,
                                                    adding_function: Callable,
                                                    modifying_function: Callable,
                                                    existing_list: list
                                                    ) -> list:

    ## DO EDITS FIRST, OR WILL BREAK WHEN TRYING TO EDIT AN ADDED ITEM
    new_list_with_edits = add_edits_from_form_and_return_updated_list(interface=interface,
                                                           modifying_function=modifying_function,
                                                           existing_list=existing_list)

    new_list_with_additions = add_new_entry_from_form_and_return_updated_list(interface=interface,
                                                               adding_function=adding_function,
                                                               existing_list=new_list_with_edits)

    return new_list_with_additions


def add_new_entry_from_form_and_return_updated_list(interface: abstractInterface,
                                                    adding_function: Callable,
                                                    existing_list: list
                                                    ) -> list:

    entry_to_add = interface.value_from_form(ADD_ENTRY_TEXT_FIELD)
    if len(entry_to_add)>0:
        ## functions need to take string and return new list of objects
        try:
            new_list = adding_function(interface=interface, entry_to_add=entry_to_add)
            return new_list
        except Exception as e:
            interface.log_error("Error when adding new entry: %s" % str(e))

    return existing_list


def add_edits_from_form_and_return_updated_list(interface: abstractInterface,
                                                    modifying_function: Callable,
                                                    existing_list: list
                                                    ) -> list:

    new_list = copy(existing_list)
    for existing_object in new_list:
        existing_as_str = str(existing_object)
        edited_value_str = interface.value_from_form(text_box_name(existing_object))
        if edited_value_str==existing_as_str:
            continue
        try:
            new_list = modifying_function(interface=interface, existing_value_as_str = existing_as_str, new_value_as_str = edited_value_str)
        except Exception as e:
            interface.log_error("Error when modifying %s to %s: %s" % (existing_as_str, edited_value_str, str(e)))

    return new_list


def delete_entry_given_form_and_return_updated_list(interface: abstractInterface,
                                                    deleting_function: Callable,
                                                    existing_list: list
                                                    ) -> list:

    entry_to_delete = deleted_button_name_from_button_str(interface.last_button_pressed())
    try:
        new_list = deleting_function(interface=interface, entry_to_delete=entry_to_delete)
    except Exception as e:
        interface.log_error("Error when deleting entry %s: " % str(e))
        new_list = copy(existing_list)

    return new_list

def reorder_list_given_form_and_return_updated_list(interface: abstractInterface,
                                                    save_function: Callable,
                                                    existing_list: list,
                                                    ) -> list:
    try:
        new_list = re_order_return_list(button_name=interface.last_button_pressed(), existing_list=existing_list)
        save_function(interface=interface, new_list=new_list)
    except Exception as e:
        interface.log_error("Error when reordering entry %s: " % str(e))
        new_list = copy(existing_list)

    return new_list

def re_order_return_list(button_name: str, existing_list: list):
    current_list_of_str = [str(item) for item in existing_list]
    new_list_of_str_ordered = modify_list_given_button_name(button_name=button_name,
                                             current_order=current_list_of_str)

    new_list_idx = [current_list_of_str.index(str_item) for str_item in new_list_of_str_ordered]
    new_list= [existing_list[idx] for idx in new_list_idx]

    return new_list

