from app.objects.volunteers import Volunteer

from app.data_access.store.object_store import ObjectStore

from app.objects.day_selectors import Day
from app.objects.events import Event

from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import \
    update_dict_of_volunteers_with_roles_and_groups_at_event

from app.backend.registration_data.volunteer_registration_data import \
    get_dict_of_registration_data_for_volunteers_at_event


def copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
    object_store: ObjectStore,
        event: Event,
    volunteer: Volunteer,
    day: Day,
    allow_replacement: bool = True,
):
    dict_of_volunteers_with_roles_and_groups_at_event = get_dict_of_volunteers_with_roles_and_groups_at_event(object_store=object_store,
                                                                                                              event=event)
    registration_data_for_volunteers_at_event  = get_dict_of_registration_data_for_volunteers_at_event(
        object_store=object_store,
        event=event
    )
    availability_for_volunteer = registration_data_for_volunteers_at_event.get_data_for_volunteer(volunteer).availablity
    try:
        dict_of_volunteers_with_roles_and_groups_at_event.copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
            volunteer=volunteer,
            day=day,
            available_days=availability_for_volunteer,
            allow_replacement=allow_replacement
        )
    except Exception as e:
        print(
            "Can't copy across role data for %s on %s, error %s, conflicting change made?"
            % (volunteer.name, day.name, str(e))
        )

    update_dict_of_volunteers_with_roles_and_groups_at_event(object_store=object_store,
                                                             dict_of_volunteers_with_roles_and_groups_at_event=dict_of_volunteers_with_roles_and_groups_at_event)



def copy_earliest_valid_role_and_overwrite_for_volunteer(
        object_store: ObjectStore,
        event: Event,
        volunteer: Volunteer,
):
    valid_day = get_day_with_earliest_valid_role_and_group_for_volunteer_or_none(
        object_store=object_store, event=event, volunteer=volunteer
    )

    print(
        "Valid day for volunteer %s is %s" % (volunteer.name, str(valid_day))
    )
    if valid_day is None:
        return

    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        object_store=object_store,
        event=event,
        volunteer=volunteer,
        day=valid_day,
        allow_replacement=True,
    )


def copy_earliest_valid_role_to_all_empty_for_volunteer(
    object_store: ObjectStore,
    event: Event,
    volunteer: Volunteer,
):
    valid_day = get_day_with_earliest_valid_role_and_group_for_volunteer_or_none(
        object_store=object_store, event=event, volunteer=volunteer
    )
    name = volunteer.name
    print("Valid day for volunteer %s is %s" % (name, str(valid_day)))
    if valid_day is None:
        return

    copy_across_duties_for_volunteer_at_event_from_one_day_to_all_other_days(
        object_store=object_store,
        event=event,
        volunteer=volunteer,
        day=valid_day,
        allow_replacement=False,
    )


from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import get_dict_of_volunteers_with_roles_and_groups_at_event

def get_day_with_earliest_valid_role_and_group_for_volunteer_or_none(
    object_store: ObjectStore,
    event: Event,
    volunteer: Volunteer,
) -> Day:

    volunteers_at_event = get_dict_of_volunteers_with_roles_and_groups_at_event(object_store=object_store, event=event)
    volunteer_data = volunteers_at_event.days_and_roles_for_volunteer(volunteer)

    for day in event.weekdays_in_event():
        role_and_group = (
            volunteer_data.role_and_group_on_day(day)
            )
        if role_and_group.is_unallocated:
            continue
        else:
            return day

    return None



