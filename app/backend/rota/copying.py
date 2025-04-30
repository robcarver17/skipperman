from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import (
    get_dict_of_volunteers_with_roles_and_groups_at_event,
)
from app.objects.volunteers import Volunteer

from app.data_access.store.object_store import ObjectStore

from app.objects.day_selectors import Day
from app.objects.events import Event


from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_all_event_data_for_volunteers,
    update_dict_of_all_event_data_for_volunteers,
)


def copy_earliest_valid_role_for_volunteer(
    object_store: ObjectStore, event: Event, volunteer: Volunteer, allow_overwrite: bool
):
    valid_day = get_day_with_earliest_valid_role_and_group_for_volunteer_or_none(
        object_store=object_store, event=event, volunteer=volunteer
    )

    if valid_day is None:
        return

    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        object_store=object_store,
        event=event,
        volunteer=volunteer,
        day=valid_day,
        allow_replacement=allow_overwrite,
    )


def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
    object_store: ObjectStore,
    event: Event,
    volunteer: Volunteer,
    day: Day,
    allow_replacement: bool = True,
):
    all_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    try:
        all_event_data.copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
            volunteer=volunteer,
            day=day,
            allow_replacement=allow_replacement,
        )
    except Exception as e:
        print(
            "Can't copy across role data for %s on %s, error %s, conflicting change made?"
            % (volunteer.name, day.name, str(e))
        )

    update_dict_of_all_event_data_for_volunteers(
        object_store=object_store, dict_of_all_event_data=all_event_data
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
