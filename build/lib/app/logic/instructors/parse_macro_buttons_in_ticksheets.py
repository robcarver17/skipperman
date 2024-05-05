from typing import List

from app.backend.ticks_and_qualifications.qualifications import apply_qualification_to_cadet, \
    remove_qualification_from_cadet
from app.backend.ticks_and_qualifications.ticksheets import get_ticksheet_data_from_state, TickSheetDataWithExtraInfo, \
    cadet_is_already_qualified
from app.logic.instructors.buttons import get_axis_tick_type_id_from_button_name, item_id_axis, cadet_id_axis, \
    qual_label, disqual_leable, from_tick_label_to_tick
from app.logic.instructors.parse_ticksheet_table import apply_ticksheet_edits_for_specific_tick
from app.logic.instructors.state_storage import get_qualification_from_state
from app.logic.instructors.ticksheet_table_elements import user_can_award_qualifications
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.ticks import Tick, no_tick


def action_if_macro_tick_button_pressed(interface: abstractInterface, button_pressed: str):
    axis, tick_type, id =  get_axis_tick_type_id_from_button_name(button_pressed)
    ticksheet_data = get_ticksheet_data_from_state(interface)
    if axis == item_id_axis:
        action_if_item_tick_button_pressed(interface=interface, tick_type=tick_type, item_id=id, ticksheet_data=ticksheet_data)
    elif axis == cadet_id_axis:
        action_if_cadet_tick_button_pressed(interface=interface, tick_type=tick_type, cadet_id=id, ticksheet_data=ticksheet_data)


def action_if_cadet_tick_button_pressed(interface: abstractInterface, tick_type: str, cadet_id: str, ticksheet_data: TickSheetDataWithExtraInfo):
    if tick_type==qual_label:
        action_if_cadet_apply_qualification_button_pressed(interface=interface, cadet_id=cadet_id)
    elif tick_type==disqual_leable:
        action_if_cadet_remove_qualification_button_pressed(interface=interface, cadet_id=cadet_id)
    else:
        tick = from_tick_label_to_tick(tick_type)
        action_if_cadet_tick_level_button_pressed(interface=interface ,tick=tick, cadet_id=cadet_id, ticksheet_data=ticksheet_data)

    # qual code


def action_if_cadet_apply_qualification_button_pressed(interface: abstractInterface,  cadet_id: str):
    interface.log_error("Qualification awarding is locked for now")
    return

    can_award_qualification = user_can_award_qualifications(interface)
    if not can_award_qualification:
        interface.log_error("User not allowed to apply qualifications!")

    qualification = get_qualification_from_state(interface)
    apply_qualification_to_cadet(interface=interface, cadet_id=cadet_id, qualification=qualification)


def action_if_cadet_remove_qualification_button_pressed(interface: abstractInterface,  cadet_id: str):
    interface.log_error("Qualification awarding is locked for now")
    return

    can_award_qualification = user_can_award_qualifications(interface)
    if not can_award_qualification:
        interface.log_error("User not allowed to remove qualifications!")

    qualification = get_qualification_from_state(interface)
    remove_qualification_from_cadet(interface=interface, cadet_id=cadet_id, qualification=qualification)


def action_if_cadet_tick_level_button_pressed(interface: abstractInterface, ticksheet_data: TickSheetDataWithExtraInfo, tick: Tick, cadet_id: str):
    already_qualified= cadet_is_already_qualified(ticksheet_data=ticksheet_data, cadet_id=cadet_id)
    if already_qualified:
        return

    # loop over get_and_save_ticksheet_edits_for_specific_tick
    list_of_item_ids = get_list_of_item_ids(ticksheet_data)
    for item_id in list_of_item_ids:
        current_tick = get_current_tick(ticksheet_data=ticksheet_data, cadet_id=cadet_id, item_id=item_id)
        apply_ticksheet_edits_for_specific_tick(
            interface=interface,
            cadet_id=cadet_id,
            item_id=item_id,
            new_tick_or_none=tick,
            current_tick=current_tick
        )


def get_list_of_item_ids(ticksheet_data: TickSheetDataWithExtraInfo)-> List[str]:
    return ticksheet_data.tick_sheet.list_of_tick_list_item_ids()


def action_if_item_tick_button_pressed(interface: abstractInterface, ticksheet_data: TickSheetDataWithExtraInfo, tick_type: str, item_id: str):
    tick = from_tick_label_to_tick(tick_type)
    list_of_cadet_ids = get_list_of_cadet_ids(ticksheet_data)
    for cadet_id in list_of_cadet_ids:
        already_qualified = cadet_is_already_qualified(ticksheet_data=ticksheet_data, cadet_id=cadet_id)
        if already_qualified:
            continue
        current_tick = get_current_tick(ticksheet_data=ticksheet_data, cadet_id=cadet_id, item_id=item_id)
        apply_ticksheet_edits_for_specific_tick(
            interface=interface,
            cadet_id=cadet_id,
            item_id=item_id,
            new_tick_or_none=tick,
            current_tick=current_tick
        )


def get_list_of_cadet_ids(ticksheet_data: TickSheetDataWithExtraInfo)-> List[str]:
    return ticksheet_data.tick_sheet.list_of_cadet_ids


def get_current_tick(ticksheet_data: TickSheetDataWithExtraInfo, cadet_id: str, item_id: str) -> Tick:
    idx = ticksheet_data.tick_sheet.index_of_cadet_id(cadet_id)
    relevant_row = ticksheet_data.tick_sheet[idx]
    dict_of_tick_items = relevant_row.dict_of_ticks_with_items

    return dict_of_tick_items.get(item_id, no_tick)
