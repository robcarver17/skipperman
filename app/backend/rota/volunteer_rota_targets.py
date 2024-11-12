from dataclasses import dataclass
from typing import List, Dict

from app.data_access.store.object_definitions import object_definition_for_list_of_targets_for_role_at_event
from app.data_access.store.object_store import ObjectStore

from app.data_access.store.data_access import DataLayer
from app.backend.volunteers.volunteers_at_event import get_dict_of_all_event_data_for_volunteers
from app.objects.composed.volunteer_with_group_and_role_at_event import DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteer_role_targets import (
    DictOfTargetsForRolesAtEvent,
)
from app.objects.roles_and_teams import RolesWithSkillIds
from app.backend.volunteers.roles_and_teams import get_list_of_roles


@dataclass
class RowInTableWithActualAndTargetsForRole:
    role: str
    daily_counts: Dict[Day, int]
    target: int
    worst_shortfall: int


def get_list_of_actual_and_targets_for_roles_at_event(
    object_store: ObjectStore, event: Event
) -> List[RowInTableWithActualAndTargetsForRole]:
    all_event_data = get_dict_of_all_event_data_for_volunteers(object_store=object_store, event=event)
    volunteers_in_roles_at_event = all_event_data.dict_of_volunteers_at_event_with_days_and_role

    targets_at_event = get_volunteer_targets_at_event(object_store=object_store, event=event)

    all_volunteer_roles = get_list_of_roles(object_store=)

    all_rows = [
        get_row_in_table_with_actual_and_targets_for_roles_at_event(
            event=event,
            role=role,
            volunteers_in_roles_at_event=volunteers_in_roles_at_event,
            targets_at_event=targets_at_event,
        )
        for role in all_volunteer_roles
    ]

    return all_rows


def get_volunteer_targets_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfTargetsForRolesAtEvent:
    return object_store.get(object_definition_for_list_of_targets_for_role_at_event, event_id = event.id)




def get_row_in_table_with_actual_and_targets_for_roles_at_event(
    event: Event,
    role: RolesWithSkillIds,
    volunteers_in_roles_at_event: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    targets_at_event: DictOfTargetsForRolesAtEvent,
) -> RowInTableWithActualAndTargetsForRole:

    daily_counts = {}
    for day in event.weekdays_in_event():
        daily_counts[day] = volunteers_in_roles_at_event.count_of_volunteers_in_role_on_day(day=day, role=role)

    min_count = min(daily_counts.values())
    target = targets_at_event.get_target_for_role(role=role)
    worst_shortfall = int(target) - int(min_count)

    return RowInTableWithActualAndTargetsForRole(
        role=role.name,
        daily_counts=daily_counts,
        target=target,
        worst_shortfall=worst_shortfall,
    )


def save_new_volunteer_target(
    data_layer: DataLayer, event: Event, role: str, target: int
):
    #volunteer_data = VolunteerRotaData(data_layer)
    #volunteer_data.save_new_volunteer_target(event=event, role=role, target=target)


def update_volunteer_targets_at_event(
    object_store: ObjectStore, dict_of_targets:  DictOfTargetsForRolesAtEvent):
    object_store.update(new_object=dict_of_targets, event_id = dict_of_targets.event.id,
                        object_definition=object_definition_for_list_of_targets_for_role_at_event)
