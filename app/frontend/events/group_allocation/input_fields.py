from copy import copy

from app.backend.groups.data_for_group_display import *

from app.frontend.events.group_allocation.buttons import (
    get_make_available_button,
)
from app.frontend.events.group_allocation.partnership_input_fields import (
    get_input_for_partner_allocation_on_day,
    get_input_for_partner_allocation_across_days,
)
from app.frontend.forms.form_utils import (
    input_name_from_column_name_and_cadet_id,
    get_availability_checkbox,
)
from app.frontend.events.group_allocation.store_state import (
    no_day_set_in_state,
    get_day_from_state_or_none,
)
from app.frontend.shared.check_security import is_admin_or_skipper
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import (
    textInput,
    checkboxInput,
    dropDownInput,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet
from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import (
    ListOfBoatGroupings,
)
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets
from app.objects.day_selectors import Day
from app.objects.utilities.transform_data import make_id_as_int_str


def get_notes_field(cadet: Cadet, dict_of_all_event_data: DictOfAllEventInfoForCadets):
    registration_for_cadet_at_event = dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).registration_data

    return textInput(
        input_name=input_name_from_column_name_and_cadet_id(
            column_name=NOTES, cadet_id=cadet.id
        ),
        input_label="",
        value=registration_for_cadet_at_event.notes,
    )


