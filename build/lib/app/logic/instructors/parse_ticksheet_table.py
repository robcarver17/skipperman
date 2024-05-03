from typing import Union

from app.backend.ticks_and_qualifications.ticksheets import get_ticksheet_data, TickSheetDataWithExtraInfo
from app.backend.data.ticksheets import TickSheetsData
from app.logic.instructors.render_ticksheet_table import get_tick_from_dropdown_or_none, get_tick_from_checkbox_or_none

from app.objects.qualifications import Qualification

from app.objects.groups import Group

from app.objects.events import Event

from app.logic.instructors.state_storage import get_group_from_state, get_qualification_from_state, \
    get_edit_state_of_ticksheet, NO_EDIT_STATE, EDIT_DROPDOWN_STATE, EDIT_CHECKBOX_STATE

from app.logic.events.events_in_state import get_event_from_state

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.ticks import DictOfTicksWithItem, Tick, not_applicable_tick, half_tick


def save_ticksheet_edits(interface: abstractInterface):
    state = get_edit_state_of_ticksheet(interface)
    if state == NO_EDIT_STATE:
        return

    event = get_event_from_state(interface)
    group = get_group_from_state(interface)
    qualification = get_qualification_from_state(interface)

    save_ticksheet_table_edits(interface=interface,
                               event=event,
                               group=group,
                               qualification=qualification
                               )

def save_ticksheet_table_edits(event: Event,
                        group: Group,
                        qualification: Qualification,
                        interface: abstractInterface
                        ):
    ticksheet_data = get_ticksheet_data(
        interface=interface,
        event=event,
        group=group,
        qualification=qualification
    )

    save_ticksheet_table_edits_given_data(interface=interface, ticksheet_data=ticksheet_data)


def save_ticksheet_table_edits_given_data(interface: abstractInterface, ticksheet_data: TickSheetDataWithExtraInfo,
                      ):

    list_of_cadet_ids = ticksheet_data.tick_sheet.list_of_cadet_ids
    return [save_ticksheet_edits_for_cadet(interface=interface,ticksheet_data=ticksheet_data,cadet_id=cadet_id)
                                            for cadet_id in list_of_cadet_ids]


def save_ticksheet_edits_for_cadet(
                                   interface: abstractInterface,
        ticksheet_data: TickSheetDataWithExtraInfo,
                                   cadet_id: str):

    idx = ticksheet_data.tick_sheet.index_of_cadet_id(cadet_id)
    relevant_row = ticksheet_data.tick_sheet[idx]
    dict_of_tick_items = relevant_row.dict_of_ticks_with_items
    save_ticksheet_edits_for_dict_of_tick_item(interface=interface,cadet_id=cadet_id,dict_of_ticks_with_items=dict_of_tick_items)

def save_ticksheet_edits_for_dict_of_tick_item( interface: abstractInterface, cadet_id: str, dict_of_ticks_with_items: DictOfTicksWithItem):
    list_of_ticks = dict_of_ticks_with_items.list_of_ticks()
    list_of_item_ids = dict_of_ticks_with_items.list_of_item_ids()
    for current_tick, item_id in zip(list_of_ticks, list_of_item_ids):
        get_and_save_ticksheet_edits_for_specific_tick(interface=interface, current_tick=current_tick, item_id=item_id, cadet_id=cadet_id)

def get_and_save_ticksheet_edits_for_specific_tick(interface: abstractInterface, current_tick: Tick, cadet_id: str, item_id: str):
    tick_or_none = get_ticksheet_edits_for_specific_tick(interface=interface,
                                                 cadet_id=cadet_id,
                                                 item_id=item_id,
                                                 current_tick=current_tick)
    if tick_or_none is None:
        return

    new_tick = tick_or_none
    if new_tick == current_tick:
        return

    save_ticksheet_edits_for_specific_tick(interface=interface, cadet_id=cadet_id, item_id=item_id, new_tick=new_tick)

def get_ticksheet_edits_for_specific_tick(interface: abstractInterface, current_tick: Tick, cadet_id: str, item_id: str) -> Union[Tick, None]:
    state = get_edit_state_of_ticksheet(interface)
    if state == NO_EDIT_STATE:
        return
    elif state == EDIT_DROPDOWN_STATE:
        return get_tick_from_dropdown_or_none(interface=interface, item_id=item_id, cadet_id=cadet_id)
    elif state == EDIT_CHECKBOX_STATE:
        if current_tick in [not_applicable_tick, half_tick]:
            return None
        else:
            return get_tick_from_checkbox_or_none(interface=interface, item_id=item_id, cadet_id=cadet_id)
    else:
        raise Exception("state %s not known" % state)


def save_ticksheet_edits_for_specific_tick(interface: abstractInterface, new_tick: Tick, cadet_id: str, item_id: str):
    ticksheet_data = TickSheetsData(interface.data)
    ticksheet_data.add_or_modify_specific_tick(cadet_id=cadet_id, item_id=item_id, new_tick=new_tick)