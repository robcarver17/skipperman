from typing import Union

from app.backend.data.resources import load_list_of_club_dinghies, load_list_of_boat_classes
from app.backend.forms.form_utils import input_name_from_column_name_and_cadet_id, get_availability_checkbox
from app.backend.group_allocations.group_allocations_data import get_allocation_data, AllocationData
from app.backend.group_allocations.summarise_allocations_data import summarise_allocations_for_event

from app.data_access.configuration.configuration import ALL_GROUPS_NAMES
from app.logic.events.constants import UPDATE_ALLOCATION_BUTTON_LABEL, ALLOCATION, ATTENDANCE, CLUB_BOAT, BOAT_CLASS, SAIL_NUMBER, PARTNER
from app.objects.abstract_objects.abstract_buttons import Button, BACK_BUTTON_LABEL
from app.objects.abstract_objects.abstract_form import Form, NewForm, dropDownInput, checkboxInput, textInput
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.cadets import Cadet
from app.objects.club_dinghies import NO_BOAT
from app.objects.events import Event
from app.objects.dinghies import NOT_ALLOCATED, NO_PARTNER_REQUIRED

def display_form_allocate_cadets_at_event(event: Event) -> Union[Form, NewForm]:
    allocations = summarise_allocations_for_event(event)
    inner_form = get_inner_form_for_cadet_allocation(event)
    back_button= Button(BACK_BUTTON_LABEL)

    return Form(ListOfLines(["Allocated cadets to groups in %s" % str(event), _______________,
                            allocations,

                    _______________,
            back_button,
                     _______________,
                     update_button,
                    inner_form,
                     update_button,
                     _______________,
                     back_button
                    ])
    )


update_button = Button(UPDATE_ALLOCATION_BUTTON_LABEL, big=True)


def get_inner_form_for_cadet_allocation(event: Event) -> Table:
    allocation_data = get_allocation_data(event)
    list_of_cadets = allocation_data.list_of_cadets_in_event

    return Table(
        [get_top_row(allocation_data=allocation_data)]+
        [
            get_row_for_cadet(cadet=cadet, allocation_data=allocation_data)
            for cadet in list_of_cadets
        ]
    )


def get_top_row(allocation_data: AllocationData) -> RowInTable:
    previous_event_names_in_list = allocation_data.previous_event_names()
    info_field_names = allocation_data.group_info_fields()
    input_field_names = ["Allocated group",
                         "Availability",
                         "Allocate: Club boat",
                         "Allocate: Class of boat",
                         "Edit: Sail number",
                         "Allocate: Two handed partner"
                         ]

    ## ensure if we add columns for cadet, add in padding and column names here
    return RowInTable([
        "" ## cadet name
    ]+previous_event_names_in_list+info_field_names+input_field_names
                      )


def get_row_for_cadet(cadet: Cadet, allocation_data: AllocationData) -> RowInTable:
    previous_groups_as_list = allocation_data.previous_groups_as_list_of_str(cadet)
    previous_group_info = allocation_data.group_info_dict_for_cadet_as_ordered_list(cadet)
    input_fields = get_input_fields_for_cadet(cadet, allocation_data)

    ## FIX ME ADD RYA LEVELS AND EXPERIENCE
    return RowInTable(
            [str(cadet)]+
            previous_groups_as_list
            +previous_group_info+
            input_fields
        )


def get_input_fields_for_cadet(cadet: Cadet, allocation_data: AllocationData) -> list:
    group_allocation_field = get_dropdown_input_for_group_allocation(cadet=cadet, allocation_data=allocation_data)
    days_attending_field = get_days_attending_field(cadet=cadet, allocation_data=allocation_data)
    dropdown_input_for_club_boat_allocation = get_dropdown_input_for_club_boat_allocation(cadet=cadet, allocation_data=allocation_data)
    dropdown_input_for_boat_class_allocation =  get_dropdown_input_for_boat_class_allocation(cadet=cadet, allocation_data=allocation_data)
    dropdown_input_for_partner_allocation= get_dropdown_input_for_partner_allocation(cadet=cadet, allocation_data=allocation_data)
    sail_number_field = get_sail_number_field(cadet=cadet, allocation_data=allocation_data)

    input_fields = [group_allocation_field,
                    days_attending_field,
                         dropdown_input_for_club_boat_allocation,
                         dropdown_input_for_boat_class_allocation,
                         sail_number_field,
                         dropdown_input_for_partner_allocation,
                         ]

    return input_fields


