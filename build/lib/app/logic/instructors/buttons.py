from app.objects.abstract_objects.abstract_lines import ListOfLines

from app.logic.instructors.state_storage import get_edit_state_of_ticksheet, EDIT_DROPDOWN_STATE
from app.logic.instructors.ticksheet_table_elements import user_can_award_qualifications
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_interface import abstractInterface


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
    return get_name_of_generic_button(cadet_id_label, label, cadet_id)


def get_name_of_tick_all_for_cadet_button(cadet_id: str):
    return get_name_of_generic_button(cadet_id_label, full_label, cadet_id)


def get_name_of_tick_na_for_cadet_button(cadet_id: str):
    return get_name_of_generic_button(cadet_id_label, na_label, cadet_id)


def get_name_of_tick_half_for_cadet_button(cadet_id: str):
    return get_name_of_generic_button(cadet_id_label, half_label, cadet_id)


def get_name_of_tick_notick_for_cadet_button(cadet_id: str):
    return get_name_of_generic_button(cadet_id_label, no_tick_label, cadet_id)


def get_name_of_tick_all_for_item_button(item_id: str):
    return get_name_of_generic_button(item_id_label, full_label, item_id)


def get_name_of_tick_half_for_item_button(item_id: str):
    return get_name_of_generic_button(item_id_label, half_label, item_id)


def get_name_of_tick_na_for_item_button(item_id: str):
    return get_name_of_generic_button(item_id_label, na_label, item_id)


def get_name_of_tick_notick_for_item_button(item_id: str):
    return get_name_of_generic_button(item_id_label, no_tick_label, item_id)


def get_name_of_generic_button(type: str, tick_type: str, id: str):
    return "%s_%s_%s" % (type, tick_type, id)


qual_label = "QUAL"
disqual_leable = "DISQUAL"
full_label = "FULL"
half_label = "HALF"
na_label = "NA"
no_tick_label = "NO"
item_id_label = "ITEM"
cadet_id_label = "CADET"
