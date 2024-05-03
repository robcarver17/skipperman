from typing import List, Dict

from app.backend.cadets import cadet_from_id
from app.backend.ticks_and_qualifications.ticksheets import get_ticksheet_data, TickSheetDataWithExtraInfo

from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.logic.instructors.state_storage import get_edit_state_of_ticksheet, NO_EDIT_STATE, EDIT_CHECKBOX_STATE, EDIT_DROPDOWN_STATE

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import checkboxInput, dropDownInput
from app.objects.events import Event
from app.objects.groups import Group
from app.objects.qualifications import Qualification

from app.objects.ticks import DictOfTicksWithItem, Tick, tick_as_str, no_tick, not_applicable_tick, full_tick, \
    half_tick, list_of_tick_options


def get_ticksheet_table(event: Event,
                        group: Group,
                        qualification: Qualification,
                        interface: abstractInterface
                        )-> Table:
    ticksheet_data = get_ticksheet_data(
        interface=interface,
        event=event,
        group=group,
        qualification=qualification
    )

    top_rows = get_top_two_rows_for_table(ticksheet_data)
    other_rows = get_body_of_table(interface=interface,
                                   ticksheet_data=ticksheet_data)

    return Table(
        top_rows+other_rows,
        has_column_headings=True, has_row_headings=True
    )


def get_top_two_rows_for_table(ticksheet_data: TickSheetDataWithExtraInfo) -> List[RowInTable]:
    list_of_tick_list_items =ticksheet_data.list_of_tick_sheet_items_for_this_qualification
    list_of_substage_names = ticksheet_data.list_of_substage_names

    first_row = [""]
    second_row = [""]
    current_substage = ""
    for tick_item, substage_name in zip(list_of_tick_list_items, list_of_substage_names):
        if current_substage!=substage_name:
            subheading = current_substage = substage_name
        else:
            subheading = ""

        first_row.append(subheading)
        second_row.append(tick_item.name)

    first_row = RowInTable(first_row)
    second_row = RowInTable(second_row)

    return [first_row, second_row]




def get_body_of_table(interface: abstractInterface, ticksheet_data: TickSheetDataWithExtraInfo,
                      ) -> List[RowInTable]:

    list_of_cadet_ids = ticksheet_data.tick_sheet.list_of_cadet_ids
    return [get_row_for_cadet_in_ticksheet(interface=interface,ticksheet_data=ticksheet_data,cadet_id=cadet_id)
                                            for cadet_id in list_of_cadet_ids]


def get_row_for_cadet_in_ticksheet(
                                   interface: abstractInterface,
        ticksheet_data: TickSheetDataWithExtraInfo,
                                   cadet_id: str) -> RowInTable:

    idx = ticksheet_data.tick_sheet.index_of_cadet_id(cadet_id)
    cadet = cadet_from_id(interface=interface, cadet_id=cadet_id)
    relevant_row = ticksheet_data.tick_sheet[idx]
    dict_of_tick_items = relevant_row.dict_of_ticks_with_items
    rest_of_row = get_rest_of_row_in_table_for_dict_of_tick_item(interface=interface, dict_of_ticks_with_items=dict_of_tick_items, cadet_id=cadet_id)

    return RowInTable([cadet.name]+rest_of_row)

def get_rest_of_row_in_table_for_dict_of_tick_item( interface: abstractInterface, cadet_id: str, dict_of_ticks_with_items: DictOfTicksWithItem) -> list:
    list_of_ticks = dict_of_ticks_with_items.list_of_ticks()
    list_of_item_ids = dict_of_ticks_with_items.list_of_item_ids()
    return [get_cell_in_table_for_tick(interface=interface, tick=tick, item_id=item_id, cadet_id=cadet_id) for tick, item_id in zip(list_of_ticks, list_of_item_ids)]

def get_cell_in_table_for_tick( interface: abstractInterface,tick: Tick, cadet_id: str,item_id: str):
    state = get_edit_state_of_ticksheet(interface)
    if state==NO_EDIT_STATE:
        return get_cell_in_table_for_view_only(tick)
    elif state == EDIT_DROPDOWN_STATE:
        return get_cell_in_table_for_dropdown_edit(tick=tick, item_id=item_id, cadet_id=cadet_id)
    elif state == EDIT_CHECKBOX_STATE:
        return get_cell_in_table_for_checkbox_edit( tick=tick, item_id=item_id, cadet_id=cadet_id)
    else:
        raise Exception("state %s not known" % state)

def get_cell_in_table_for_view_only(tick: Tick):
    return tick_as_str(tick)


def get_cell_in_table_for_checkbox_edit(tick: Tick,cadet_id: str, item_id: str):

    if tick == no_tick:
        return get_checkbox_input(False, cadet_id=cadet_id, item_id=item_id)
    elif tick == full_tick:
        return get_checkbox_input(True, cadet_id=cadet_id, item_id=item_id)
    elif tick == not_applicable_tick:
        return 'N/A'
    elif tick == half_tick:
        return '1/2'

FULL_TICK ='full'
def get_checkbox_input(ticked: bool,cadet_id: str, item_id: str) -> checkboxInput:

        return  checkboxInput(
            input_name=get_name_of_cell(item_id=item_id, cadet_id=cadet_id),
            dict_of_labels={FULL_TICK:''},
            dict_of_checked={FULL_TICK: ticked},
            input_label=''
        )

def get_tick_from_checkbox_or_none(interface: abstractInterface, cadet_id: str, item_id: str) -> Tick:
    try:
        selected_tick = interface.value_of_multiple_options_from_form(get_name_of_cell(item_id=item_id, cadet_id=cadet_id))
    except:
        ## happens if half or n/a tick
        return None

    if FULL_TICK in selected_tick:
        return full_tick
    else:
        return no_tick

def get_cell_in_table_for_dropdown_edit(tick: Tick, cadet_id: str, item_id: str) -> dropDownInput:
    current_tick_name = tick.name
    dict_of_tick_options = get_dict_of_tick_options()

    return dropDownInput(
        input_label='',
        dict_of_options=dict_of_tick_options,
        default_label=current_tick_name,
        input_name=get_name_of_cell(item_id=item_id, cadet_id=cadet_id)
    )


def get_dict_of_tick_options() -> Dict[str,str]:
    option_names = [option.name for option in list_of_tick_options]
    dict_of_options = dict([
        (name, name) for name in option_names
    ])

    return dict_of_options

def get_tick_from_dropdown(interface: abstractInterface, cadet_id: str, item_id: str) -> Tick:
    selected_tick_name = interface.value_from_form(get_name_of_cell(item_id=item_id, cadet_id=cadet_id))

    return Tick[selected_tick_name]



def get_name_of_cell(item_id: str, cadet_id: str):
    return "%s_%s" % (item_id, cadet_id)

