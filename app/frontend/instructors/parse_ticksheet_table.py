from typing import Union

from app.objects.cadets import Cadet

from app.backend.qualifications_and_ticks.ticksheets import (
    save_ticksheet_edits_for_specific_tick,
)
from app.frontend.instructors.render_ticksheet_table import (
    get_tick_from_dropdown_or_none,
    get_tick_from_checkbox_or_none, get_ticksheet_data_from_state,
get_dropdown_mode_from_state
)

from app.frontend.shared.qualification_and_tick_state_storage import (
    get_edit_state_of_ticksheet,
    NO_EDIT_STATE,
    EDIT_DROPDOWN_STATE,
    EDIT_CHECKBOX_STATE, not_editing,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.ticks import  Tick, half_tick, not_applicable_tick
from app.objects.substages import TickSheetItem
from app.objects.composed.ticksheet import DictOfCadetsAndTicksWithinQualification
from app.objects.composed.ticks_for_qualification import DictOfTickSheetItemsAndTicksForCadet, TicksForQualification


def save_ticksheet_edits(interface: abstractInterface):
    if not_editing(interface):
        return

    ticksheet_data = get_ticksheet_data_from_state(interface)

    save_ticksheet_table_edits_given_data(
        interface=interface, ticksheet_data=ticksheet_data
    )


def save_ticksheet_table_edits_given_data(
    interface: abstractInterface,
    ticksheet_data: DictOfCadetsAndTicksWithinQualification
):

    return [
        save_ticksheet_edits_for_cadet(
            interface=interface, ticks_for_qualification=ticksheet_data[cadet], cadet=cadet
        )
        for cadet, ticks_for_qualification in ticksheet_data.items()
    ]


def save_ticksheet_edits_for_cadet(
    interface: abstractInterface,
    ticks_for_qualification: TicksForQualification,
    cadet: Cadet
):
    dict_of_tick_items = ticks_for_qualification.all_tick_sheet_items_and_ticks()
    save_ticksheet_edits_for_dict_of_tick_item(
        interface=interface,
        cadet=cadet,
        dict_of_tick_items=dict_of_tick_items

    )


def save_ticksheet_edits_for_dict_of_tick_item(
    interface: abstractInterface,
    cadet: Cadet,
    dict_of_tick_items: DictOfTickSheetItemsAndTicksForCadet

):

    for tick_item, current_tick in dict_of_tick_items.items():
        get_and_save_ticksheet_edits_for_specific_tick(
            interface=interface,
            current_tick=current_tick,
            tick_item=tick_item,
            cadet=cadet
        )


def get_and_save_ticksheet_edits_for_specific_tick(
    interface: abstractInterface, current_tick: Tick, cadet: Cadet, tick_item: TickSheetItem

):
    new_tick_or_none = get_ticksheet_edits_for_specific_tick_or_none(
        interface=interface, cadet_id=cadet.id, item_id=tick_item.id,
        current_tick=current_tick
    )

    apply_ticksheet_edits_for_specific_tick(
        interface=interface,
        cadet=cadet,
        tick_item = tick_item,
        new_tick_or_none=new_tick_or_none,
        current_tick=current_tick
    )


def apply_ticksheet_edits_for_specific_tick(
    interface: abstractInterface,
    current_tick: Tick,
    new_tick_or_none: Union[Tick, None],
    cadet: Cadet,
    tick_item: TickSheetItem

):
    if tick_status_unchanged(current_tick=current_tick, new_tick_or_none=new_tick_or_none):
        return

    print("APPLYING TICK CHANGE TO %s ITEM %s FROM %s to %s" % (str(cadet), str(tick_item), str(current_tick), str(new_tick_or_none)))

    save_ticksheet_edits_for_specific_tick(
        object_store = interface.object_store,
        cadet = cadet,
        tick_item = tick_item,
        new_tick=new_tick_or_none
    )

def tick_status_unchanged(    current_tick: Tick,
        new_tick_or_none: Union[Tick, None],

)->bool:
    if new_tick_or_none is None:
        return True

    return new_tick_or_none == current_tick


def get_ticksheet_edits_for_specific_tick_or_none(
    interface: abstractInterface, cadet_id: str, item_id: str,
        current_tick: Tick
) -> Union[Tick, None]:
    state = get_edit_state_of_ticksheet(interface)
    if state == NO_EDIT_STATE:
        return None
    elif state == EDIT_DROPDOWN_STATE:
        return get_tick_from_dropdown_or_none(
            interface=interface, item_id=item_id, cadet_id=cadet_id
        )
    elif state == EDIT_CHECKBOX_STATE:
        if current_tick in [half_tick, not_applicable_tick]:
            ## Not possible to get tick if not set to none or full
            return None

        return get_tick_from_checkbox_or_none(
            interface=interface, item_id=item_id, cadet_id=cadet_id
        )
    else:
        raise Exception("state %s not known" % state)


