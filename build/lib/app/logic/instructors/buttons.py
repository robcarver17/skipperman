from typing import List, Tuple, Union

from app.backend.ticks_and_qualifications.ticksheets import get_ticksheet_data

from app.logic.events.events_in_state import get_event_from_state

from app.objects.abstract_objects.abstract_lines import ListOfLines, Line

from app.logic.instructors.state_storage import get_edit_state_of_ticksheet, EDIT_DROPDOWN_STATE, NO_EDIT_STATE, \
    get_group_from_state, get_qualification_from_state, set_cadet_id_in_state, return_true_if_a_cadet_id_been_set
from app.logic.instructors.ticksheet_table_elements import user_can_award_qualifications
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.ticks import no_tick, full_tick, half_tick, not_applicable_tick, Tick, TickSheetItem

def get_select_cadet_button_when_in_no_edit_mode(cadet_id: str, cadet_label: str, has_an_id_been_set: bool) -> Union[ListOfLines, str]:
    if has_an_id_been_set:
        return cadet_label

    return ListOfLines(
        [Line([
            Button(label=cadet_label, value=get_name_of_select_cadet_button(cadet_id=cadet_id))
            ]
        )
    ]
    )

def get_button_or_label_for_tickitem_name(interface: abstractInterface, tick_item: TickSheetItem) -> Union[ListOfLines, str]:
    has_an_id_been_set = return_true_if_a_cadet_id_been_set(interface)

    state = get_edit_state_of_ticksheet(interface)
    if state==NO_EDIT_STATE or has_an_id_been_set:
        return tick_item.name

    full_tick_button_label = "%s (Full tick)" % tick_item.name

    state = get_edit_state_of_ticksheet(interface)
    is_dropdown_state = state == EDIT_DROPDOWN_STATE
    item_id = tick_item.id

    first_button = Button(label=full_tick_button_label, value=get_name_of_tick_all_for_item_button(item_id))
    buttons = [first_button]

    if is_dropdown_state:
        buttons=buttons+[
            Button(label="Half tick", value=get_name_of_tick_half_for_item_button(item_id)),
            Button(label="NA tick", value=get_name_of_tick_na_for_item_button(item_id)),
            Button(label="No tick", value=get_name_of_tick_notick_for_item_button(item_id))
        ]

    return ListOfLines(buttons).add_Lines()


def get_name_of_tick_notick_for_item_button(item_id: str):
    return get_name_of_generic_button(item_id_axis, no_tick_label, item_id)


def get_cadet_buttons_at_start_of_row_in_edit_state(interface: abstractInterface,
                                                    qualification_name: str,
                                                    cadet_name: str,
                                                    cadet_id: str,
                                                    already_qualified: bool) -> ListOfLines:

    can_award_qualification = user_can_award_qualifications(interface)

    if can_award_qualification:
        return get_cadet_buttons_at_start_of_row_in_edit_state_if_can_award_qualification(
            interface=interface,
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

def get_cadet_buttons_at_start_of_row_in_edit_state_if_can_award_qualification(interface: abstractInterface,
                                                    qualification_name: str,
                                                    cadet_name: str,
                                                    cadet_id: str,
                                                    already_qualified: bool) -> ListOfLines:


    if already_qualified:
        qual_label = "Withdraw %s for %s" %  (qualification_name, cadet_name)
        qual_button = Button(label=qual_label, value=get_name_of_qualify_disqualify_for_cadet_button(cadet_id=cadet_id,
                                                                                                     already_qualifed=already_qualified))
        return ListOfLines([qual_button])

    qual_label = "Award %s for %s" %  (qualification_name, cadet_name)

    ## Cadet name appears as a button, plus extra buttons, regardless of state
    qual_button = Button(label=qual_label, value=get_name_of_qualify_disqualify_for_cadet_button(cadet_id=cadet_id, already_qualifed=already_qualified))
    tick_buttons = get_buttons_to_set_tick_state_for_cadet(interface=interface, cadet_name=cadet_name, cadet_id=cadet_id, cadet_name_on_first_button=False)

    return ListOfLines([qual_button]+tick_buttons)

def get_cadet_buttons_at_start_of_row_in_edit_state_if_cannot_award_qualifications(interface: abstractInterface,
                                                    qualification_name: str,
                                                    cadet_name: str,
                                                    cadet_id: str,
                                                    already_qualified: bool) -> ListOfLines:

    if already_qualified:
        ## can't edit, no buttons
        cadet_label = "%s (%s)" % (cadet_name, qualification_name)
        return ListOfLines([cadet_label])

    tick_buttons = get_buttons_to_set_tick_state_for_cadet(interface=interface, cadet_id=cadet_id, cadet_name=cadet_name, cadet_name_on_first_button=True)
    return ListOfLines(tick_buttons)


def get_buttons_to_set_tick_state_for_cadet(interface: abstractInterface, cadet_id: str, cadet_name: str, cadet_name_on_first_button: bool):
    if cadet_name_on_first_button:
        full_tick_button_label = "%s (Full tick)" % cadet_name
    else:
        full_tick_button_label = "Full tick"

    state = get_edit_state_of_ticksheet(interface)
    is_dropdown_state = state == EDIT_DROPDOWN_STATE

    first_button = Button(label=full_tick_button_label, value=get_name_of_tick_all_for_cadet_button(cadet_id))
    buttons = [first_button]

    if is_dropdown_state:
        buttons=buttons+[
            Button(label="Half tick", value=get_name_of_tick_half_for_cadet_button(cadet_id)),
            Button(label="NA tick", value=get_name_of_tick_na_for_cadet_button(cadet_id)),
            Button(label="No tick", value=get_name_of_tick_notick_for_cadet_button(cadet_id))
        ]

    return buttons

def get_name_of_qualify_disqualify_for_cadet_button(cadet_id: str, already_qualifed: bool = True):
    if already_qualifed:
        label = disqual_leable
    else:
        label = qual_label
    return get_name_of_generic_button(cadet_id_axis, label, cadet_id)

def get_name_of_select_cadet_button(cadet_id: str):
    return "%s_%s" % (select_cadet_axis, cadet_id)

def cadet_id_when_selected_from_button_label(label: str):
    return label.split("_")[1]

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
select_cadet_axis = "scCadet"

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
        all_buttons+=list_of_all_possible_buttons_for_cadet_id_macro_ticks(cadet_id)

    for item_id in list_of_item_ids:
        all_buttons+=list_of_all_possible_buttons_for_item_id_macro_ticks(item_id)

    return all_buttons

def get_list_of_all_possible_select_cadet_buttons(interface: abstractInterface) ->List[str]:
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

    return [get_name_of_select_cadet_button(cadet_id) for cadet_id in list_of_cadet_ids]

def list_of_all_possible_buttons_for_cadet_id_macro_ticks(cadet_id: str) -> List[str]:
    all_buttons_for_cadet = [get_name_of_generic_button(
        axis=cadet_id_axis,
        tick_type=tick_type,
        id=cadet_id
    )
    for tick_type in types_of_tick_for_cadet]

    return all_buttons_for_cadet


def list_of_all_possible_buttons_for_item_id_macro_ticks(item_id: str) -> List[str]:
    all_buttons_for_item = [get_name_of_generic_button(
        axis=item_id_axis,
        tick_type=tick_type,
        id=item_id
    )
        for tick_type in types_of_tick]

    return all_buttons_for_item

def set_cadet_id(interface: abstractInterface, button_pressed: str):
    cadet_id = cadet_id_when_selected_from_button_label(button_pressed)
    set_cadet_id_in_state(interface=interface, cadet_id=cadet_id)
