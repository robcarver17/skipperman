from app.objects.cadets import Cadet

from app.objects.composed.ticksheet import DictOfCadetsAndTicksWithinQualification

from app.backend.qualifications_and_ticks.qualifications_for_cadet import (
    apply_qualification_to_cadet,
    remove_qualification_from_cadet,
)

from app.frontend.instructors.buttons import (
    get_axis_tick_type_id_from_button_name,
    item_id_axis,
    cadet_id_axis,
    qual_label,
    disqual_leable,
    from_tick_label_to_tick,
)
from app.frontend.instructors.parse_ticksheet_table import (
    apply_ticksheet_edits_for_specific_tick,
)
from app.frontend.instructors.render_ticksheet_table import (
    get_ticksheet_data_from_state,
)
from app.frontend.shared.qualification_and_tick_state_storage import (
    get_qualification_from_state,
)
from app.frontend.instructors.ticksheet_table_elements import (
    user_can_award_qualifications,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.ticks import Tick
from app.objects.substages import TickSheetItem
from app.backend.cadets.list_of_cadets import get_cadet_from_id


def action_if_macro_tick_button_pressed(
    interface: abstractInterface, button_pressed: str
):
    axis, tick_type, id = get_axis_tick_type_id_from_button_name(button_pressed)
    ticksheet_data = get_ticksheet_data_from_state(interface)
    if axis == item_id_axis:
        action_if_item_tick_button_pressed(
            interface=interface,
            tick_type=tick_type,
            item_id=id,
            ticksheet_data=ticksheet_data,
        )
    elif axis == cadet_id_axis:
        action_if_cadet_tick_button_pressed(
            interface=interface,
            tick_type=tick_type,
            cadet_id=id,
            ticksheet_data=ticksheet_data,
        )


def action_if_cadet_tick_button_pressed(
    interface: abstractInterface,
    tick_type: str,
    cadet_id: str,
    ticksheet_data: DictOfCadetsAndTicksWithinQualification,
):
    cadet = get_cadet_from_id(object_store=interface.object_store, cadet_id=cadet_id)
    if tick_type == qual_label:
        action_if_cadet_apply_qualification_button_pressed(
            interface=interface, cadet=cadet
        )
    elif tick_type == disqual_leable:
        action_if_cadet_remove_qualification_button_pressed(
            interface=interface, cadet=cadet
        )
    else:
        tick = from_tick_label_to_tick(tick_type)
        action_if_cadet_tick_level_button_pressed(
            interface=interface,
            tick=tick,
            cadet=cadet,
            ticksheet_data=ticksheet_data,
        )

    # qual code


def action_if_cadet_apply_qualification_button_pressed(
    interface: abstractInterface, cadet: Cadet
):
    can_award_qualification = user_can_award_qualifications(interface)
    if not can_award_qualification:
        interface.log_error("User not allowed to apply qualifications_and_ticks!")

    qualification = get_qualification_from_state(interface)
    apply_qualification_to_cadet(
        object_store=interface.object_store, cadet=cadet, qualification=qualification
    )


def action_if_cadet_remove_qualification_button_pressed(
    interface: abstractInterface, cadet: Cadet
):
    can_award_qualification = user_can_award_qualifications(interface)
    if not can_award_qualification:
        interface.log_error("User not allowed to remove qualifications_and_ticks!")

    qualification = get_qualification_from_state(interface)
    remove_qualification_from_cadet(
        object_store=interface.object_store, cadet=cadet, qualification=qualification
    )


def action_if_cadet_tick_level_button_pressed(
    interface: abstractInterface,
    ticksheet_data: DictOfCadetsAndTicksWithinQualification,
    tick: Tick,
    cadet: Cadet,
):
    already_qualified = ticksheet_data[cadet].already_qualified
    if already_qualified:
        return

    # loop over get_and_save_ticksheet_edits_for_specific_tick
    list_of_items = ticksheet_data.list_of_tick_sheet_items_for_this_qualification
    for tick_item in list_of_items:
        current_tick = get_current_tick(
            ticksheet_data=ticksheet_data, cadet=cadet, tick_item=tick_item
        )
        apply_ticksheet_edits_for_specific_tick(
            interface=interface,
            cadet=cadet,
            tick_item=tick_item,
            new_tick_or_none=tick,
            current_tick=current_tick,
        )


def action_if_item_tick_button_pressed(
    interface: abstractInterface,
    ticksheet_data: DictOfCadetsAndTicksWithinQualification,
    tick_type: str,
    item_id: str,
):
    tick_item = (
        ticksheet_data.list_of_tick_sheet_items_for_this_qualification.object_with_id(
            item_id
        )
    )
    tick = from_tick_label_to_tick(tick_type)
    list_of_cadets = ticksheet_data.list_of_cadets
    for cadet in list_of_cadets:
        already_qualified = ticksheet_data[cadet].already_qualified
        if already_qualified:
            continue
        current_tick = get_current_tick(
            ticksheet_data=ticksheet_data, cadet=cadet, tick_item=tick_item
        )
        apply_ticksheet_edits_for_specific_tick(
            interface=interface,
            tick_item=tick_item,
            cadet=cadet,
            new_tick_or_none=tick,
            current_tick=current_tick,
        )


def get_current_tick(
    ticksheet_data: DictOfCadetsAndTicksWithinQualification,
    cadet: Cadet,
    tick_item: TickSheetItem,
) -> Tick:
    ticksheet_for_cadet = ticksheet_data[cadet]
    return ticksheet_for_cadet.current_tick(tick_item)
