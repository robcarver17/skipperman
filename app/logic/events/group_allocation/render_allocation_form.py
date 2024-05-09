from typing import Union, List, Tuple

from app.objects.day_selectors import Day

from app.objects.utils import make_id_as_int_str

from app.backend.data.dinghies import load_list_of_club_dinghies, load_list_of_boat_classes
from app.backend.forms.form_utils import input_name_from_column_name_and_cadet_id_and_day, get_availability_checkbox
from app.backend.forms.reorder_form import reorder_table
from app.backend.group_allocations.boat_allocation import summarise_club_boat_allocations_for_event, \
    summarise_class_attendance_for_event
from app.backend.group_allocations.group_allocations_data import get_allocation_data, AllocationData
from app.backend.group_allocations.sorting import sorted_active_cadets
from app.backend.group_allocations.summarise_allocations_data import summarise_allocations_for_event

from app.data_access.configuration.configuration import ALL_GROUPS_NAMES
from app.logic.events.constants import UPDATE_ALLOCATION_BUTTON_LABEL, ALLOCATION, ATTENDANCE, CLUB_BOAT, BOAT_CLASS, SAIL_NUMBER, PARTNER
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_buttons import Button, BACK_BUTTON_LABEL, ButtonBar
from app.objects.abstract_objects.abstract_form import Form, NewForm, dropDownInput, checkboxInput, textInput
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________, DetailListOfLines, Line, \
    DetailLine
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.cadets import Cadet
from app.objects.club_dinghies import NO_BOAT
from app.objects.constants import missing_data
from app.objects.events import Event
from app.objects.dinghies import NO_PARTNERSHIP_LIST

NOTES = "Notes"

def display_form_allocate_cadets_at_event(interface: abstractInterface, event: Event, sort_order: list) -> Union[Form, NewForm]:
    if event.contains_groups:
        star_indicator = "* indicates only compulsory for racing / river training with spotter sheets"
    elif event.reg_splitting_allowed:
        star_indicator = ""
    else:
        star_indicator = ""

    allocations_and_class_summary = get_allocations_and_classes_detail(event=event, interface=interface)
    day_dropdown = ''#HERE
    inner_form = get_inner_form_for_cadet_allocation(event, sort_order=sort_order)
    sort_button_table = sort_buttons_for_allocation_table(sort_order)
    nav_bar = ButtonBar([back_button, update_button])

    return Form(ListOfLines([
                ButtonBar([back_button]),
                    Heading("Cadets in %s " % str(event), size=4), _______________,
                    _______________,
                    allocations_and_class_summary,
                    DetailListOfLines(ListOfLines([
                    _______________,
                    "Specify order that table is sorted in:",
                    sort_button_table]), "Sort order", open=True),
                     _______________,
                    nav_bar,
                    star_indicator,
                    day_dropdown,
                    inner_form,
                    _______________,
                    #nav_bar
                    ])
    )


def get_allocations_and_classes_detail(interface: abstractInterface, event: Event)-> DetailListOfLines:
    if event.contains_groups:
        allocations = summarise_allocations_for_event(interface=interface, event=event)
    elif event.reg_splitting_allowed:
        allocations = "No groups in event- racing only"
    else:
        ##shouldn't happen, but ok
        allocations = ""

    club_dinghies = summarise_club_boat_allocations_for_event(event=event, interface=interface)
    classes = summarise_class_attendance_for_event(event=event, interface=interface)
    return DetailListOfLines(ListOfLines([
        _______________,
        allocations,
        _______________,
        "Allocated club dinghies:",
        club_dinghies,
        _______________,
        "Classes",
        classes,
        _______________]), "Summary", open=False)




update_button = Button(UPDATE_ALLOCATION_BUTTON_LABEL, nav_button=True)
back_button = Button(BACK_BUTTON_LABEL, nav_button=True)


def sort_buttons_for_allocation_table(sort_order: list) -> Table:
    return reorder_table(sort_order)


def get_inner_form_for_cadet_allocation(event: Event, sort_order: list) -> Table:
    allocation_data = get_allocation_data(event)
    list_of_cadets = sorted_active_cadets(allocation_data, sort_order)
    list_of_cadets = allocation_data.list_of_cadets_in_event_active_only[:50]
    return Table(
        [get_top_row(allocation_data=allocation_data)]+
        [
            get_row_for_cadet(cadet=cadet, allocation_data=allocation_data)
            for cadet in list_of_cadets
        ], has_column_headings=True, has_row_headings=True
    )



def get_top_row(allocation_data: AllocationData) -> RowInTable:
    previous_event_names_in_list = allocation_data.previous_event_names()
    info_field_names = allocation_data.group_info_fields()

    event = allocation_data.event


    input_field_names_over_days =[]
    for day in event.weekdays_in_event():
        input_field_names_over_days+=get_input_field_headings_for_day(
            day=day,
            event_contains_groups=event.contains_groups
        )


    input_field_names = ["Set: Availability"]+input_field_names_over_days+["Notes"]

    return RowInTable([
        "" ## cadet name
    ]+previous_event_names_in_list+info_field_names+["Official qualification"]+input_field_names
                      )

