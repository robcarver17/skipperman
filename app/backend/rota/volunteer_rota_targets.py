from dataclasses import dataclass
from typing import List, Dict

from app.data_access.store.object_definitions import (
    object_definition_for_list_of_targets_for_role_at_event,
)
from app.data_access.store.object_store import ObjectStore

from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_all_event_data_for_volunteers,
)
from app.objects.composed.volunteer_roles import RoleWithSkills
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    DEPRECATED_DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
)
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.composed.dict_of_volunteer_role_targets import (
    DictOfTargetsForRolesAtEvent,
)
from app.backend.volunteers.roles_and_teams import (
    get_list_of_roles_with_skills,
)


@dataclass
class RowInTableWithActualAndTargetsForRole:
    role: RoleWithSkills
    daily_counts: Dict[Day, int]
    target: int
    worst_shortfall: int



def get_list_of_actual_and_targets_for_roles_at_event(
    object_store: ObjectStore, event: Event
) -> List[RowInTableWithActualAndTargetsForRole]:
    all_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    volunteers_in_roles_at_event = (
        all_event_data.dict_of_volunteers_at_event_with_days_and_roles
    )

    targets_at_event = get_volunteer_targets_at_event(
        object_store=object_store, event=event
    )

    all_volunteer_roles = get_list_of_roles_with_skills(object_store=object_store)
    visible_roles = [role for role in all_volunteer_roles if not role.hidden]

    all_rows = [
        get_row_in_table_with_actual_and_targets_for_roles_at_event(
            event=event,
            role=role,
            volunteers_in_roles_at_event=volunteers_in_roles_at_event,
            targets_at_event=targets_at_event,
        )
        for role in visible_roles
    ]

    return all_rows


def get_volunteer_targets_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfTargetsForRolesAtEvent:
    return object_store.DEPRECATE_get(
        object_definition_for_list_of_targets_for_role_at_event, event_id=event.id
    )


def get_row_in_table_with_actual_and_targets_for_roles_at_event(
    event: Event,
    role: RoleWithSkills,
    volunteers_in_roles_at_event: DEPRECATED_DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    targets_at_event: DictOfTargetsForRolesAtEvent,
) -> RowInTableWithActualAndTargetsForRole:
    daily_counts = {}
    for day in event.days_in_event():
        daily_counts[
            day
        ] = volunteers_in_roles_at_event.count_of_volunteers_in_role_on_day(
            day=day, role=role
        )

    min_count = min(daily_counts.values())
    target = targets_at_event.get_target_for_role(role=role)
    worst_shortfall = int(target) - int(min_count)

    return RowInTableWithActualAndTargetsForRole(
        role=role,
        daily_counts=daily_counts,
        target=target,
        worst_shortfall=worst_shortfall,
    )


def save_new_volunteer_target(
    object_store: ObjectStore, event: Event, role: RoleWithSkills, target: int
):
    targets_at_event = get_volunteer_targets_at_event(
        object_store=object_store, event=event
    )
    targets_at_event.update_new_volunteer_target(role=role, target=target)
    update_volunteer_targets_at_event(
        object_store=object_store, dict_of_targets=targets_at_event
    )


def update_volunteer_targets_at_event(
    object_store: ObjectStore, dict_of_targets: DictOfTargetsForRolesAtEvent
):
    object_store.DEPRECATE_update(
        new_object=dict_of_targets,
        event_id=dict_of_targets.event.id,
        object_definition=object_definition_for_list_of_targets_for_role_at_event,
    )
