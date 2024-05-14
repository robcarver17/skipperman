from typing import Union

from app.objects.constants import missing_data

from app.logic.events.cadets_at_event.track_cadet_id_in_state_when_importing import get_current_cadet_id_at_event

from app.logic.events.group_allocation.input_fields import get_notes_field, get_days_attending_field, \
    make_long_thing_detail_box, get_input_fields_for_cadet, button_name_for_add_partner, RESET_DAY_BUTTON_LABEL, \
    make_cadet_available_button_name
from app.logic.events.group_allocation.store_state import  no_day_set_in_state, \
    get_day_from_state_or_none

from app.backend.forms.reorder_form import reorder_table
from app.backend.group_allocations.boat_allocation import summarise_club_boat_allocations_for_event, \
    summarise_class_attendance_for_event
from app.backend.group_allocations.group_allocations_data import get_allocation_data, AllocationData
from app.backend.group_allocations.sorting import sorted_active_cadets
from app.backend.group_allocations.summarise_allocations_data import summarise_allocations_for_event

from app.logic.events.constants import UPDATE_ALLOCATION_BUTTON_LABEL
from app.logic.events.events_in_state import get_event_from_state
from app.objects.abstract_objects.abstract_buttons import Button, BACK_BUTTON_LABEL, ButtonBar
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________, DetailListOfLines, Line
from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_text import Heading
from app.objects.cadets import Cadet
from app.objects.events import Event


def display_form_allocate_cadets_at_event(interface: abstractInterface, event: Event, sort_order: list) -> Union[Form, NewForm]:
    if event.contains_groups:
        star_indicator = "* indicates only compulsory for racing / river training with spotter sheets"
    elif event.reg_splitting_allowed:
        star_indicator = ""
    else:
        star_indicator = ""

    allocations_and_class_summary = get_allocations_and_classes_detail(event=event, interface=interface)
    day_dropdown = get_day_buttons(interface)
    inner_form = get_inner_form_for_cadet_allocation(interface=interface, event=event, sort_order=sort_order)
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
                    nav_bar
                    ])
    )


def get_day_buttons(interface: abstractInterface) -> Line:
    if no_day_set_in_state(interface):
        event = get_event_from_state(interface)
        event_weekdays = event.weekdays_in_event()
        weekday_buttons = [Button(day.name) for day in event_weekdays]
        return Line(["  Choose day to edit (if you want to allocate cadets to different groups, boats or partners on specific days): "]+weekday_buttons)
    else:
        day = get_day_from_state_or_none(interface)
        return Line(["Currently editing %s: " % day.name, Button(RESET_DAY_BUTTON_LABEL)])

def list_of_all_day_button_names(interface: abstractInterface):
    event = get_event_from_state(interface)
    event_weekdays = event.weekdays_in_event()
    weekday_buttons = [day.name for day in event_weekdays]
    weekday_buttons.append(RESET_DAY_BUTTON_LABEL)

    return weekday_buttons

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


def get_inner_form_for_cadet_allocation(interface: abstractInterface, event: Event, sort_order: list) -> Table:
    allocation_data = get_allocation_data(interface=interface, event=event)
    day_or_none = get_day_from_state_or_none(interface)
    list_of_cadets = sorted_active_cadets(allocation_data=allocation_data, sort_order=sort_order, day_or_none=day_or_none)
    return Table(
        [get_top_row(allocation_data=allocation_data, interface=interface)]+
        [
            get_row_for_cadet(interface=interface, cadet=cadet, allocation_data=allocation_data)
            for cadet in list_of_cadets
        ], has_column_headings=True, has_row_headings=True
    )

NUMBER_OF_PREVIOUS_EVENTS = 3

def get_top_row(interface: abstractInterface, allocation_data: AllocationData) -> RowInTable:
    previous_event_names_in_list = allocation_data.previous_event_names(number_of_events=NUMBER_OF_PREVIOUS_EVENTS)
    info_field_names = allocation_data.group_info_fields()

    input_field_names_over_days =get_daily_input_field_headings(allocation_data=allocation_data, interface=interface)

    return RowInTable([
        "" ## cadet name
    , "Set Availability"]+previous_event_names_in_list+info_field_names+["Official qualification", "Notes"]+input_field_names_over_days
                      )