def get_input_field_headings_for_day(day: Day, event_contains_groups: bool) -> list:

    if event_contains_groups:
        star="*"
    else:
        star = ""
    input_field_names = ["Allocate: group (%s)" % day.name,
                         "Allocate: Club boat(%s)" % day.name,
                         "Allocate: Class of boat%s (%s)" % (star , day.name),
                         "Edit: Sail number %s (%s)" % (star , day.name),
                         "Allocate: Two handed partner (%s)" % day.name]

    return input_field_names


def get_row_for_cadet(cadet: Cadet, allocation_data: AllocationData) -> RowInTable:
    previous_groups_as_list = allocation_data.previous_groups_as_list_of_str(cadet)
    previous_group_info = allocation_data.group_info_dict_for_cadet_as_ordered_list(cadet)
    previous_group_info  = [make_long_thing_detail_box(field) for field in previous_group_info ]
    input_fields = get_input_fields_for_cadet(cadet, allocation_data)
    qualification = allocation_data.get_highest_qualification_for_cadet(cadet)

    return RowInTable(
            [str(cadet)]+
            previous_groups_as_list
            +previous_group_info+[qualification]+
            input_fields
        )

def make_long_thing_detail_box(some_string:str):
    if len(some_string)>100:
        return DetailLine(string=some_string, name="Detail")
    else:
        return some_string

def get_input_fields_for_cadet(cadet: Cadet, allocation_data: AllocationData) -> list:
    notes_field = get_notes_field(cadet=cadet, allocation_data=allocation_data)
    days_attending_field = get_days_attending_field(cadet=cadet, allocation_data=allocation_data)

    input_fields_by_day =[]
    for day in allocation_data.event.weekdays_in_event():
        input_fields_by_day+=get_input_fields_for_cadet_on_day(
            cadet=cadet,
            day=day,
            allocation_data=allocation_data
        )

    input_fields = [
                    days_attending_field]+input_fields_by_day+[
                        notes_field
                         ]

    return input_fields


def get_input_fields_for_cadet_on_day(cadet: Cadet, day: Day, allocation_data: AllocationData) -> list:
    group_allocation_field = get_dropdown_input_for_group_allocation_on_day(cadet=cadet, allocation_data=allocation_data, day=day)
    dropdown_input_for_club_boat_allocation = get_dropdown_input_for_club_boat_allocation_on_day(cadet=cadet, allocation_data=allocation_data, day=day)
    dropdown_input_for_boat_class_allocation =  get_dropdown_input_for_boat_class_allocation_on_day(cadet=cadet, allocation_data=allocation_data, day=day)
    dropdown_input_for_partner_allocation= get_dropdown_input_for_partner_allocation_on_day(cadet=cadet, allocation_data=allocation_data, day=day)
    sail_number_field = get_sail_number_field_on_day(cadet=cadet, allocation_data=allocation_data, day=day)

    input_fields = [group_allocation_field,
                         dropdown_input_for_club_boat_allocation,
                         dropdown_input_for_boat_class_allocation,
                         sail_number_field,
                         dropdown_input_for_partner_allocation,
                         ]

    return input_fields


def get_dropdown_input_for_group_allocation_on_day(cadet: Cadet, day: Day, allocation_data: AllocationData) -> Union[dropDownInput, str]:
    if allocation_data.event.contains_groups:
        current_group = allocation_data.get_current_group_name_for_day(cadet=cadet, day=day)
        drop_down_input_field = dropDownInput(
                    input_name=input_name_from_column_name_and_cadet_id_and_day(ALLOCATION, cadet_id=cadet.id, day=day),
                    input_label="",
                    default_label=current_group,
                    dict_of_options=dict_of_all_possible_groups_for_dropdown_input,
                )
        return drop_down_input_field
    else:
        return "Racing"

dict_of_all_possible_groups_for_dropdown_input= dict([(group, group) for group in ALL_GROUPS_NAMES])

def get_notes_field(cadet: Cadet, allocation_data: AllocationData):
    cadet_at_event = allocation_data.cadets_at_event_including_non_active.cadet_at_event(cadet.id)

    return textInput(
        input_name=input_name_from_column_name_and_cadet_id_and_day(column_name=NOTES, cadet_id=cadet.id),
        input_label="",
        value=cadet_at_event.notes
    )



def get_days_attending_field(cadet: Cadet, allocation_data: AllocationData)-> checkboxInput:

    days_attending_field = get_availability_checkbox(availability=allocation_data.cadet_availability_at_event(cadet),
                                     event=allocation_data.event,
                                     input_name=input_name_from_column_name_and_cadet_id_and_day(column_name=ATTENDANCE,
                                                                                                 cadet_id=cadet.id),
                                     line_break=True)
    return days_attending_field


def get_dropdown_input_for_club_boat_allocation_on_day(cadet: Cadet, day: Day, allocation_data: AllocationData) -> dropDownInput:
    current_club_boat = allocation_data.get_current_club_boat_name_on_day(cadet=cadet, day=day)
    dict_of_club_dinghies_for_dropdown_input = get_list_of_club_dinghies_for_dropdown(allocation_data)
    drop_down_input_field = dropDownInput(
                input_name=input_name_from_column_name_and_cadet_id_and_day(CLUB_BOAT, cadet_id=cadet.id, day=day),
                input_label="",
                default_label=str(current_club_boat),
                dict_of_options=dict_of_club_dinghies_for_dropdown_input,
            )
    return drop_down_input_field

