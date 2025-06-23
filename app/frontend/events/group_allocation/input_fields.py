from app.backend.groups.data_for_group_display import *
from app.backend.groups.data_for_group_display import (
    get_potential_partner_to_be_added_or_missing_data,
)
from app.frontend.events.group_allocation.buttons import (
    get_make_available_button,
    get_button_for_partnership_cell,
)
from app.frontend.forms.form_utils import (
    input_name_from_column_name_and_cadet_id,
    get_availability_checkbox,
)
from app.frontend.events.constants import (
    ATTENDANCE,
)
from app.frontend.events.group_allocation.store_state import (
    no_day_set_in_state,
    get_day_from_state_or_none,
)
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_form import (
    textInput,
    checkboxInput,
    dropDownInput,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.cadets import Cadet
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets
from app.objects.day_selectors import Day
from app.objects.partners import NO_PARTNERSHIP_LIST_OF_STR
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
    availability = cadet_availability_at_event(
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
) -> list:
    if no_day_set_in_state(interface=interface):
        return get_input_fields_for_cadet_across_days(
            cadet=cadet, dict_of_all_event_data=dict_of_all_event_data
        )
    day = get_day_from_state_or_none(interface)

    return get_input_fields_for_cadet_on_day(
        cadet=cadet, day=day, dict_of_all_event_data=dict_of_all_event_data
    )


def get_input_fields_for_cadet_across_days(
    cadet: Cadet, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> list:
    group_allocation_field = get_dropdown_input_for_group_allocation_across_days(
        cadet=cadet, dict_of_all_event_data=dict_of_all_event_data
    )
    dropdown_input_for_club_boat_allocation = (
        get_dropdown_input_for_club_boat_allocation_across_days(
            cadet=cadet, dict_of_all_event_data=dict_of_all_event_data
        )
    )
    dropdown_input_for_boat_class_allocation = (
        get_dropdown_input_for_boat_class_allocation_across_days(
            cadet=cadet, dict_of_all_event_data=dict_of_all_event_data
        )
    )
    sail_number_field = get_sail_number_field_across_days(
        cadet=cadet, dict_of_all_event_data=dict_of_all_event_data
    )
    input_for_partner_allocation = get_input_for_partner_allocation_across_days(
        cadet=cadet, dict_of_all_event_data=dict_of_all_event_data
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
    cadet: Cadet, day: Day, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> list:
    availability = cadet_availability_at_event(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    if not availability.available_on_day(day):
        return get_input_fields_for_cadet_on_day_when_unavailable(cadet)
    else:
        return get_input_fields_for_cadet_on_day_when_available(
            cadet=cadet, day=day, dict_of_all_event_data=dict_of_all_event_data
        )


def get_input_fields_for_cadet_on_day_when_unavailable(cadet: Cadet) -> list:
    padding = [""] * 4
    return [get_make_available_button(cadet)] + padding


def get_input_fields_for_cadet_on_day_when_available(
    cadet: Cadet, day: Day, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> list:
    group_allocation_field = get_dropdown_input_for_group_allocation_on_day(
        cadet=cadet, dict_of_all_event_data=dict_of_all_event_data, day=day
    )
    dropdown_input_for_club_boat_allocation = (
        get_dropdown_input_for_club_boat_allocation_on_day(
            cadet=cadet, dict_of_all_event_data=dict_of_all_event_data, day=day
        )
    )
    dropdown_input_for_boat_class_allocation = (
        get_dropdown_input_for_boat_class_allocation_on_day(
            cadet=cadet, dict_of_all_event_data=dict_of_all_event_data, day=day
        )
    )
    sail_number_field = get_sail_number_field_on_day(
        cadet=cadet, dict_of_all_event_data=dict_of_all_event_data, day=day
    )
    input_for_partner_allocation = get_input_for_partner_allocation_on_day(
        cadet=cadet, dict_of_all_event_data=dict_of_all_event_data, day=day
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
    cadet: Cadet,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
) -> Union[dropDownInput, str]:
    current_group = get_current_group_name_across_days_or_none_if_different(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    if current_group is None:
        return get_string_describing_different_group_names(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )

    return get_dropdown_input_for_group_allocation(
        dict_of_all_event_data=dict_of_all_event_data,
        cadet=cadet,
        current_group=current_group,
    )


def get_dropdown_input_for_group_allocation_on_day(
    cadet: Cadet, day: Day, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> Union[dropDownInput, str]:
    current_group = get_current_group_name_for_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )

    return get_dropdown_input_for_group_allocation(
        dict_of_all_event_data=dict_of_all_event_data,
        cadet=cadet,
        current_group=current_group,
    )


def get_dropdown_input_for_group_allocation(
    cadet: Cadet,
    current_group: str,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
) -> Union[dropDownInput, str]:
    dict_of_options = get_dict_of_all_possible_groups_for_dropdown_input(
        dict_of_all_event_data
    )
    drop_down_input_field = dropDownInput(
        input_name=input_name_from_column_name_and_cadet_id(
            ALLOCATION, cadet_id=cadet.id
        ),
        input_label="",
        default_label=current_group,
        dict_of_options=dict_of_options,
    )

    return drop_down_input_field


def get_dict_of_all_possible_groups_for_dropdown_input(
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
):
    all_groups = (
        dict_of_all_event_data.dict_of_cadets_with_days_and_groups.list_of_groups
    )
    all_groups = all_groups + [unallocated_group]
    dict_of_all_possible_groups_for_dropdown_input = dict(
        [(group.name, group.name) for group in all_groups if not group.hidden]
    )

    return dict_of_all_possible_groups_for_dropdown_input


def get_dropdown_input_for_club_boat_allocation_across_days(
    cadet: Cadet,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
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
    dropdown_input_field = get_dropdown_input_field_for_club_dinghies(
        dict_of_all_event_data=dict_of_all_event_data,
        cadet=cadet,
        current_club_boat_name=current_club_boat_name,
    )

    return dropdown_input_field


def get_dropdown_input_for_club_boat_allocation_on_day(
    cadet: Cadet, day: Day, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> dropDownInput:
    current_club_boat_name = get_current_club_boat_name_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )

    dropdown_input_field = get_dropdown_input_field_for_club_dinghies(
        dict_of_all_event_data=dict_of_all_event_data,
        cadet=cadet,
        current_club_boat_name=current_club_boat_name,
    )

    return dropdown_input_field


def get_dict_of_club_dinghies_for_dropdown(
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
):
    club_dinghies = (
        dict_of_all_event_data.dict_of_cadets_and_club_dinghies_at_event.list_of_club_dinghies
    )
    club_dinghies.append(no_club_dinghy)
    dict_of_all_possible_club_boats_for_dropdown = dict(
        [(dinghy.name, dinghy.name) for dinghy in club_dinghies if not dinghy.hidden]
    )

    return dict_of_all_possible_club_boats_for_dropdown


def get_dropdown_input_field_for_club_dinghies(
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    cadet: Cadet,
    current_club_boat_name: str,
) -> dropDownInput:
    dict_of_club_dinghies_for_dropdown_input = get_dict_of_club_dinghies_for_dropdown(
        dict_of_all_event_data
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
    cadet: Cadet, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> dropDownInput:
    current_boat_class = get_current_boat_class_across_days_or_none_if_different(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    if current_boat_class is None:
        return get_string_describing_different_boat_class_across_days(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )
    else:
        return get_dropdown_input_for_boat_class_allocation(
            dict_of_all_event_data=dict_of_all_event_data,
            cadet=cadet,
            current_boat_class=current_boat_class,
        )


def get_dropdown_input_for_boat_class_allocation_on_day(
    cadet: Cadet, day: Day, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> dropDownInput:
    current_boat_class = get_name_of_class_of_boat_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )
    return get_dropdown_input_for_boat_class_allocation(
        dict_of_all_event_data=dict_of_all_event_data,
        cadet=cadet,
        current_boat_class=current_boat_class,
    )


def get_dropdown_input_for_boat_class_allocation(
    cadet: Cadet,
    current_boat_class: str,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
) -> dropDownInput:
    dict_of_all_possible_boat_classes = get_dict_of_boat_classes(dict_of_all_event_data)
    drop_down_input_field = dropDownInput(
        input_name=input_name_from_column_name_and_cadet_id(
            BOAT_CLASS, cadet_id=cadet.id
        ),
        input_label="",
        default_label=str(current_boat_class),
        dict_of_options=dict_of_all_possible_boat_classes,
    )
    return drop_down_input_field


def get_dict_of_boat_classes(dict_of_all_event_data: DictOfAllEventInfoForCadets):
    boat_classes = (
        dict_of_all_event_data.dict_of_cadets_and_boat_class_and_partners.list_of_boat_classes
    )
    boat_classes.append(no_boat_class)
    dict_of_all_possible_boat_classes = dict(
        [(dinghy.name, dinghy.name) for dinghy in boat_classes if not dinghy.hidden]
    )

    return dict_of_all_possible_boat_classes


def get_sail_number_field_across_days(
    cadet: Cadet, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> textInput:
    current_number = get_current_sail_number_across_days_or_none_if_different(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    if current_number is None:
        return get_string_describing_different_sail_numbers_across_days(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )
    return get_sail_number_field(cadet=cadet, current_number=current_number)


def get_sail_number_field_on_day(
    cadet: Cadet, day: Day, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> textInput:
    current_number = make_id_as_int_str(
        get_sail_number_for_boat_on_day(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
        )
    )
    return get_sail_number_field(cadet=cadet, current_number=current_number)


def get_sail_number_field(cadet: Cadet, current_number: str) -> textInput:
    sail_number_field = textInput(
        input_name=input_name_from_column_name_and_cadet_id(
            cadet_id=cadet.id, column_name=SAIL_NUMBER
        ),
        value=current_number,
        input_label="",
    )
    return sail_number_field


def get_input_for_partner_allocation_across_days(
    cadet: Cadet, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> ListOfLines:
    current_partner_name = get_two_handed_partner_as_str_for_dropdown_cadet_across_days(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    if current_partner_name is None:
        return get_string_describing_two_handed_partner_name_across_days(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )
    else:
        return get_input_for_partner_allocation_across_days_when_consistent(
            dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
        )


def get_input_for_partner_allocation_across_days_when_consistent(
    cadet: Cadet, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> ListOfLines:
    current_partner_name = get_two_handed_partner_as_str_for_dropdown_cadet_across_days(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )

    list_of_other_cadets = get_list_of_cadet_names_including_asterix_marks_at_event_with_matching_schedules_excluding_this_cadet(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )  ### needs to disapply cadets who aren't also available the whole week
    list_of_other_cadets = NO_PARTNERSHIP_LIST_OF_STR + list_of_other_cadets

    potential_partner_to_be_added_or_missing_data = (
        get_potential_partner_to_be_added_or_missing_data(
            cadet=cadet, dict_of_all_event_data=dict_of_all_event_data
        )
    )

    return get_input_for_partner_allocation(
        cadet=cadet,
        list_of_other_cadets=list_of_other_cadets,
        current_partner_name=current_partner_name,
        potential_partner_to_be_added_or_missing_data=potential_partner_to_be_added_or_missing_data,
    )


def get_input_for_partner_allocation_on_day(
    cadet: Cadet, day: Day, dict_of_all_event_data: DictOfAllEventInfoForCadets
) -> ListOfLines:
    current_partner_name = get_two_handed_partner_as_str_for_dropdown_cadet_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )
    list_of_other_cadets = get_list_of_cadet_names_including_asterix_marks_at_event_with_matching_schedules_excluding_this_cadet(
        dict_of_all_event_data=dict_of_all_event_data,
        cadet=cadet,
        available_on_specific_day=day,
    )

    potential_partner_to_be_added_or_missing_data = (
        get_potential_partner_to_be_added_or_missing_data(
            cadet=cadet, dict_of_all_event_data=dict_of_all_event_data
        )
    )

    return get_input_for_partner_allocation(
        cadet=cadet,
        list_of_other_cadets=list_of_other_cadets,
        current_partner_name=current_partner_name,
        potential_partner_to_be_added_or_missing_data=potential_partner_to_be_added_or_missing_data,
    )


def get_input_for_partner_allocation(
    cadet: Cadet,
    list_of_other_cadets: List[str],
    current_partner_name: str,
    potential_partner_to_be_added_or_missing_data: str,
) -> ListOfLines:
    drop_down_input_field = get_dropdown_field_for_partner_allocation(
        list_of_other_cadets=list_of_other_cadets,
        current_partner_name=current_partner_name,
        cadet=cadet,
    )
    partnership_button = get_button_for_partnership_cell(
        cadet=cadet,
        potential_partner_to_be_added_or_missing_data=potential_partner_to_be_added_or_missing_data,
        current_partner_name=current_partner_name,
    )

    return ListOfLines([drop_down_input_field, partnership_button])


def get_dropdown_field_for_partner_allocation(
    cadet: Cadet,
    list_of_other_cadets: List[str],
    current_partner_name: str,
) -> dropDownInput:
    list_of_other_cadets = NO_PARTNERSHIP_LIST_OF_STR + list_of_other_cadets
    dict_of_all_possible_cadets = dict(
        [(cadet_name, cadet_name) for cadet_name in list_of_other_cadets]
    )

    drop_down_input_field = dropDownInput(
        input_name=input_name_from_column_name_and_cadet_id(PARTNER, cadet_id=cadet.id),
        input_label="",
        default_label=current_partner_name,
        dict_of_options=dict_of_all_possible_cadets,
    )

    return drop_down_input_field


NOTES = "Notes"
ALLOCATION = "allocation"
CLUB_BOAT = "club_boat"
PARTNER = "partner"
BOAT_CLASS = "boat_class"
SAIL_NUMBER = "sail_number"


GUESS_BOAT_BUTTON = "Autofill Boat Class"

guess_boat_button = Button(GUESS_BOAT_BUTTON, nav_button=True)