def get_days_attending_field(
    cadet: Cadet, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> checkboxInput:
    availability = cadet_availability_at_event_from_dict_of_all_event_data(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    days_attending_field = get_availability_checkbox(
        availability=availability,
        event=dict_of_all_event_data.event,
        input_name=input_name_from_column_name_and_cadet_id(
            column_name=ATTENDANCE, cadet_id=cadet.id
        ),
        line_break=True,
    )
    return days_attending_field


def get_input_fields_for_cadet(
    interface: abstractInterface,
    cadet: Cadet,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    list_of_boat_groupings: ListOfBoatGroupings,
) -> list:
    if no_day_set_in_state(interface=interface):
        return get_input_fields_for_cadet_across_days(
            interface=interface,
            cadet=cadet,
            dict_of_all_event_data=dict_of_all_event_data,
            list_of_boat_groupings=list_of_boat_groupings,
        )
    day = get_day_from_state_or_none(interface)

    return get_input_fields_for_cadet_on_day(
        interface=interface,
        cadet=cadet,
        day=day,
        dict_of_all_event_data=dict_of_all_event_data,
        list_of_boat_groupings=list_of_boat_groupings,
    )


def get_input_fields_for_cadet_across_days(
    interface: abstractInterface,
    cadet: Cadet,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    list_of_boat_groupings: ListOfBoatGroupings,
) -> list:
    can_edit = list_of_boat_groupings.does_cadet_have_edit_rights_across_days(cadet)
    group_allocation_field = get_dropdown_input_for_group_allocation_across_days(
        interface=interface,
        cadet=cadet,
        dict_of_all_event_data=dict_of_all_event_data,
        can_edit=can_edit,
    )
    dropdown_input_for_club_boat_allocation = (
        get_dropdown_input_for_club_boat_allocation_across_days(
            interface=interface,
            cadet=cadet,
            dict_of_all_event_data=dict_of_all_event_data,
            can_edit=can_edit,
        )
    )
    dropdown_input_for_boat_class_allocation = (
        get_dropdown_input_for_boat_class_allocation_across_days(
            cadet=cadet,
            dict_of_all_event_data=dict_of_all_event_data,
            can_edit=can_edit,
        )
    )
    sail_number_field = get_sail_number_field_across_days(
        cadet=cadet, dict_of_all_event_data=dict_of_all_event_data, can_edit=can_edit
    )
    input_for_partner_allocation = get_input_for_partner_allocation_across_days(
        interface=interface, cadet=cadet, dict_of_all_event_data=dict_of_all_event_data
    )

    input_fields = [
        group_allocation_field,
        dropdown_input_for_club_boat_allocation,
        dropdown_input_for_boat_class_allocation,
        sail_number_field,
        input_for_partner_allocation,
    ]

    return input_fields


def get_input_fields_for_cadet_on_day(
    interface: abstractInterface,
    cadet: Cadet,
    day: Day,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    list_of_boat_groupings: ListOfBoatGroupings,
) -> list:
    availability = cadet_availability_at_event_from_dict_of_all_event_data(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    if not availability.available_on_day(day):
        return get_input_fields_for_cadet_on_day_when_unavailable(
            interface=interface, cadet=cadet
        )
    else:
        return get_input_fields_for_cadet_on_day_when_available(
            interface=interface,
            cadet=cadet,
            day=day,
            dict_of_all_event_data=dict_of_all_event_data,
            list_of_boat_groupings=list_of_boat_groupings,
        )


def get_input_fields_for_cadet_on_day_when_unavailable(
    cadet: Cadet, interface: abstractInterface
) -> list:
    padding = [""] * 4
    if is_admin_or_skipper(interface):
        return [get_make_available_button(cadet)] + padding
    else:
        return ["Not attending today"] + padding


def get_input_fields_for_cadet_on_day_when_available(
    interface: abstractInterface,
    cadet: Cadet,
    day: Day,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    list_of_boat_groupings: ListOfBoatGroupings,
) -> list:
    can_edit = list_of_boat_groupings.does_cadet_have_edit_rights_on_day(cadet, day=day)

    group_allocation_field = get_dropdown_input_for_group_allocation_on_day(
        interface=interface,
        cadet=cadet,
        dict_of_all_event_data=dict_of_all_event_data,
        day=day,
        can_edit=can_edit,
    )
    dropdown_input_for_club_boat_allocation = (
        get_dropdown_input_for_club_boat_allocation_on_day(
            interface=interface,
            cadet=cadet,
            dict_of_all_event_data=dict_of_all_event_data,
            day=day,
            can_edit=can_edit,
        )
    )
    dropdown_input_for_boat_class_allocation = (
        get_dropdown_input_for_boat_class_allocation_on_day(
            cadet=cadet,
            dict_of_all_event_data=dict_of_all_event_data,
            day=day,
            can_edit=can_edit,
        )
    )
    sail_number_field = get_sail_number_field_on_day(
        cadet=cadet,
        dict_of_all_event_data=dict_of_all_event_data,
        day=day,
        can_edit=can_edit,
    )
    input_for_partner_allocation = get_input_for_partner_allocation_on_day(
        interface=interface,
        cadet=cadet,
        dict_of_all_event_data=dict_of_all_event_data,
        day=day,
    )

    input_fields = [
        group_allocation_field,
        dropdown_input_for_club_boat_allocation,
        dropdown_input_for_boat_class_allocation,
        sail_number_field,
        input_for_partner_allocation,
    ]

    return input_fields


def get_dropdown_input_for_group_allocation_across_days(
    interface: abstractInterface,
    cadet: Cadet,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    can_edit: bool,
) -> Union[dropDownInput, str]:
    current_group_name = get_current_group_name_across_days_or_none_if_different(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    if current_group_name is None:
        return get_string_describing_different_group_names(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )

    if is_admin_or_skipper(interface) and can_edit:
        return get_dropdown_input_for_group_allocation(
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
            current_group_name=current_group_name,
        )
    else:
        return current_group_name


def get_dropdown_input_for_group_allocation_on_day(
    interface: abstractInterface,
    cadet: Cadet,
    day: Day,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    can_edit: bool,
) -> Union[dropDownInput, str]:
    current_group_name = get_current_group_name_for_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )

    if is_admin_or_skipper(interface) and can_edit:
        return get_dropdown_input_for_group_allocation(
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
            current_group_name=current_group_name,
        )
    else:
        return current_group_name


def get_dropdown_input_for_group_allocation(
    cadet: Cadet,
    current_group_name: str,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
) -> Union[dropDownInput, str]:
    dict_of_options = get_dict_of_all_possible_groups_for_dropdown_input(
        dict_of_all_event_data, current_group_name=current_group_name
    )
    drop_down_input_field = dropDownInput(
        input_name=input_name_from_column_name_and_cadet_id(
            ALLOCATION, cadet_id=cadet.id
        ),
        input_label="",
        default_label=current_group_name,
        dict_of_options=dict_of_options,
    )

    return drop_down_input_field


def get_dict_of_all_possible_groups_for_dropdown_input(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, current_group_name: str
):
    all_groups = copy(dict_of_all_event_data.list_of_groups)
    all_groups.add_unallocated()
    dict_of_all_possible_groups_for_dropdown_input = dict(
        [
            (group.name, group.name)
            for group in all_groups
            if not group.hidden or group.name == current_group_name
        ]
    )

    return dict_of_all_possible_groups_for_dropdown_input


def get_dropdown_input_for_club_boat_allocation_across_days(
    interface: abstractInterface,
    cadet: Cadet,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    can_edit: bool,
) -> Union[dropDownInput, str]:
    current_club_boat_name = (
        get_current_club_boat_name_across_days_or_none_if_different(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )
    )
    if current_club_boat_name is None:
        return get_string_describing_different_club_boats_across_days(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )
    if is_admin_or_skipper(interface) and can_edit:
        return get_dropdown_input_field_for_club_dinghies(
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
            current_club_boat_name=current_club_boat_name,
        )
    else:
        return current_club_boat_name


def get_dropdown_input_for_club_boat_allocation_on_day(
    interface: abstractInterface,
    cadet: Cadet,
    day: Day,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    can_edit: bool,
) -> Union[dropDownInput, str]:
    current_club_boat_name = get_current_club_boat_name_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )

    if is_admin_or_skipper(interface) and can_edit:
        return get_dropdown_input_field_for_club_dinghies(
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
            current_club_boat_name=current_club_boat_name,
        )
    else:
        return current_club_boat_name


def get_dict_of_club_dinghies_for_dropdown(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, current_club_boat_name: str
):
    club_dinghies = copy(dict_of_all_event_data.list_of_club_dinghies)
    club_dinghies.add_no_club_dinghy()
    dict_of_all_possible_club_boats_for_dropdown = dict(
        [
            (dinghy.name, dinghy.name)
            for dinghy in club_dinghies
            if not dinghy.hidden or dinghy.name == current_club_boat_name
        ]
    )

    return dict_of_all_possible_club_boats_for_dropdown


def get_dropdown_input_field_for_club_dinghies(
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    cadet: Cadet,
    current_club_boat_name: str,
) -> dropDownInput:
    dict_of_club_dinghies_for_dropdown_input = get_dict_of_club_dinghies_for_dropdown(
        dict_of_all_event_data, current_club_boat_name=current_club_boat_name
    )

    dropdown_input_field = dropDownInput(
        input_name=input_name_from_column_name_and_cadet_id(
            CLUB_BOAT, cadet_id=cadet.id
        ),
        input_label="",
        default_label=current_club_boat_name,
        dict_of_options=dict_of_club_dinghies_for_dropdown_input,
    )

    return dropdown_input_field


def get_dropdown_input_for_boat_class_allocation_across_days(
    cadet: Cadet, dict_of_all_event_data: DictOfAllEventInfoForCadets, can_edit: bool
) -> Union[dropDownInput, str]:
    current_boat_class_name = get_current_boat_class_across_days_or_none_if_different(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    if current_boat_class_name is None:
        return get_string_describing_different_boat_class_across_days(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )
    if can_edit:
        return get_dropdown_input_for_boat_class_allocation(
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
            current_boat_class_name=current_boat_class_name,
        )
    else:
        return current_boat_class_name


def get_dropdown_input_for_boat_class_allocation_on_day(
    cadet: Cadet,
    day: Day,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    can_edit: bool,
) -> Union[dropDownInput, str]:
    current_boat_class_name = get_name_of_class_of_boat_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )
    if can_edit:
        return get_dropdown_input_for_boat_class_allocation(
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
            current_boat_class_name=current_boat_class_name,
        )
    else:
        return current_boat_class_name


def get_dropdown_input_for_boat_class_allocation(
    cadet: Cadet,
    current_boat_class_name: str,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
) -> dropDownInput:
    dict_of_all_possible_boat_classes = get_dict_of_boat_classes(
        dict_of_all_event_data, current_boat_class_name=current_boat_class_name
    )
    drop_down_input_field = dropDownInput(
        input_name=input_name_from_column_name_and_cadet_id(
            BOAT_CLASS, cadet_id=cadet.id
        ),
        input_label="",
        default_label=str(current_boat_class_name),
        dict_of_options=dict_of_all_possible_boat_classes,
    )
    return drop_down_input_field


def get_dict_of_boat_classes(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, current_boat_class_name: str
):
    boat_classes = dict_of_all_event_data.list_of_boat_classes
    boat_classes.append(no_boat_class)
    dict_of_all_possible_boat_classes = dict(
        [
            (dinghy.name, dinghy.name)
            for dinghy in boat_classes
            if not dinghy.hidden or dinghy.name == current_boat_class_name
        ]
    )

    return dict_of_all_possible_boat_classes


def get_sail_number_field_across_days(
    cadet: Cadet, dict_of_all_event_data: DictOfAllEventInfoForCadets, can_edit: bool
) -> Union[textInput, str]:
    current_number = get_current_sail_number_across_days_or_none_if_different(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    if current_number is None:
        return get_string_describing_different_sail_numbers_across_days(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )
    if can_edit:
        return get_sail_number_field(cadet=cadet, current_number=current_number)
    else:
        return current_number


def get_sail_number_field_on_day(
    cadet: Cadet,
    day: Day,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    can_edit: bool,
) -> Union[textInput, str]:
    current_number = make_id_as_int_str(
        get_sail_number_for_boat_on_day(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
        )
    )
    if can_edit:
        return get_sail_number_field(cadet=cadet, current_number=current_number)
    else:
        return current_number


def get_sail_number_field(cadet: Cadet, current_number: str) -> textInput:
    sail_number_field = textInput(
        input_name=input_name_from_column_name_and_cadet_id(
            cadet_id=cadet.id, column_name=SAIL_NUMBER
        ),
        value=current_number,
        input_label="",
    )
    return sail_number_field


NOTES = "Notes"
ALLOCATION = "allocation"
CLUB_BOAT = "club_boat"
BOAT_CLASS = "boat_class"
SAIL_NUMBER = "sail_number"
ATTENDANCE = "attendance"

GUESS_BOAT_BUTTON = "Autofill Boat Class"

guess_boat_button = Button(GUESS_BOAT_BUTTON, nav_button=True)
