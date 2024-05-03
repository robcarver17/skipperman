from typing import List, Tuple

from app.backend.ticks_and_qualifications.ticksheets import get_ticksheet_data

from app.logic.events.events_in_state import get_event_from_state

from app.objects.abstract_objects.abstract_lines import ListOfLines

from app.logic.instructors.state_storage import get_edit_state_of_ticksheet, EDIT_DROPDOWN_STATE, NO_EDIT_STATE, \
    get_group_from_state, get_qualification_from_state
from app.logic.instructors.ticksheet_table_elements import user_can_award_qualifications
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.ticks import no_tick, full_tick, half_tick, not_applicable_tick, Tick


def get_cadet_buttons_at_start_of_row_in_edit_state(interface: abstractInterface,
                                                    qualification_name: str,
                                                    cadet_name: str,
                                                    cadet_id: str,
                                                    already_qualified: bool) -> ListOfLines:

    can_award_qualification = user_can_award_qualifications(interface)

    if can_award_qualification:
        return get_cadet_buttons_at_start_of_row_in_edit_state_if_can_award_qualification(
            qualification_name=qualification_name,
            cadet_id=cadet_id,
            cadet_name=cadet_name,
            already_qualified=already_qualified
        )
    else:
        return get_cadet_buttons_at_start_of_row_in_edit_state_if_cannot_award_qualifications(
            interface=interface,
            qualification_name=qualification_name,
            cadet_id=cadet_id,
            cadet_name=cadet_name,
            already_qualified=already_qualified

        )

def get_cadet_buttons_at_start_of_row_in_edit_state_if_can_award_qualification(
                                                    qualification_name: str,
                                                    cadet_name: str,
                                                    cadet_id: str,
                                                    already_qualified: bool) -> ListOfLines:


    if already_qualified:
        cadet_label = "%s (Withdraw %s)" % (cadet_name, qualification_name)
    else:
        cadet_label = "%s (Award %s)" % (cadet_name, qualification_name)

    ## Cadet name appears as a button, plus extra buttons, regardless of state
    cadet_button = Button(label=cadet_label, value=get_name_of_qualify_disqualify_for_cadet_button(cadet_id=cadet_id, already_qualifed=already_qualified))
    extra_buttons = get_extra_buttons_to_set_tick_state_for_cadet(cadet_id)
    return ListOfLines([cadet_button]+extra_buttons)

def get_cadet_buttons_at_start_of_row_in_edit_state_if_cannot_award_qualifications(interface: abstractInterface,
                                                    qualification_name: str,
                                                    cadet_name: str,
                                                    cadet_id: str,
                                                    already_qualified: bool) -> ListOfLines:

    if already_qualified:
        ## can't edit, no buttons
        cadet_label = "%s (%s)" % (cadet_name, qualification_name)
        return ListOfLines([cadet_label])

    state = get_edit_state_of_ticksheet(interface)
    is_dropdown_state = state == EDIT_DROPDOWN_STATE

    cadet_label = "%s (Full tick)" % cadet_name

    if is_dropdown_state:
        ## first button applies full tick, rest do other ticks
        return ListOfLines(get_extra_buttons_to_set_tick_state_for_cadet(cadet_id, label_for_first_button=cadet_label))
    else:
        ## checkbox state, just one button to do full ticks
        cadet_button = Button(label=cadet_label, value=get_name_of_tick_all_for_cadet_button(cadet_id))
        return ListOfLines([cadet_button])


def get_extra_buttons_to_set_tick_state_for_cadet(cadet_id: str, label_for_first_button = "Full tick"):
    return \
        [
            Button(label=label_for_first_button, value=get_name_of_tick_all_for_cadet_button(cadet_id)),
            Button(label="Half tick", value=get_name_of_tick_half_for_cadet_button(cadet_id)),
            Button(label="NA tick", value=get_name_of_tick_na_for_cadet_button(cadet_id)),
            Button(label="No tick", value=get_name_of_tick_notick_for_cadet_button(cadet_id))
        ]


def get_name_of_qualify_disqualify_for_cadet_button(cadet_id: str, already_qualifed: bool = True):
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


def get_name_of_tick_notick_for_item_button(item_id: str):
    return get_name_of_generic_button(item_id_axis, no_tick_label, item_id)


def get_name_of_generic_button(axis: str, tick_type: str, id: str):
    return "%s_%s_%s" % (axis, tick_type, id)

def get_axis_tick_type_id_from_button_name(button_name: str) -> Tuple[str, str, str]:
    axis,tick_type, id = button_name.split("_")
    return axis, tick_type, id


### only internal, weird names make unusual collisions less likely
qual_label = "tBqQUAL"
disqual_leable = "tBqDISQUAL"
item_id_axis = "tBiITEM"
cadet_id_axis = "tBiCADET"

full_label = full_tick.name
half_label = half_tick.name
na_label = not_applicable_tick.name
no_tick_label = no_tick.name

def from_tick_label_to_tick(tick_label) -> Tick:
    return Tick[tick_label]

types_of_tick = [full_label, half_label, na_label, no_tick_label]
types_of_tick_for_cadet = types_of_tick+[qual_label, disqual_leable]

def get_list_of_all_tick_related_button_names(interface: abstractInterface)  -> List[str]:
    state = get_edit_state_of_ticksheet(interface)
    if state == NO_EDIT_STATE:
        return []

    event = get_event_from_state(interface)
    group = get_group_from_state(interface)
    qualification = get_qualification_from_state(interface)

    ticksheet_data = get_ticksheet_data(
        interface=interface,
        event=event,
        group=group,
        qualification=qualification
    )

    list_of_cadet_ids = ticksheet_data.tick_sheet.list_of_cadet_ids
    list_of_item_ids = ticksheet_data.tick_sheet.list_of_tick_list_item_ids()

    all_buttons = []
    for cadet_id in list_of_cadet_ids:
        all_buttons+=list_of_all_possible_buttons_for_cadet_id(cadet_id)

    for item_id in list_of_item_ids:
        all_buttons+=list_of_all_possible_buttons_for_item_id(item_id)

    return all_buttons

def list_of_all_possible_buttons_for_cadet_id(cadet_id: str) -> List[str]:
    all_buttons_for_cadet = [get_name_of_generic_button(
        axis=cadet_id_axis,
        tick_type=tick_type,
        id=cadet_id
    )
    for tick_type in types_of_tick_for_cadet]

    return all_buttons_for_cadet


def list_of_all_possible_buttons_for_item_id(item_id: str) -> List[str]:
    all_buttons_for_item = [get_name_of_generic_button(
        axis=item_id_axis,
        tick_type=tick_type,
        id=item_id
    )
        for tick_type in types_of_tick]

    return all_buttons_for_item