def get_list_of_club_dinghies_for_dropdown(allocation_data: AllocationData):
    club_dinghies = allocation_data.list_of_club_boats
    dict_of_club_dinghies_for_dropdown_input = {NO_BOAT: NO_BOAT}
    dict_of_all_possible_club_boats= dict([(dinghy.name, dinghy.name) for dinghy in club_dinghies])
    dict_of_club_dinghies_for_dropdown_input.update(dict_of_all_possible_club_boats)

    return dict_of_club_dinghies_for_dropdown_input


def get_dropdown_input_for_boat_class_allocation_on_day(cadet: Cadet, day: Day, allocation_data: AllocationData) -> dropDownInput:
    current_boat_class = allocation_data.get_name_of_class_of_boat_on_day(cadet=cadet, day=day)
    dict_of_all_possible_boat_classes = get_dict_of_boat_classes(allocation_data)
    drop_down_input_field = dropDownInput(
                input_name=input_name_from_column_name_and_cadet_id_and_day(BOAT_CLASS, cadet_id=cadet.id, day=day),
                input_label="",
                default_label=str(current_boat_class),
                dict_of_options=dict_of_all_possible_boat_classes
            )
    return drop_down_input_field

def get_dict_of_boat_classes(allocation_data: AllocationData):
    boat_classes = allocation_data.list_of_dinghies
    dict_of_all_possible_boat_classes= dict([(dinghy.name, dinghy.name) for dinghy in boat_classes])
    return dict_of_all_possible_boat_classes

def get_sail_number_field_on_day(cadet: Cadet, day: Day, allocation_data: AllocationData)-> textInput:
    current_number = make_id_as_int_str(allocation_data.get_sail_number_for_boat_on_day(cadet=cadet, day=day))
    sail_number_field = textInput(
        input_name=input_name_from_column_name_and_cadet_id_and_day(cadet_id=cadet.id, column_name=SAIL_NUMBER, day=day),
        value=current_number,
        input_label=""
    )
    return sail_number_field


def get_dropdown_input_for_partner_allocation_on_day(cadet: Cadet, day: Day, allocation_data: AllocationData) -> ListOfLines:
    current_partner_name = allocation_data.get_two_handed_partner_name_for_cadet_on_day(cadet=cadet, day=day)
    list_of_other_cadets = allocation_data.list_of_names_of_cadets_at_event_excluding_cadet(cadet)
    list_of_other_cadets = NO_PARTNERSHIP_LIST+list_of_other_cadets
    dict_of_all_possible_cadets = dict(
        [
            (cadet_name, cadet_name)
            for cadet_name in list_of_other_cadets
        ]
    )

    drop_down_input_field = dropDownInput(
                input_name=input_name_from_column_name_and_cadet_id_and_day(PARTNER, cadet_id=cadet.id, day=day),
                input_label="",
                default_label=current_partner_name,
                dict_of_options=dict_of_all_possible_cadets
            )

    if okay_to_have_partner_button_on_day(cadet_id=cadet.id, allocation_data=allocation_data, day=day):
        button_to_add_partner = Button(value=button_name_for_add_partner_on_day(cadet_id=cadet.id, day=day), label="Add partner as new cadet")
    else:
        button_to_add_partner = ""

    return ListOfLines([drop_down_input_field, button_to_add_partner])


def okay_to_have_partner_button_on_day(cadet_id: str, day: Day, allocation_data: AllocationData)-> bool:
    registration_split_allowed = allocation_data.event.reg_splitting_allowed
    boat_exists = boat_already_exists_for_cadet_on_day(cadet_id=cadet_id,day=day, allocation_data=allocation_data)
    return registration_split_allowed and boat_exists

def boat_already_exists_for_cadet_on_day(cadet_id: str, day: Day, allocation_data: AllocationData)-> bool:
    is_missing = allocation_data.list_of_cadets_at_event_with_dinghies.object_with_cadet_id_on_day(cadet_id=cadet_id, day=day) is missing_data

    return not is_missing

def button_name_for_add_partner_on_day(cadet_id: str, day: Day):
    return "addPartner_%s_%s" % (day.name, cadet_id)

def day_and_cadet_id_given_partner_button(button_name: str) -> Tuple[Day, str]:
    splitter =button_name.split("_")
    return Day[splitter[1]], splitter[2]

def list_of_all_add_partner_buttons(interface: abstractInterface):
    event = get_event_from_state(interface)
    allocation_data = get_allocation_data(event)
    list_of_cadets = sorted_active_cadets(allocation_data)
    list_of_buttons = []
    for day in allocation_data.event.weekdays_in_event():
        list_of_buttons+= [button_name_for_add_partner_on_day(cadet_id=id, day=day) for id in list_of_cadets.list_of_ids]

    return list_of_buttons