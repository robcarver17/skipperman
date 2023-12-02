from dataclasses import dataclass
from typing import Union

from app.data_access.configuration.configuration import ALL_GROUPS, UNALLOCATED_GROUP
from app.logic.abstract_logic_api import initial_state_form
from app.logic.forms_and_interfaces.abstract_form import (
    Form,
    NewForm,
    Line,
    ListOfLines,
    dropDownInput,
    cancel_button,
    Button,
    Table,
    RowInTable,
    ElementsInTable,
    back_button,
    BACK_BUTTON_LABEL,
)
from app.logic.forms_and_interfaces.abstract_interface import (
    abstractInterface,
    form_with_message_and_finished_button,
)
from app.logic.allocation.allocations_data import (
    get_list_of_cadets_in_master_event,
    get_previous_allocations,
    get_current_allocations,
    save_current_allocations_for_event,
    update_previous_allocations,
)
from app.logic.events.backend.load_and_save_wa_mapped_events import load_master_event

from app.logic.events.constants import (
    ALLOCATION,
    UPDATE_ALLOCATION_BUTTON_LABEL,
    VIEW_EVENT_STAGE,
)
from app.logic.events.utilities import get_event_from_state
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.groups import ListOfCadetIdsWithGroups, Group
from app.objects.events import Event
from app.objects.master_event import MasterEvent


def display_form_allocate_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    inner_form = get_inner_form_for_cadet_allocation(event)

    return Form(
        ListOfLines([back_button, inner_form, Button(UPDATE_ALLOCATION_BUTTON_LABEL)])
    )


@dataclass
class AllocationData:
    all_previous_allocations: ListOfCadetIdsWithGroups
    current_allocation_for_event: ListOfCadetIdsWithGroups
    master_event_data: MasterEvent
    list_of_cadets: ListOfCadets

    def get_last_group(self, cadet: Cadet):
        try:
            previous_allocation = self.all_previous_allocations.item_with_cadet_id(
                cadet_id=cadet.id
            ).group
        except:
            previous_allocation = UNALLOCATED_GROUP

        return previous_allocation

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
        [
            get_row_for_cadet(cadet=cadet, allocation_data=allocation_data)
            for cadet in list_of_cadets
        ]
    )


def get_allocation_data(event: Event) -> AllocationData:
    all_previous_allocations = get_previous_allocations()
    current_allocation_for_event = get_current_allocations(event)
    master_event_data = load_master_event(event)
    list_of_cadets = get_list_of_cadets_in_master_event(event)

    return AllocationData(
        all_previous_allocations=all_previous_allocations,
        current_allocation_for_event=current_allocation_for_event,
        master_event_data=master_event_data,
        list_of_cadets=list_of_cadets,
    )


def get_row_for_cadet(cadet: Cadet, allocation_data: AllocationData) -> RowInTable:
    current_group = allocation_data.get_current_group(cadet)
    previous_group = allocation_data.get_last_group(cadet)
    return RowInTable(
        [
            str(cadet),
            "Previous group: %s"
            % str(previous_group),  ## in time add other useful fields here
            dropDownInput(
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
    return dict([(group, group) for group in ALL_GROUPS])


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

    allocation_data.all_previous_allocations.update_group_for_cadet(
        cadet=cadet, chosen_group=chosen_group
    )
    update_previous_allocations(allocation_data.all_previous_allocations)
