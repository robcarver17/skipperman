from typing import List, Tuple, Union

from app.backend.qualifications_and_ticks.ticksheets import (
    get_ticksheet_data_for_cadets_at_event_in_group_with_qualification,
)

from app.frontend.shared.events_state import get_event_from_state
from app.frontend.shared.cadet_state import update_state_for_specific_cadet_id, update_state_for_specific_cadet
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line

from app.frontend.shared.qualification_and_tick_state_storage import (
    get_edit_state_of_ticksheet,
    EDIT_DROPDOWN_STATE,
    NO_EDIT_STATE,
    get_group_from_state,
    get_qualification_from_state,
    return_true_if_a_cadet_id_been_set,
)
from app.frontend.instructors.ticksheet_table_elements import (
    user_can_award_qualifications,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet
from app.objects.ticks import (
    no_tick,
    full_tick,
    half_tick,
    not_applicable_tick,
    Tick,
)
from app.objects.substages import TickSheetItem
from app.frontend.shared.buttons import get_button_value_for_cadet_selection, cadet_from_button_pressed, \
    get_button_value_given_type_and_attributes, get_attributes_from_button_pressed_of_known_type, is_button_of_type


def get_select_cadet_button_when_in_no_edit_mode(
    cadet: Cadet, cadet_label: str, has_an_id_been_set: bool
) -> Union[ListOfLines, str]:
    if has_an_id_been_set:
        return cadet_label

    return ListOfLines(
        [
            Line(
                [
                    Button(
                        label=cadet_label,
                        value=get_button_value_for_cadet_selection(cadet),
                    )
                ]
            )
        ]
    )


def get_button_or_label_for_tickitem_name(
    interface: abstractInterface, tick_item: TickSheetItem
) -> Union[ListOfLines, str]:
    has_an_id_been_set = return_true_if_a_cadet_id_been_set(interface)

    state = get_edit_state_of_ticksheet(interface)
    if state == NO_EDIT_STATE or has_an_id_been_set:
        return tick_item.name

    full_tick_button_label = "%s (Full tick)" % tick_item.name

    state = get_edit_state_of_ticksheet(interface)
    is_dropdown_state = state == EDIT_DROPDOWN_STATE
    item_id = tick_item.id

    first_button = Button(
        label=full_tick_button_label,
        value=get_name_of_tick_all_for_item_button(item_id),
    )
    buttons = [first_button]

    if is_dropdown_state:
        buttons = buttons + [
            Button(
                label="Half tick", value=get_name_of_tick_half_for_item_button(item_id)
            ),
            Button(label="NA tick", value=get_name_of_tick_na_for_item_button(item_id)),
            Button(
                label="No tick", value=get_name_of_tick_notick_for_item_button(item_id)
            ),
        ]

    return ListOfLines(buttons).add_Lines()


def get_name_of_tick_notick_for_item_button(item_id: str):
    return get_name_of_generic_button(item_id_axis, no_tick_label, item_id)


def get_cadet_buttons_at_start_of_row_in_edit_state(
    interface: abstractInterface,
    qualification_name: str,
    cadet_name: str,
    cadet_id: str,
    already_qualified: bool,
) -> ListOfLines:
    can_award_qualification = user_can_award_qualifications(interface)

    if can_award_qualification:
        return (
            get_cadet_buttons_at_start_of_row_in_edit_state_if_can_award_qualification(
                interface=interface,
                qualification_name=qualification_name,
                cadet_id=cadet_id,
                cadet_name=cadet_name,
                already_qualified=already_qualified,
            )
        )
    else:
        return get_cadet_buttons_at_start_of_row_in_edit_state_if_cannot_award_qualifications(
            interface=interface,
            qualification_name=qualification_name,
            cadet_id=cadet_id,
            cadet_name=cadet_name,
            already_qualified=already_qualified,
        )


def get_cadet_buttons_at_start_of_row_in_edit_state_if_can_award_qualification(
    interface: abstractInterface,
    qualification_name: str,
    cadet_name: str,
    cadet_id: str,
    already_qualified: bool,
) -> ListOfLines:
    if already_qualified:
        qual_label = "Withdraw %s for %s" % (qualification_name, cadet_name)
        qual_button = Button(
            label=qual_label,
            value=get_name_of_qualify_disqualify_for_cadet_button(
                cadet_id=cadet_id, already_qualifed=already_qualified
            ),
        )
        return ListOfLines([qual_button])

    qual_label = "Award %s for %s" % (qualification_name, cadet_name)

    ## Cadet name appears as a button, plus extra buttons, regardless of state
    qual_button = Button(
        label=qual_label,
        value=get_name_of_qualify_disqualify_for_cadet_button(
            cadet_id=cadet_id, already_qualifed=already_qualified
        ),
    )
    tick_buttons = get_buttons_to_set_tick_state_for_cadet(
        interface=interface,
        cadet_name=cadet_name,
        cadet_id=cadet_id,
        cadet_name_on_first_button=False,
    )

    return ListOfLines([qual_button] + tick_buttons)


def get_cadet_buttons_at_start_of_row_in_edit_state_if_cannot_award_qualifications(
    interface: abstractInterface,
    qualification_name: str,
    cadet_name: str,
    cadet_id: str,
    already_qualified: bool,
) -> ListOfLines:
    if already_qualified:
        ## can't edit, no buttons
        cadet_label = "%s (%s)" % (cadet_name, qualification_name)
        return ListOfLines([cadet_label])

    tick_buttons = get_buttons_to_set_tick_state_for_cadet(
        interface=interface,
        cadet_id=cadet_id,
        cadet_name=cadet_name,
        cadet_name_on_first_button=True,
    )
    return ListOfLines(tick_buttons)


def get_buttons_to_set_tick_state_for_cadet(
    interface: abstractInterface,
    cadet_id: str,
    cadet_name: str,
    cadet_name_on_first_button: bool,
):
    if cadet_name_on_first_button:
        full_tick_button_label = "%s (Full tick)" % cadet_name
    else:
        full_tick_button_label = "Full tick"

    state = get_edit_state_of_ticksheet(interface)
    is_dropdown_state = state == EDIT_DROPDOWN_STATE

    first_button = Button(
        label=full_tick_button_label,
        value=get_name_of_tick_all_for_cadet_button(cadet_id),
    )
    buttons = [first_button]

    if is_dropdown_state:
        buttons = buttons + [
            Button(
                label="Half tick",
                value=get_name_of_tick_half_for_cadet_button(cadet_id),
            ),
            Button(
                label="NA tick", value=get_name_of_tick_na_for_cadet_button(cadet_id)
            ),
            Button(
                label="No tick",
                value=get_name_of_tick_notick_for_cadet_button(cadet_id),
            ),
        ]

    return buttons


def get_name_of_qualify_disqualify_for_cadet_button(
    cadet_id: str, already_qualifed: bool = True
):
    if already_qualifed:
        label = disqual_leable
    else:
        label = qual_label
    return get_name_of_generic_button(cadet_id_axis, label, cadet_id)




def get_name_of_tick_all_for_cadet_button(cadet_id: str):
    return get_name_of_generic_button(cadet_id_axis, full_label, cadet_id)


def get_name_of_tick_na_for_cadet_button(cadet_id: str):
    return get_name_of_generic_button(cadet_id_axis, na_label, cadet_id)


def get_name_of_tick_half_for_cadet_button(cadet_id: str):
    return get_name_of_generic_button(cadet_id_axis, half_label, cadet_id)


def get_name_of_tick_notick_for_cadet_button(cadet_id: str):
    return get_name_of_generic_button(cadet_id_axis, no_tick_label, cadet_id)


def get_name_of_tick_all_for_item_button(item_id: str):
    return get_name_of_generic_button(item_id_axis, full_label, item_id)


def get_name_of_tick_half_for_item_button(item_id: str):
    return get_name_of_generic_button(item_id_axis, half_label, item_id)


def get_name_of_tick_na_for_item_button(item_id: str):
    return get_name_of_generic_button(item_id_axis, na_label, item_id)

generic_tick_button_type="genericTickButton"

def get_name_of_generic_button(axis: str, tick_type: str, id: str):
    return get_button_value_given_type_and_attributes(generic_tick_button_type, axis, tick_type, id)

def get_axis_tick_type_id_from_button_name(button_name: str) -> Tuple[str, str, str]:
    axis, tick_type, id = get_attributes_from_button_pressed_of_known_type(value_of_button_pressed=button_name,
                                                                           type_to_check=generic_tick_button_type)
    return axis, tick_type, id

def is_generic_tick_button_pressed(button_name:str):

    return is_button_of_type(type_to_check=generic_tick_button_type, value_of_button_pressed=button_name)

### only internal, weird names make unusual collisions less likely
qual_label = "tBqQUAL"
disqual_leable = "tBqDISQUAL"
item_id_axis = "tBiITEM"
cadet_id_axis = "tBiCADET"
select_cadet_axis = "scCadet"

full_label = full_tick.name
half_label = half_tick.name
na_label = not_applicable_tick.name
no_tick_label = no_tick.name


def from_tick_label_to_tick(tick_label) -> Tick:
    return Tick[tick_label]


types_of_tick = [full_label, half_label, na_label, no_tick_label]
types_of_tick_for_cadet = types_of_tick + [qual_label, disqual_leable]


