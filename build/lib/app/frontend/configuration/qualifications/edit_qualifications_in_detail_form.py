from typing import List

from app.backend.qualifications_and_ticks.list_of_substages import AutoCorrectForQualificationEdit, \
    get_suggestions_for_autocorrect
from app.backend.qualifications_and_ticks.dict_of_qualifications_substages_and_ticks import \
    get_tick_items_as_dict_for_qualification
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import textInput, listInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import Line
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.qualifications import Qualification
from app.objects.substages import TickSubStage, TickSheetItem
from app.objects.composed.ticks_in_dicts import TickSubStagesAsDict


def table_for_edit_qualification_details(
    interface: abstractInterface, qualification: Qualification
) -> Table:
    tick_items_as_dict = get_tick_items_as_dict_for_qualification(
        data_layer=interface.data, qualification=qualification
    )
    suggestions = get_suggestions_for_autocorrect(data_layer = interface.data, qualification=qualification)

    table =[]
    for substage in tick_items_as_dict.keys():
        table+=get_table_elements_for_substage_in_table(substage=substage, tick_items_as_dict=tick_items_as_dict, suggestions=suggestions)

    table.append(row_to_add_substage_in_table(suggestions=suggestions))

    return Table(table)


def get_table_elements_for_substage_in_table(substage: TickSubStage,  tick_items_as_dict: TickSubStagesAsDict, suggestions: AutoCorrectForQualificationEdit) -> List[RowInTable]:
    first_row = first_row_for_substage_in_table(substage, suggestions=suggestions)
    tick_items_this_substage = tick_items_as_dict[substage]
    rows_for_existing = [row_for_tickitem_in_table(tick_sheet_item) for tick_sheet_item in tick_items_this_substage]
    final_row = final_row_for_substage_in_table(substage)

    return [first_row]+rows_for_existing+[final_row]


def first_row_for_substage_in_table(substage: TickSubStage, suggestions: AutoCorrectForQualificationEdit) -> RowInTable:
    text_input=listInput(
        input_label="Edit name of substage (delete to see suggestions)",
        input_name=name_of_edit_substage_field(substage),
        default_option=substage.name,
        list_of_options=suggestions.substage_names
    )
    return RowInTable([text_input, 'Tick items in sub-stage: %s:' % substage.name])


def list_of_names_of_edit_substage_name_field(tick_items_as_dict: TickSubStagesAsDict):
    all_names = [name_of_edit_substage_field(substage)
    for substage in tick_items_as_dict.keys()]

    return all_names


def name_of_edit_substage_field(substage: TickSubStage):
    return "EDITSS_%s" % substage.id


def row_for_tickitem_in_table(tick_sheet_item: TickSheetItem):
    text_input=textInput(
        input_label="Edit tick item:",
        input_name=name_of_edit_tickitem_field(tick_sheet_item),
        value=tick_sheet_item.name
    )

    return RowInTable(['',text_input])


def list_of_names_of_edit_tickitem_field(tick_items_as_dict: TickSubStagesAsDict):
    all_names = []
    for substage in tick_items_as_dict.keys():
        all_names+=list_of_names_of_edit_tickitem_fields_for_substage(substage=substage, tick_items_as_dict=tick_items_as_dict)

    return all_names

def list_of_names_of_edit_tickitem_fields_for_substage(substage: TickSubStage, tick_items_as_dict: TickSubStagesAsDict):
    tick_items_this_substage = tick_items_as_dict[substage]

    return [name_of_edit_tickitem_field(tick_sheet_item) for tick_sheet_item in tick_items_this_substage]



def name_of_edit_tickitem_field(tick_sheet_item: TickSheetItem):
    return "EDITTI_%s" % tick_sheet_item.id



def final_row_for_substage_in_table(substage: TickSubStage) -> RowInTable:
    entry_field = textInput(
        input_label="New tick item for sub-stage %s:" % substage.name,
        input_name=fieldname_for_new_item_in_substage_name(substage),
        value=''
    )
    button = button_for_new_item_in_substage_name(substage)
    return RowInTable(['',Line([entry_field, button])])


def list_of_names_of_new_item_in_substage_name_field(tick_items_as_dict: TickSubStagesAsDict):
    all_names = [fieldname_for_new_item_in_substage_name(substage)
    for substage in tick_items_as_dict.keys()]

    return all_names

def fieldname_for_new_item_in_substage_name(substage: TickSubStage) -> str:
    return "NEWTICKITEM_%s" % substage.id

def list_of_button_names_for_new_item_in_substage_name_field(tick_items_as_dict: TickSubStagesAsDict):
    all_names = [ button_value_for_new_item_in_substage_name(substage)
    for substage in tick_items_as_dict.keys()]

    return all_names

def button_for_new_item_in_substage_name(substage: TickSubStage) -> Button:
    return Button("Add", value=button_value_for_new_item_in_substage_name(substage))


def button_value_for_new_item_in_substage_name(substage: TickSubStage) -> str:
    return "ADDITEMBUTTON_%s" % substage.id

def substage_id_for_button_name_new_item(button_value: str) -> str:
    return button_value.split("_")[1]


FIELDNAME_FOR_NEW_SUBSTAGE_TEXT_BOX = "SUBSTAGENEW"

def row_to_add_substage_in_table(suggestions: AutoCorrectForQualificationEdit) -> RowInTable:
    ## need interface for autocomplete
    ### AUTOCORRECT
    text_input=listInput(
        input_label="New substage for qualification (click to see suggestions or enter new value)",
        input_name=FIELDNAME_FOR_NEW_SUBSTAGE_TEXT_BOX,
        list_of_options=suggestions.substage_names
    )

    return RowInTable([Line([text_input, button_for_new_substage]),''])


ADD_NEW_SUBSTAGE_BUTTON_VALUE = "ADDSUBSTAGE"

button_for_new_substage= Button("Add", value=ADD_NEW_SUBSTAGE_BUTTON_VALUE)


