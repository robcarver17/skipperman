from typing import Union


from app.data_access.configuration.configuration import ALL_GROUPS_NAMES
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    dropDownInput,
)
from app.objects.abstract_objects.abstract_tables import RowInTable, Table
from app.objects.abstract_objects.abstract_lines import ListOfLines, _______________
from app.objects.abstract_objects.abstract_buttons import BACK_BUTTON_LABEL, Button
from app.backend.group_allocations.summarise_allocations_data import summarise_allocations_for_event
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.backend.group_allocations.group_allocations_data import (
    AllocationData, get_allocation_data,
)
from app.backend.data.group_allocations import save_current_allocations_for_event

from app.logic.events.constants import (
    ALLOCATION,
    UPDATE_ALLOCATION_BUTTON_LABEL,
)
from app.logic.events.events_in_state import get_event_from_state
from app.objects.cadets import Cadet
from app.objects.groups import Group
from app.objects.events import Event


def display_form_allocate_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
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
    list_of_cadets = allocation_data.list_of_cadets_in_event_active_only

    return Table(
        [get_top_row(allocation_data=allocation_data)]+
        [
            get_row_for_cadet(cadet=cadet, allocation_data=allocation_data)
            for cadet in list_of_cadets
        ]
    )


def get_top_row(allocation_data: AllocationData) -> RowInTable:
    previous_event_names_in_list = allocation_data.previous_event_names()

    ## ensure if we add columns for cadet, add in padding and column names here
    return RowInTable([
        "Previous groups:" ## cadet name
    ]+previous_event_names_in_list+[
        "" ## column for input
    ]
                      )

def get_row_for_cadet(cadet: Cadet, allocation_data: AllocationData) -> RowInTable:
    previous_groups_as_list = allocation_data.previous_groups_as_list_of_str(cadet)
    drop_down_input_field = get_dropdown_input_for_cadet(cadet=cadet, allocation_data=allocation_data)
    ## FIX ME ADD RYA LEVELS AND EXPERIENCE, DAYS AVAILABLE, BOATS, DOUBLE HANDED CREW, PREFERRED GROUP
    return RowInTable(
        [str(cadet)]+

            previous_groups_as_list
            +
            [drop_down_input_field]
    )

def get_dropdown_input_for_cadet(cadet: Cadet, allocation_data: AllocationData) -> dropDownInput:
    current_group = allocation_data.get_current_group_name(cadet)
    drop_down_input_field = dropDownInput(
                input_name=create_field_name_for_cadet_allocation(cadet),
                input_label="Select group:",
                default_label=str(current_group),
                dict_of_options=dict_of_all_possible_groups_for_dropdown_input,
            )
    return drop_down_input_field

def create_field_name_for_cadet_allocation(cadet: Cadet):
    return ALLOCATION + "_" + cadet.id


dict_of_all_possible_groups_for_dropdown_input= dict([(group, group) for group in ALL_GROUPS_NAMES])


def post_form_allocate_cadets(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    if interface.last_button_pressed() == BACK_BUTTON_LABEL:
        return previous_form(interface)
    else:
        return do_allocation_for_cadets_in_form(interface)

def previous_form(interface: abstractInterface):
    return interface.get_new_display_form_for_parent_of_function(display_form_allocate_cadets)

def do_allocation_for_cadets_in_form(interface: abstractInterface):
    event = get_event_from_state(interface)
    allocation_data = get_allocation_data(event)
    list_of_cadets = allocation_data.list_of_cadets_in_event_active_only
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
                "Couldn't allocate group to %s error code %s" % (str(cadet), str(e))
            )

    return interface.get_new_form_given_function(display_form_allocate_cadets)


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


