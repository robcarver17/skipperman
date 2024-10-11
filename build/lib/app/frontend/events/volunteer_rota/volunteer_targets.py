from typing import List

from app.frontend.forms.swaps import is_ready_to_swap
from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_buttons import Button

from app.objects.abstract_objects.abstract_lines import DetailListOfLines, ListOfLines

from app.OLD_backend.rota.volunteer_rota_summary import (
    get_list_of_actual_and_targets_for_roles_at_event,
    RowInTableWithActualAndTargetsForRole,
    save_new_volunteer_target,
)


from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_form import intInput

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.events import Event


def get_volunteer_targets_table_and_save_button(
    interface:abstractInterface,
    event: Event,

) -> DetailListOfLines:
    table = get_volunteer_targets_table(event=event, interface=interface)
    elements_to_return = [table]

    if not is_ready_to_swap(interface):
        elements_to_return.append(save_targets_button)

    return DetailListOfLines(
        ListOfLines(elements_to_return).add_Lines(), name="Role numbers and targets"
    )


save_targets_button = Button("Save changes to targets")

def get_volunteer_targets_table(
    event: Event,    interface: abstractInterface,
) -> Table:
    top_row = get_top_row_of_volunteer_targets_table(event=event)
    other_rows = get_body_of_volunteer_targets_table(event=event, interface=interface)

    return Table(
        [top_row] + other_rows, has_column_headings=True, has_row_headings=True
    )


def get_top_row_of_volunteer_targets_table(event: Event) -> RowInTable:
    actual_for_days_at_event_as_str = [
        "%s (allocated)" % day.name for day in event.weekdays_in_event()
    ]
    return RowInTable(
        ["Role"]
        + actual_for_days_at_event_as_str
        + ["Target (Editable)", "Worst shortfall"]
    )


def get_body_of_volunteer_targets_table(
    event: Event, interface: abstractInterface
) -> List[RowInTable]:
    data_for_table = get_list_of_actual_and_targets_for_roles_at_event(
        cache =interface.cache, event=event
    )
    ready_to_swap = is_ready_to_swap(interface)

    other_rows = [
        get_row_for_volunteer_targets_at_event(
            row_of_data=row_of_data, event=event, ready_to_swap=ready_to_swap
        )
        for row_of_data in data_for_table
    ]

    return other_rows


def get_row_for_volunteer_targets_at_event(
    row_of_data: RowInTableWithActualAndTargetsForRole,
    event: Event,
    ready_to_swap: bool = False,
) -> RowInTable:
    role = row_of_data.role
    daily_counts = row_of_data.daily_counts
    daily_values = [daily_counts[day] for day in event.weekdays_in_event()]
    target_box = get_target_box_in_form(
        role=role, target=row_of_data.target, ready_to_swap=ready_to_swap
    )
    worst_shortfall = row_of_data.worst_shortfall

    return RowInTable([role] + daily_values + [target_box, worst_shortfall])


def get_target_box_in_form(role: str, target: int, ready_to_swap: bool = False):
    if ready_to_swap:
        return target
    else:
        return intInput(
            value=int(target), input_label="", input_name=get_input_name_for_target_box(role)
        )


def get_input_name_for_target_box(role: str):
    return "tgt_%s" % role


def save_volunteer_targets(interface: abstractInterface):
    event = get_event_from_state(interface)
    data_for_table = get_list_of_actual_and_targets_for_roles_at_event(
        cache=interface.cache, event=event
    )
    for row in data_for_table:
        try:
            save_volunteer_targets_for_specific_role(
                interface=interface, event=event, role=row.role
            )
        except:
            ## roles must have changed, no bother
            continue


def save_volunteer_targets_for_specific_role(
    interface: abstractInterface, event: Event, role: str
):
    new_target = get_target_from_form(interface=interface, role=role)
    save_new_volunteer_target(
        data_layer=interface.data, event=event, role=role, target=new_target
    )


def get_target_from_form(interface: abstractInterface, role: str):
    return interface.value_from_form(get_input_name_for_target_box(role))
