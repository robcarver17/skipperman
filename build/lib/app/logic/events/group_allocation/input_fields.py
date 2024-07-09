from typing import Union, List

from app.backend.forms.form_utils import (
    input_name_from_column_name_and_cadet_id,
    get_availability_checkbox,
)
from app.backend.group_allocations.group_allocations_data import AllocationData
from app.data_access.configuration.groups import all_groups_names
from app.logic.events.constants import (
    ATTENDANCE,
    ALLOCATION,
    CLUB_BOAT,
    BOAT_CLASS,
    SAIL_NUMBER,
    PARTNER,
)
from app.logic.events.group_allocation.store_state import (
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
from app.objects.club_dinghies import NO_BOAT
from app.objects.constants import missing_data
from app.objects.day_selectors import Day
from app.objects.dinghies import NO_PARTNERSHIP_LIST
from app.objects.utils import make_id_as_int_str


def get_notes_field(cadet: Cadet, allocation_data: AllocationData):
    cadet_at_event = (
        allocation_data.cadets_at_event_including_non_active.cadet_at_event(cadet.id)
    )

    return textInput(
        input_name=input_name_from_column_name_and_cadet_id(
            column_name=NOTES, cadet_id=cadet.id
        ),
        input_label="",
        value=cadet_at_event.notes,
    )


def get_days_attending_field(
    cadet: Cadet, allocation_data: AllocationData
) -> checkboxInput:
    days_attending_field = get_availability_checkbox(
        availability=allocation_data.cadet_availability_at_event(cadet),
        event=allocation_data.event,
        input_name=input_name_from_column_name_and_cadet_id(
            column_name=ATTENDANCE, cadet_id=cadet.id
        ),
        line_break=True,
    )
    return days_attending_field


def get_input_fields_for_cadet(
    interface: abstractInterface, cadet: Cadet, allocation_data: AllocationData
) -> list:
    if no_day_set_in_state(interface=interface):
        return get_input_fields_for_cadet_across_days(
            cadet=cadet, allocation_data=allocation_data
        )
    day = get_day_from_state_or_none(interface)

    return get_input_fields_for_cadet_on_day(
        cadet=cadet, day=day, allocation_data=allocation_data
    )


def get_input_fields_for_cadet_across_days(
    cadet: Cadet, allocation_data: AllocationData
) -> list:
    group_allocation_field = get_dropdown_input_for_group_allocation_across_days(
        cadet=cadet, allocation_data=allocation_data
    )
    dropdown_input_for_club_boat_allocation = (
        get_dropdown_input_for_club_boat_allocation_across_days(
            cadet=cadet, allocation_data=allocation_data
        )
    )
    dropdown_input_for_boat_class_allocation = (
        get_dropdown_input_for_boat_class_allocation_across_days(
            cadet=cadet, allocation_data=allocation_data
        )
    )
    dropdown_input_for_partner_allocation = (
        get_dropdown_input_for_partner_allocation_across_days(
            cadet=cadet, allocation_data=allocation_data
        )
    )
    sail_number_field = get_sail_number_field_across_days(
        cadet=cadet, allocation_data=allocation_data
    )

    input_fields = [
        group_allocation_field,
        dropdown_input_for_club_boat_allocation,
        dropdown_input_for_boat_class_allocation,
        sail_number_field,
        dropdown_input_for_partner_allocation,
    ]

    return input_fields


def get_input_fields_for_cadet_on_day(
    cadet: Cadet, day: Day, allocation_data: AllocationData
) -> list:
    if not allocation_data.is_cadet_available_on_this_day(cadet=cadet, day=day):
        padding = [""] * 4
        return [
            Button(
                label=MAKE_CADET_AVAILABLE_ON_DAY_BUTTON,
                value=make_cadet_available_button_name(cadet),
            )
        ] + padding

    group_allocation_field = get_dropdown_input_for_group_allocation_on_day(
        cadet=cadet, allocation_data=allocation_data, day=day
    )
    dropdown_input_for_club_boat_allocation = (
        get_dropdown_input_for_club_boat_allocation_on_day(
            cadet=cadet, allocation_data=allocation_data, day=day
        )
    )
    dropdown_input_for_boat_class_allocation = (
        get_dropdown_input_for_boat_class_allocation_on_day(
            cadet=cadet, allocation_data=allocation_data, day=day
        )
    )
    dropdown_input_for_partner_allocation = (
        get_dropdown_input_for_partner_allocation_on_day(
            cadet=cadet, allocation_data=allocation_data, day=day
        )
    )
    sail_number_field = get_sail_number_field_on_day(
        cadet=cadet, allocation_data=allocation_data, day=day
    )

    input_fields = [
        group_allocation_field,
        dropdown_input_for_club_boat_allocation,
        dropdown_input_for_boat_class_allocation,
        sail_number_field,
        dropdown_input_for_partner_allocation,
    ]

    return input_fields


def make_cadet_available_button_name(cadet: Cadet):
    return "%s_%s" % (MAKE_CADET_AVAILABLE_ON_DAY_BUTTON, cadet.id)


def cadet_id_from_cadet_available_buttons(button_str: str):
    return button_str.split("_")[1]


def get_dropdown_input_for_group_allocation_across_days(
    cadet: Cadet, allocation_data: AllocationData
) -> Union[dropDownInput, str]:
    current_group = (
        allocation_data.get_current_group_name_across_days_or_none_if_different(
            cadet=cadet
        )
    )
    if current_group is None:
        return allocation_data.get_string_describing_different_group_names(cadet=cadet)
    return get_dropdown_input_for_group_allocation(
        cadet=cadet, current_group=current_group, allocation_data=allocation_data
    )


def get_dropdown_input_for_group_allocation_on_day(
    cadet: Cadet, day: Day, allocation_data: AllocationData
) -> Union[dropDownInput, str]:
    current_group = allocation_data.get_current_group_name_for_day(cadet=cadet, day=day)
    return get_dropdown_input_for_group_allocation(
        cadet=cadet, current_group=current_group, allocation_data=allocation_data
    )


def get_dropdown_input_for_group_allocation(
    cadet: Cadet, current_group: str, allocation_data: AllocationData
) -> Union[dropDownInput, str]:
    if allocation_data.event.contains_groups:
        drop_down_input_field = dropDownInput(
            input_name=input_name_from_column_name_and_cadet_id(
                ALLOCATION, cadet_id=cadet.id
            ),
            input_label="",
            default_label=current_group,
            dict_of_options=dict_of_all_possible_groups_for_dropdown_input,
        )
        return drop_down_input_field
    else:
        return "Racing"


dict_of_all_possible_groups_for_dropdown_input = dict(
    [(group, group) for group in all_groups_names]
)


def get_dropdown_input_for_club_boat_allocation_across_days(
    cadet: Cadet, allocation_data: AllocationData
) -> Union[dropDownInput, str]:
    current_club_boat = (
        allocation_data.get_current_club_boat_name_across_days_or_none_if_different(
            cadet=cadet
        )
    )
    if current_club_boat is None:
        return allocation_data.get_string_describing_different_club_boats_across_days(
            cadet=cadet
        )
    return get_dropdown_input_for_club_boat_allocation(
        cadet=cadet,
        current_club_boat=current_club_boat,
        allocation_data=allocation_data,
    )


def get_dropdown_input_for_club_boat_allocation_on_day(
    cadet: Cadet, day: Day, allocation_data: AllocationData
) -> dropDownInput:
    current_club_boat = allocation_data.get_current_club_boat_name_on_day(
        cadet=cadet, day=day
    )
    return get_dropdown_input_for_club_boat_allocation(
        cadet=cadet,
        current_club_boat=current_club_boat,
        allocation_data=allocation_data,
    )


def get_dropdown_input_for_club_boat_allocation(
    cadet: Cadet, current_club_boat: str, allocation_data: AllocationData
) -> dropDownInput:
    dict_of_club_dinghies_for_dropdown_input = get_list_of_club_dinghies_for_dropdown(
        allocation_data
    )
    drop_down_input_field = dropDownInput(
        input_name=input_name_from_column_name_and_cadet_id(
            CLUB_BOAT, cadet_id=cadet.id
        ),
        input_label="",
        default_label=str(current_club_boat),
        dict_of_options=dict_of_club_dinghies_for_dropdown_input,
    )
    return drop_down_input_field


def get_list_of_club_dinghies_for_dropdown(allocation_data: AllocationData):
    club_dinghies = allocation_data.list_of_club_boats
    dict_of_club_dinghies_for_dropdown_input = {NO_BOAT: NO_BOAT}
    dict_of_all_possible_club_boats = dict(
        [(dinghy.name, dinghy.name) for dinghy in club_dinghies]
    )
    dict_of_club_dinghies_for_dropdown_input.update(dict_of_all_possible_club_boats)

    return dict_of_club_dinghies_for_dropdown_input


def get_dropdown_input_for_boat_class_allocation_across_days(
    cadet: Cadet, allocation_data: AllocationData
) -> dropDownInput:
    current_boat_class = (
        allocation_data.get_current_boat_class_across_days_or_none_if_different(
            cadet=cadet
        )
    )
    if current_boat_class is None:
        return allocation_data.get_string_describing_different_boat_class_across_days(
            cadet=cadet
        )
    return get_dropdown_input_for_boat_class_allocation(
        cadet=cadet,
        current_boat_class=current_boat_class,
        allocation_data=allocation_data,
    )


def get_dropdown_input_for_boat_class_allocation_on_day(
    cadet: Cadet, day: Day, allocation_data: AllocationData
) -> dropDownInput:
    current_boat_class = allocation_data.get_name_of_class_of_boat_on_day(
        cadet=cadet, day=day
    )
    return get_dropdown_input_for_boat_class_allocation(
        cadet=cadet,
        current_boat_class=current_boat_class,
        allocation_data=allocation_data,
    )


def get_dropdown_input_for_boat_class_allocation(
    cadet: Cadet, current_boat_class: str, allocation_data: AllocationData
) -> dropDownInput:
    dict_of_all_possible_boat_classes = get_dict_of_boat_classes(allocation_data)
    drop_down_input_field = dropDownInput(
        input_name=input_name_from_column_name_and_cadet_id(
            BOAT_CLASS, cadet_id=cadet.id
        ),
        input_label="",
        default_label=str(current_boat_class),
        dict_of_options=dict_of_all_possible_boat_classes,
    )
    return drop_down_input_field


def get_dict_of_boat_classes(allocation_data: AllocationData):
    boat_classes = allocation_data.list_of_dinghies
    dict_of_all_possible_boat_classes = dict(
        [(dinghy.name, dinghy.name) for dinghy in boat_classes]
    )
    return dict_of_all_possible_boat_classes


def get_sail_number_field_across_days(
    cadet: Cadet, allocation_data: AllocationData
) -> textInput:
    current_number = (
        allocation_data.get_current_sail_number_across_days_or_none_if_different(
            cadet=cadet
        )
    )
    if current_number is None:
        return allocation_data.get_string_describing_different_sail_numbers_across_days(
            cadet=cadet
        )
    return get_sail_number_field(cadet=cadet, current_number=current_number)


def get_sail_number_field_on_day(
    cadet: Cadet, day: Day, allocation_data: AllocationData
) -> textInput:
    current_number = make_id_as_int_str(
        allocation_data.get_sail_number_for_boat_on_day(cadet=cadet, day=day)
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


def get_dropdown_input_for_partner_allocation_across_days(
    cadet: Cadet, allocation_data: AllocationData
) -> ListOfLines:
    current_partner_name = allocation_data.get_two_handed_partner_name_for_cadet_across_days_or_none_if_different(
        cadet=cadet
    )
    if current_partner_name is None:
        return (
            allocation_data.get_string_describing_two_handed_partner_name_across_days(
                cadet=cadet
            )
        )

    list_of_other_cadets = allocation_data.list_of_cadets_as_str_at_event_with_matching_schedules_excluding_this_cadet(
        cadet
    )  ### needs to disapply cadets who aren't also available the whole week
    list_of_other_cadets = NO_PARTNERSHIP_LIST + list_of_other_cadets
    okay_to_have_partner_button = okay_to_have_partner_button_across_days(
        cadet=cadet, allocation_data=allocation_data
    )

    return get_dropdown_input_for_partner_allocation(
        cadet=cadet,
        list_of_other_cadets=list_of_other_cadets,
        current_partner_name=current_partner_name,
        okay_to_have_partner_button=okay_to_have_partner_button,
    )


def okay_to_have_partner_button_across_days(
    cadet: Cadet, allocation_data: AllocationData
) -> bool:
    registration_split_allowed = allocation_data.event.reg_splitting_allowed
    boat_exists = allocation_data.cadet_at_event_with_dinghy_object_already_exists_for_cadet_across_days(
        cadet=cadet
    )
    return registration_split_allowed and boat_exists


def get_dropdown_input_for_partner_allocation_on_day(
    cadet: Cadet, day: Day, allocation_data: AllocationData
) -> ListOfLines:
    current_partner_name = allocation_data.get_two_handed_partner_as_str_for_cadet_on_day(
        cadet=cadet, day=day
    )
    list_of_other_cadets = allocation_data.list_of_cadets_as_str_at_event_excluding_cadet_available_on_day(
        cadet=cadet, day=day
    )

    okay_to_have_partner_button = okay_to_have_partner_button_on_day(
        cadet_id=cadet.id, allocation_data=allocation_data, day=day
    )

    return get_dropdown_input_for_partner_allocation(
        cadet=cadet,
        list_of_other_cadets=list_of_other_cadets,
        current_partner_name=current_partner_name,
        okay_to_have_partner_button=okay_to_have_partner_button,
    )


def get_dropdown_input_for_partner_allocation(
    cadet: Cadet,
    list_of_other_cadets: List[str],
    current_partner_name: str,
    okay_to_have_partner_button: bool,
) -> ListOfLines:
    list_of_other_cadets = NO_PARTNERSHIP_LIST + list_of_other_cadets
    dict_of_all_possible_cadets = dict(
        [(cadet_name, cadet_name) for cadet_name in list_of_other_cadets]
    )

    drop_down_input_field = dropDownInput(
        input_name=input_name_from_column_name_and_cadet_id(PARTNER, cadet_id=cadet.id),
        input_label="",
        default_label=current_partner_name,
        dict_of_options=dict_of_all_possible_cadets,
    )

    if okay_to_have_partner_button:
        button_to_add_partner = Button(
            value=button_name_for_add_partner(cadet_id=cadet.id),
            label="Add partner as new cadet",
        )
    else:
        button_to_add_partner = ""

    return ListOfLines([drop_down_input_field, button_to_add_partner])


def okay_to_have_partner_button_on_day(
    cadet_id: str, day: Day, allocation_data: AllocationData
) -> bool:
    registration_split_allowed = allocation_data.event.reg_splitting_allowed
    boat_exists = boat_already_exists_for_cadet_on_day(
        cadet_id=cadet_id, day=day, allocation_data=allocation_data
    )
    return registration_split_allowed and boat_exists


def boat_already_exists_for_cadet_on_day(
    cadet_id: str, day: Day, allocation_data: AllocationData
) -> bool:
    is_missing = (
        allocation_data.list_of_cadets_at_event_with_dinghies.object_with_cadet_id_on_day(
            cadet_id=cadet_id, day=day
        )
        is missing_data
    )

    return not is_missing


def button_name_for_add_partner(cadet_id: str):
    return "addPartner_%s" % cadet_id


def cadet_id_given_partner_button(button_name: str) -> str:
    splitter = button_name.split("_")
    return splitter[1]


NOTES = "Notes"
RESET_DAY_BUTTON_LABEL = "Show all day view"
MAKE_CADET_AVAILABLE_ON_DAY_BUTTON = "Cadet not sailing today - click to change"
