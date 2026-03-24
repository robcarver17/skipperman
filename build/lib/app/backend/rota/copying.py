from app.backend.rota.changes import update_role_and_group_at_event_for_volunteer_on_day
from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import (
    get_dict_of_volunteers_with_roles_and_groups_at_event,
    get_role_and_group_on_day_for_event_and_volunteer,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.volunteers import Volunteer

from app.data_access.store.object_store import ObjectStore

from app.objects.day_selectors import Day
from app.objects.events import Event


def copy_earliest_valid_role_for_volunteer(
    interface: abstractInterface,
    event: Event,
    volunteer: Volunteer,
    allow_overwrite: bool,
):
    day_to_copy_from = get_day_with_earliest_valid_role_and_group_for_volunteer_or_none(
        object_store=interface.object_store, event=event, volunteer=volunteer
    )

    if day_to_copy_from is None:
        return

    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        interface=interface,
        event=event,
        volunteer=volunteer,
        day_to_copy_from=day_to_copy_from,
        allow_replacement=allow_overwrite,
    )


def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
    interface: abstractInterface,
    event: Event,
    volunteer: Volunteer,
    day_to_copy_from: Day,
    allow_replacement: bool = True,
):
    role_and_group = get_role_and_group_on_day_for_event_and_volunteer(
        object_store=interface.object_store, event=event, volunteer=volunteer, day=day_to_copy_from
    )

    for day_to_copy_to in event.days_in_event():
        if day_to_copy_from == day_to_copy_to:
            continue

        update_role_and_group_at_event_for_volunteer_on_day(
            interface=interface,
            event=event,
            volunteer=volunteer,
            day=day_to_copy_to,
            new_role=role_and_group.role,
            new_group=role_and_group.group,
            allow_replacement=allow_replacement,
        )


def get_day_with_earliest_valid_role_and_group_for_volunteer_or_none(
    object_store: ObjectStore,
    event: Event,
    volunteer: Volunteer,
) -> Day:
    volunteers_at_event = get_dict_of_volunteers_with_roles_and_groups_at_event(
        object_store=object_store, event=event
    )
    volunteer_data = volunteers_at_event.days_and_roles_for_volunteer(volunteer)

    for day in event.days_in_event():
        role_and_group = volunteer_data.role_and_group_on_day(day)
        if role_and_group.is_unallocated:
            continue
        else:
            return day

    return None