def get_daily_input_field_headings(interface: abstractInterface, allocation_data: AllocationData) -> list:
    event = allocation_data.event
    if no_day_set_in_state(interface):
        return get_input_field_headings_for_day('All days', event_contains_groups=event.contains_groups)
    else:
        day = get_day_from_state_or_none(interface)
        return get_input_field_headings_for_day(day.name, event_contains_groups=event.contains_groups)


def get_input_field_headings_for_day(day_name:str, event_contains_groups: bool) -> list:

    if event_contains_groups:
        star="*"
    else:
        star = ""
    input_field_names = ["Allocate: group (%s)" % day_name,
                         "Allocate: Club boat(%s)" % day_name,
                         "Allocate: Class of boat%s (%s)" % (star , day_name),
                         "Edit: Sail number %s (%s)" % (star , day_name),
                         "Allocate: Two handed partner (%s)" % day_name]

    return input_field_names


def get_row_for_cadet(interface: abstractInterface, cadet: Cadet, allocation_data: AllocationData) -> RowInTable:
    cell_for_cadet = get_cell_for_cadet(interface=interface, cadet=cadet, allocation_data=allocation_data)
    previous_groups_as_list = allocation_data.previous_groups_as_list_of_str(cadet, number_of_events=NUMBER_OF_PREVIOUS_EVENTS)
    previous_group_info = allocation_data.group_info_dict_for_cadet_as_ordered_list(cadet)
    previous_group_info  = [make_long_thing_detail_box(field) for field in previous_group_info]
    input_fields = get_input_fields_for_cadet(interface=interface, cadet=cadet, allocation_data=allocation_data)
    qualification = allocation_data.get_highest_qualification_for_cadet(cadet)
    notes_field = get_notes_field(cadet=cadet, allocation_data=allocation_data)
    days_attending_field = get_days_attending_field(cadet=cadet, allocation_data=allocation_data)

    return RowInTable(
        [cell_for_cadet, days_attending_field] +
        previous_groups_as_list
        + previous_group_info + [qualification, notes_field] +
        input_fields
        )

MAX_EVENTS_TO_SHOW = 12

def get_cell_for_cadet(interface: abstractInterface, allocation_data: AllocationData, cadet: Cadet) -> Union[ListOfLines, Button]:
    if this_cadet_has_been_clicked_on_already(interface=
                                              interface, cadet=
                                              cadet):
        dict_of_groups = allocation_data.previous_groups_as_dict(cadet=cadet, number_of_events=MAX_EVENTS_TO_SHOW)
        list_of_groups_as_str = ["%s: %s" % (str(event), group.group_name) for event, group in dict_of_groups.items()]
        return ListOfLines([str(cadet), "Previous groups:-"]+list_of_groups_as_str).add_Lines()
    else:
        return Button(str(cadet), value=get_button_id_for_cadet(cadet.id))

def this_cadet_has_been_clicked_on_already(interface: abstractInterface, cadet: Cadet):
    cadet_id = get_current_cadet_id_at_event(interface)
    if cadet_id is missing_data:
        print("No stored cadet id")
        return False
    return cadet_id == cadet.id

def get_button_id_for_cadet(id:str)-> str:
    return "cadet_%s" % id

def get_list_of_all_cadet_buttons(interface: abstractInterface):
    list_of_cadets = get_list_of_all_cadets(interface)
    return  [get_button_id_for_cadet(id) for id in list_of_cadets.list_of_ids]

def cadet_id_from_cadet_button(button_str):
    return button_str.split("_")[1]


def get_list_of_all_add_partner_buttons(interface: abstractInterface):
    list_of_cadets = get_list_of_all_cadets(interface)
    return  [button_name_for_add_partner(cadet_id=id) for id in list_of_cadets.list_of_ids]

def get_list_of_all_add_cadet_availability_buttons(interface: abstractInterface):
    list_of_cadets = get_list_of_all_cadets(interface)

    return  [make_cadet_available_button_name(cadet) for cadet in list_of_cadets]

def get_list_of_all_cadets(interface: abstractInterface):
    event = get_event_from_state(interface)
    allocation_data = get_allocation_data(interface=interface, event=event)
    list_of_cadets = sorted_active_cadets(allocation_data)

    return list_of_cadets