from typing import List

from app.backend.groups.group_notes_at_event import (
    update_group_notes_at_event_for_group,
)
from app.backend.rota.volunteer_rota_summary import get_sorted_list_of_groups_at_event
from app.backend.rota.volunteer_summary_of_instructors import (
    get_summary_table_of_instructors_and_groups_for_event,
    get_group_notes_field_value,
)
from app.frontend.forms.swaps import is_ready_to_swap
from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_buttons import Button

from app.objects.abstract_objects.abstract_lines import DetailListOfLines, ListOfLines

from app.backend.rota.volunteer_rota_targets import (
    get_list_of_actual_and_targets_for_roles_at_event,
    RowInTableWithActualAndTargetsForRole,
    save_new_volunteer_target,
)


from app.objects.abstract_objects.abstract_tables import Table, RowInTable
from app.objects.abstract_objects.abstract_form import intInput

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.events import Event
from app.objects.groups import Group
from app.objects.utilities.exceptions import MISSING_FROM_FORM


def get_volunteer_targets_table_and_save_button(
    interface: abstractInterface,
    event: Event,
) -> DetailListOfLines:
    table = get_volunteer_targets_table(event=event, interface=interface)
    elements_to_return = [table, save_targets_button]

    return DetailListOfLines(
        ListOfLines(elements_to_return).add_Lines(), name="Role numbers and targets"
    )


save_targets_button = Button("Save changes to targets")


def get_volunteer_targets_table(
    event: Event,
    interface: abstractInterface,
) -> Table:
    top_row = get_top_row_of_volunteer_targets_table(event=event)
    other_rows = get_body_of_volunteer_targets_table(event=event, interface=interface)

    return Table(
        [top_row] + other_rows, has_column_headings=True, has_row_headings=True
    )


def get_top_row_of_volunteer_targets_table(event: Event) -> RowInTable:
    actual_for_days_at_event_as_str = [
        "%s (allocated)" % day.name for day in event.days_in_event()
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
        object_store=interface.object_store, event=event
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
    daily_values = [daily_counts[day] for day in event.days_in_event()]
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
            value=int(target),
            input_label="",
            input_name=get_input_name_for_target_box(role),
        )


def get_input_name_for_target_box(role: str):
    return "tgt_%s" % role


def save_volunteer_targets(interface: abstractInterface):
    event = get_event_from_state(interface)
    data_for_table = get_list_of_actual_and_targets_for_roles_at_event(
        object_store=interface.object_store, event=event
    )
    for row in data_for_table:
        save_volunteer_targets_for_specific_role(
            interface=interface, event=event, role_name=row.role
        )


def save_volunteer_targets_for_specific_role(
    interface: abstractInterface, event: Event, role_name: str
):
    new_target = get_target_from_form(
        interface=interface, role_name=role_name, default=MISSING_FROM_FORM
    )
    if new_target is MISSING_FROM_FORM:
        return

    save_new_volunteer_target(
        object_store=interface.object_store,
        event=event,
        role_name=role_name,
        target=new_target,
    )


def get_target_from_form(
    interface: abstractInterface, role_name: str, default=MISSING_FROM_FORM
):
    return interface.value_from_form(
        get_input_name_for_target_box(role_name), default=default
    )


def get_summary_instructor_group_table(interface: abstractInterface, event: Event):
    summary_of_instructor_groups = (
        get_summary_table_of_instructors_and_groups_for_event(
            object_store=interface.object_store, event=event
        )
    )
    if len(summary_of_instructor_groups) == 0:
        return ""

    summary_of_instructor_groups = DetailListOfLines(
        ListOfLines([summary_of_instructor_groups, save_group_notes_button]),
        name="Summary of instructors and groups",
    )

    return summary_of_instructor_groups


save_group_notes_button = Button("Save Group Notes")


def save_group_notes_from_form(interface: abstractInterface):
    event = get_event_from_state(interface)
    list_of_groups = get_sorted_list_of_groups_at_event(
        object_store=interface.object_store, event=event
    )
    for group in list_of_groups:
        save_group_notes_for_group(interface=interface, event=event, group=group)


def save_group_notes_for_group(
    interface: abstractInterface, event: Event, group: Group
):
    notes = interface.value_from_form(
        get_group_notes_field_value(group), default=MISSING_FROM_FORM
    )
    if notes is MISSING_FROM_FORM:
        return
    update_group_notes_at_event_for_group(
        object_store=interface.object_store, event=event, group=group, notes=notes
    )
