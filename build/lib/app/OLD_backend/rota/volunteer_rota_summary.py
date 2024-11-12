from dataclasses import dataclass
from typing import List, Dict

from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache
from app.data_access.store.data_access import DataLayer

from app.OLD_backend.data.volunteer_rota import VolunteerRotaData
from app.OLD_backend.rota.volunteer_rota import (
    get_volunteers_in_role_at_event_with_active_allocations,
)
from app.data_access.configuration.skills_and_roles import all_volunteer_role_names
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteer_role_targets import (
    ListOfTargetForRoleWithIdAtEvent,
)
from app.objects.volunteer_roles_and_groups_with_id import (
    ListOfVolunteersWithIdInRoleAtEvent,
)


@dataclass
class RowInTableWithActualAndTargetsForRole:
    role: str
    daily_counts: Dict[Day, int]
    target: int
    worst_shortfall: int


def get_list_of_actual_and_targets_for_roles_at_event(
    cache: AdHocCache, event: Event
) -> List[RowInTableWithActualAndTargetsForRole]:
    volunteers_in_roles_at_event = cache.get_from_cache(
        get_volunteers_in_role_at_event_with_active_allocations,
        event=event,
    )

    targets_at_event = cache.get_from_cache(get_volunteer_targets_at_event, event=event)

    all_rows = [
        get_row_in_table_with_actual_and_targets_for_roles_at_event(
            event=event,
            role=role,
            volunteers_in_roles_at_event=volunteers_in_roles_at_event,
            targets_at_event=targets_at_event,
        )
        for role in all_volunteer_role_names
    ]

    return all_rows


def get_volunteer_targets_at_event(
    data_layer: DataLayer, event: Event
) -> ListOfTargetForRoleWithIdAtEvent:
    volunteer_data = VolunteerRotaData(data_layer)
    return volunteer_data.get_list_of_targets_for_role_at_event(event)


def get_row_in_table_with_actual_and_targets_for_roles_at_event(
    event: Event,
    role: str,
    volunteers_in_roles_at_event: ListOfVolunteersWithIdInRoleAtEvent,
    targets_at_event: ListOfTargetForRoleWithIdAtEvent,
) -> RowInTableWithActualAndTargetsForRole:
    daily_counts = {}
    for day in event.weekdays_in_event():
        volunteer_count = [
            1
            for volunteer in volunteers_in_roles_at_event
            if volunteer.role == role and volunteer.day == day
        ]
        total_count = sum(volunteer_count)
        daily_counts[day] = total_count

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
    data_layer: DataLayer, event: Event, role: str, target: int
):
    volunteer_data = VolunteerRotaData(data_layer)
    volunteer_data.save_new_volunteer_target(event=event, role=role, target=target)


####


## TEAMS


# SHARED
