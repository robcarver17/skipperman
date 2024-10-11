from typing import Union

from app.OLD_backend.ticks_and_qualifications.ticksheets import (
    TickSheetDataWithExtraInfo,
    save_ticksheet_edits_for_specific_tick,
    get_ticksheet_data,
)
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.instructors.render_ticksheet_table import (
    get_tick_from_dropdown_or_none,
    get_tick_from_checkbox_or_none,
)

from app.frontend.shared.qualification_and_tick_state_storage import (
    get_edit_state_of_ticksheet,
    NO_EDIT_STATE,
    EDIT_DROPDOWN_STATE,
    EDIT_CHECKBOX_STATE,
    not_editing,
    get_group_from_state,
    get_qualification_from_state,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.ticks import DictOfTicksWithItem, Tick


def save_ticksheet_edits(interface: abstractInterface):
    if not_editing(interface):
        return

    ticksheet_data = get_ticksheet_data_from_state(interface)
    save_ticksheet_table_edits_given_data(
        interface=interface, ticksheet_data=ticksheet_data
    )


def save_ticksheet_table_edits_given_data(
    interface: abstractInterface,
    ticksheet_data: TickSheetDataWithExtraInfo,
):
    list_of_cadet_ids = ticksheet_data.tick_sheet.list_of_cadet_ids
    return [
        save_ticksheet_edits_for_cadet(
            interface=interface, ticksheet_data=ticksheet_data, cadet_id=cadet_id
        )
        for cadet_id in list_of_cadet_ids
    ]


def save_ticksheet_edits_for_cadet(
    interface: abstractInterface,
    ticksheet_data: TickSheetDataWithExtraInfo,
    cadet_id: str,
):
    idx = ticksheet_data.tick_sheet.index_of_cadet_id(cadet_id)
    relevant_row = ticksheet_data.tick_sheet[idx]
    dict_of_tick_items = relevant_row.dict_of_ticks_with_items
    save_ticksheet_edits_for_dict_of_tick_item(
        interface=interface,
        cadet_id=cadet_id,
        dict_of_ticks_with_items=dict_of_tick_items,
    )


def save_ticksheet_edits_for_dict_of_tick_item(
    interface: abstractInterface,
    cadet_id: str,
    dict_of_ticks_with_items: DictOfTicksWithItem,
):
    list_of_ticks = dict_of_ticks_with_items.list_of_ticks()
    list_of_item_ids = dict_of_ticks_with_items.list_of_item_ids()
    for current_tick, item_id in zip(list_of_ticks, list_of_item_ids):
        get_and_save_ticksheet_edits_for_specific_tick(
            interface=interface,
            current_tick=current_tick,
            item_id=item_id,
            cadet_id=cadet_id,
        )


def get_and_save_ticksheet_edits_for_specific_tick(
    interface: abstractInterface, current_tick: Tick, cadet_id: str, item_id: str
):
    new_tick_or_none = get_ticksheet_edits_for_specific_tick_or_none(
        interface=interface, cadet_id=cadet_id, item_id=item_id
    )

    apply_ticksheet_edits_for_specific_tick(
        interface=interface,
        cadet_id=cadet_id,
        item_id=item_id,
        new_tick_or_none=new_tick_or_none,
        current_tick=current_tick,
    )


def apply_ticksheet_edits_for_specific_tick(
    interface: abstractInterface,
    current_tick: Tick,
    new_tick_or_none: Union[Tick, None],
    cadet_id: str,
    item_id: str,
):
    if new_tick_or_none is None:
        return

    new_tick = new_tick_or_none
    if new_tick == current_tick:
        return

    print("APPLYING")
    print(cadet_id)
    print(item_id)
    print(str(new_tick))
    save_ticksheet_edits_for_specific_tick(
        interface=interface, cadet_id=cadet_id, item_id=item_id, new_tick=new_tick
    )


def get_ticksheet_edits_for_specific_tick_or_none(
    interface: abstractInterface, cadet_id: str, item_id: str
) -> Union[Tick, None]:
    state = get_edit_state_of_ticksheet(interface)
    if state == NO_EDIT_STATE:
        return None
    elif state == EDIT_DROPDOWN_STATE:
        return get_tick_from_dropdown_or_none(
            interface=interface, item_id=item_id, cadet_id=cadet_id
        )
    elif state == EDIT_CHECKBOX_STATE:
        return get_tick_from_checkbox_or_none(
            interface=interface, item_id=item_id, cadet_id=cadet_id
        )
    else:
        raise Exception("state %s not known" % state)


def get_ticksheet_data_from_state(
    interface: abstractInterface,
) -> TickSheetDataWithExtraInfo:
    event = get_event_from_state(interface)
    group = get_group_from_state(interface)
    qualification = get_qualification_from_state(interface)

    ticksheet_data = get_ticksheet_data(
        interface=interface, event=event, group=group, qualification=qualification
    )
    return ticksheet_data
