from dataclasses import dataclass
from typing import Union


from app.data_access.configuration.configuration import ALL_GROUPS_NAMES, UNALLOCATED_GROUP_NAME
from app.logic.abstract_logic_api import initial_state_form
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    dropDownInput,
)
from app.objects.abstract_objects.abstract_tables import RowInTable, Table
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL, back_button, Button
from app.backend.group_allocations.summarise_allocations_data import summarise_allocations_for_event, reorder_list_of_cadets_by_allocated_group
from app.logic.abstract_interface import (
    abstractInterface,
)
from app.backend.group_allocations.cadet_event_allocations import get_list_of_cadets_in_master_event, get_current_allocations, \
    save_current_allocations_for_event
from app.backend.group_allocations.previous_allocations import allocation_for_cadet_in_previous_events, get_dict_of_allocations_for_events_and_list_of_cadets
from app.backend.wa_import.load_and_save_wa_mapped_events import load_master_event

from app.logic.events.constants import (
    ALLOCATION,
    UPDATE_ALLOCATION_BUTTON_LABEL,
    VIEW_EVENT_STAGE,
)
from app.logic.events.events_in_state import get_event_from_state
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.groups import ListOfCadetIdsWithGroups, Group
from app.objects.events import Event, list_of_events_excluding_one_event
from app.objects.master_event import MasterEvent


def display_form_allocate_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    allocations = summarise_allocations_for_event(event)
    inner_form = get_inner_form_for_cadet_allocation(event)

    return Form(
        allocations +
        ListOfLines([back_button,
                    inner_form,
                    Button(UPDATE_ALLOCATION_BUTTON_LABEL)])
    )


@dataclass
class AllocationData:
    current_allocation_for_event: ListOfCadetIdsWithGroups
    master_event_data: MasterEvent
    list_of_cadets: ListOfCadets
    previous_allocations_as_dict: dict

    def previous_groups_as_list_of_str(self, cadet: Cadet) -> list:
        previous_groups_as_list = self.previous_groups_as_list(cadet)
        return [str(x) for x in previous_groups_as_list]


    def previous_groups_as_list(self, cadet: Cadet) -> list:
        return allocation_for_cadet_in_previous_events(cadet=cadet,previous_allocations_as_dict=self.previous_allocations_as_dict)

    def get_last_group(self, cadet: Cadet):
        previous_allocation = self.previous_groups_as_list(cadet)
        previous_allocation.reverse() ## last event first when considering
        for allocation in previous_allocation:
            if allocation == UNALLOCATED_GROUP_NAME:
                continue
            else:
                return allocation

        return UNALLOCATED_GROUP_NAME

    def get_current_group(self, cadet: Cadet):
        try:
            current_allocation = self.current_allocation_for_event.item_with_cadet_id(
                cadet_id=cadet.id
            ).group

        except:
            current_allocation = self.get_last_group(cadet)

        return current_allocation


def get_inner_form_for_cadet_allocation(event: Event) -> Table:
    allocation_data = get_allocation_data(event)
    list_of_cadets = allocation_data.list_of_cadets

    return Table(
        [get_top_row(allocation_data=allocation_data)]+
        [
            get_row_for_cadet(cadet=cadet, allocation_data=allocation_data)
            for cadet in list_of_cadets
        ]
    )


def get_allocation_data(event: Event) -> AllocationData:
    current_allocation_for_event = get_current_allocations(event)
    master_event_data = load_master_event(event)
    unsorted_list_of_cadets = get_list_of_cadets_in_master_event(event)
    list_of_cadets = reorder_list_of_cadets_by_allocated_group(list_of_cadets=unsorted_list_of_cadets, current_allocation_for_event=current_allocation_for_event)
    list_of_events = list_of_events_excluding_one_event(event_to_exclude=event)
    previous_allocations_as_dict = get_dict_of_allocations_for_events_and_list_of_cadets(list_of_events)

    return AllocationData(
        current_allocation_for_event=current_allocation_for_event,
        master_event_data=master_event_data,
        list_of_cadets=list_of_cadets,
        previous_allocations_as_dict=previous_allocations_as_dict
    )

def get_top_row(allocation_data: AllocationData) -> RowInTable:
    previous_events = list(allocation_data.previous_allocations_as_dict.keys())
    previous_events_as_list_of_str = [str(event) for event in previous_events]

    ## ensure if we add columns for cadet, add in padding and column names here
    return RowInTable([
        "Previous groups:"
    ]+previous_events_as_list_of_str+[
        "" ## column for input
    ]
                      )

def get_row_for_cadet(cadet: Cadet, allocation_data: AllocationData) -> RowInTable:
    current_group = allocation_data.get_current_group(cadet)
    previous_groups_as_list = allocation_data.previous_groups_as_list_of_str(cadet)
    return RowInTable(
        [
            str(cadet)]+
            previous_groups_as_list
            +[dropDownInput(
                input_name=create_field_name_for_cadet_allocation(cadet),
                input_label="Select group:",
                default_label=str(current_group),
                dict_of_options=dict_of_groups(),
            ),
        ]
    )


def create_field_name_for_cadet_allocation(cadet: Cadet):
    return ALLOCATION + "_" + cadet.id


def dict_of_groups():
    return dict([(group, group) for group in ALL_GROUPS_NAMES])


def post_form_allocate_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    if interface.last_button_pressed() == BACK_BUTTON_LABEL:
        return NewForm(VIEW_EVENT_STAGE)
    event = get_event_from_state(interface)
    allocation_data = get_allocation_data(event)
    list_of_cadets = allocation_data.list_of_cadets
    for cadet in list_of_cadets:
        try:
            do_allocation_for_cadet_at_event(
                event=event,
                interface=interface,
                cadet=cadet,
                allocation_data=allocation_data,
            )

        except Exception as e:
            interface.log_error(
                "Couldn't allocate %s error code %s" % (str(cadet), str(e))
            )
            return initial_state_form

    return NewForm(VIEW_EVENT_STAGE)


def do_allocation_for_cadet_at_event(
    event: Event,
    cadet: Cadet,
    allocation_data: AllocationData,
    interface: abstractInterface,
):
    allocation_str = interface.value_from_form(
        create_field_name_for_cadet_allocation(cadet)
    )
    print("Allocation %s for cadet %s" % (allocation_str, str(cadet)))
    chosen_group = Group(allocation_str)
    allocation_data.current_allocation_for_event.update_group_for_cadet(
        cadet=cadet, chosen_group=chosen_group
    )
    save_current_allocations_for_event(
        list_of_cadets_with_groups=allocation_data.current_allocation_for_event,
        event=event,
    )


