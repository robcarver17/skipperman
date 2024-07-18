from typing import Union, List

from app.objects.abstract_objects.abstract_text import Heading

from app.objects.abstract_objects.abstract_tables import Table, RowInTable

from app.objects.abstract_objects.abstract_buttons import ButtonBar, cancel_menu_button, save_menu_button, \
    back_menu_button, Button

from app.OLD_backend.ticks_and_qualifications.edit_qualifications import (
    get_tick_items_as_dict_for_qualification,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line

from app.logic.abstract_logic_api import button_error_and_back_to_initial_state_form
from app.logic.shared.qualification_and_tick_state_storage import (
    get_qualification_from_state,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm, textInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.qualifications import Qualification
from app.objects.ticks import TickSubStage, TickSubStagesAsDict, ListOfTickSheetItems, TickSheetItem

header_text = "List of qualifications: add, edit, re-order"


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


def table_for_edit_qualification_details(
    interface: abstractInterface, qualification: Qualification
) -> Table:
    tick_items_as_dict = get_tick_items_as_dict_for_qualification(
        data_layer=interface.data, qualification=qualification
    )

    table =[]
    for substage in tick_items_as_dict.keys():
        table+=get_table_elements_for_substage_in_table(substage=substage, tick_items_as_dict=tick_items_as_dict)

    table.append(row_to_add_substage_in_table(interface))

    return Table(table)


def get_table_elements_for_substage_in_table(substage: TickSubStage,  tick_items_as_dict: TickSubStagesAsDict) -> List[RowInTable]:
    first_row = first_row_for_substage_in_table(substage)
    tick_items_this_substage = tick_items_as_dict[substage]
    rows_for_existing = [row_for_tickitem_in_table(tick_sheet_item) for tick_sheet_item in tick_items_this_substage]
    final_row = final_row_for_substage_in_table(substage)

    return [first_row]+rows_for_existing+[final_row]

def first_row_for_substage_in_table(substage: TickSubStage) -> RowInTable:
    text_input=textInput(
        input_label="Edit name of substage",
        input_name=name_of_edit_substage_field(substage),
        value=substage.name
    )
    return RowInTable([text_input, 'Tick items in sub-stage: %s:' % substage.name])

def name_of_edit_substage_field(substage: TickSubStage):
    return "EDITSS_%s" % substage.id

def row_for_tickitem_in_table(tick_sheet_item: TickSheetItem):
    text_input=textInput(
        input_label="Edit tick item:",
        input_name=name_of_edit_tickitem_field(tick_sheet_item),
        value=tick_sheet_item.name
    )

    return RowInTable(['',text_input])

def name_of_edit_tickitem_field(tick_sheet_item: TickSheetItem):
    return "EDITTI_%s" % tick_sheet_item.id

def final_row_for_substage_in_table(substage: TickSubStage) -> RowInTable:
    ### AUTOCORRECT
    entry_field = textInput(
        input_label="New tick item for sub-stage %s:" % substage.name,
        input_name=fieldname_for_new_item_in_substage_name(substage),
        value=''
    )
    button = button_for_new_item_in_substage_name(substage)
    return RowInTable(['',Line([entry_field, button])])

def fieldname_for_new_item_in_substage_name(substage: TickSubStage) -> str:
    return "NEWTICKITEM_%s" % substage.id

def button_for_new_item_in_substage_name(substage: TickSubStage) -> Button:
    return Button("Add", value=button_value_for_new_item_in_substage_name(substage))


def button_value_for_new_item_in_substage_name(substage: TickSubStage) -> str:
    return "ADD_ITEM_BUTTON_%s" % substage.id

def row_to_add_substage_in_table(interface: abstractInterface) -> RowInTable:
    ## need interface for autocomplete
    ### AUTOCORRECT
    entry_field = textInput(
        input_label="New substage for qualification",
        input_name=FIELDNAME_FOR_NEW_SUBSTAGE_TEXT_BOX,
        value=''
    )
    button = button_for_new_substage()
    return RowInTable(['',Line([entry_field, button])])


FIELDNAME_FOR_NEW_SUBSTAGE_TEXT_BOX = "SUBSTAGENEW"

def button_for_new_substage() -> Button:
    return Button("Add", value=ADD_NEW_SUBSTAGE_BUTTON_VALUE)

ADD_NEW_SUBSTAGE_BUTTON_VALUE = "ADDSUBSTAGE"

def post_form_edit_qualification_details(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()
    if cancel_menu_button.pressed(last_button_pressed):
        return interface.get_new_display_form_for_parent_of_function(
            display_form_edit_qualification_details
        )

    elif save_menu_button.pressed(last_button_pressed):
        ## save and show form again
        interface.flush_cache_to_store()
        return display_form_edit_qualification_details(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)