def get_dropdown_input_for_group_allocation(cadet: Cadet, allocation_data: AllocationData) -> dropDownInput:
    current_group = allocation_data.get_current_group_name(cadet)
    drop_down_input_field = dropDownInput(
                input_name=input_name_from_column_name_and_cadet_id(ALLOCATION, cadet_id=cadet.id),
                input_label="",
                default_label=current_group,
                dict_of_options=dict_of_all_possible_groups_for_dropdown_input,
            )
    return drop_down_input_field

dict_of_all_possible_groups_for_dropdown_input= dict([(group, group) for group in ALL_GROUPS_NAMES])


def get_days_attending_field(cadet: Cadet, allocation_data: AllocationData)-> checkboxInput:

    days_attending_field = get_availability_checkbox(availability=allocation_data.cadet_availability_at_event(cadet),
                                     event=allocation_data.event,
                                     input_name=input_name_from_column_name_and_cadet_id(ATTENDANCE,
                                                                                         cadet_id=cadet.id),
                                     line_break=True)
    return days_attending_field


def get_dropdown_input_for_club_boat_allocation(cadet: Cadet, allocation_data: AllocationData) -> dropDownInput:
    current_club_boat = allocation_data.get_current_club_boat_name(cadet)
    drop_down_input_field = dropDownInput(
                input_name=input_name_from_column_name_and_cadet_id(CLUB_BOAT, cadet_id=cadet.id),
                input_label="",
                default_label=str(current_club_boat),
                dict_of_options=dict_of_club_dinghies_for_dropdown_input,
            )
    return drop_down_input_field

club_dinghies = load_list_of_club_dinghies()
dict_of_club_dinghies_for_dropdown_input = {NO_BOAT: NO_BOAT}
dict_of_all_possible_club_boats= dict([(dinghy.name, dinghy.name) for dinghy in club_dinghies])
dict_of_club_dinghies_for_dropdown_input.update(dict_of_all_possible_club_boats)



def get_dropdown_input_for_boat_class_allocation(cadet: Cadet, allocation_data: AllocationData) -> dropDownInput:
    current_boat_class = allocation_data.get_name_of_class_of_boat(cadet)
    drop_down_input_field = dropDownInput(
                input_name=input_name_from_column_name_and_cadet_id(BOAT_CLASS, cadet_id=cadet.id),
                input_label="",
                default_label=str(current_boat_class),
                dict_of_options=dict_of_all_possible_boat_classes
            )
    return drop_down_input_field

boat_classes = load_list_of_boat_classes()
dict_of_all_possible_boat_classes= dict([(dinghy.name, dinghy.name) for dinghy in boat_classes])

def get_sail_number_field(cadet: Cadet, allocation_data: AllocationData)-> textInput:
    current_number = allocation_data.get_sail_number_for_boat(cadet)
    sail_number_field = textInput(
        input_name=input_name_from_column_name_and_cadet_id(cadet_id=cadet.id, column_name=SAIL_NUMBER),
        value=current_number,
        input_label=""
    )
    return sail_number_field


def get_dropdown_input_for_partner_allocation(cadet: Cadet, allocation_data: AllocationData) -> dropDownInput:
    current_partner_name = allocation_data.get_two_handed_partner_name_for_cadet(cadet)
    list_of_other_cadets = allocation_data.list_of_names_of_cadets_at_event_excluding_cadet(cadet)
    list_of_other_cadets.insert(0,NO_PARTNER_REQUIRED)
    list_of_other_cadets.insert(0,NOT_ALLOCATED)
    dict_of_all_possible_cadets = dict(
        [
            (cadet_name, cadet_name)
            for cadet_name in list_of_other_cadets
        ]
    )

    drop_down_input_field = dropDownInput(
                input_name=input_name_from_column_name_and_cadet_id(PARTNER, cadet_id=cadet.id),
                input_label="",
                default_label=current_partner_name,
                dict_of_options=dict_of_all_possible_cadets
            )

    return drop_down_input_field

