
from app.objects.groups import Group

from app.backend.volunteers.volunteers_at_event import get_dict_of_all_event_data_for_volunteers, \
    update_dict_of_all_event_data_for_volunteers
from app.backend.registration_data.volunteer_registration_data import \
    get_dict_of_registration_data_for_volunteers_at_event, update_dict_of_registration_data_for_volunteers_at_event
from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import \
    get_dict_of_volunteers_with_roles_and_groups_at_event, update_dict_of_volunteers_with_roles_and_groups_at_event
from app.data_access.store.object_store import ObjectStore
from app.objects.composed.volunteer_roles import RoleWithSkills
from app.objects.composed.volunteer_with_group_and_role_at_event import RoleAndGroupAndTeam
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteers import Volunteer


def delete_role_at_event_for_volunteer_on_day(
    object_store: ObjectStore, volunteer: Volunteer, day: Day, event: Event
):
    dict_of_all_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )

    dict_of_all_event_data.delete_role_at_event_for_volunteer_on_day(volunteer=volunteer, day=day)
    update_dict_of_all_event_data_for_volunteers(
        object_store=object_store,
        dict_of_all_event_data=dict_of_all_event_data
    )




def update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
    object_store: ObjectStore,
        event: Event,
        volunteer: Volunteer,
        new_role_and_group: RoleAndGroupAndTeam
):

    dict_of_volunteers_at_event = get_dict_of_all_event_data_for_volunteers(object_store=object_store,
                                                                                                              event=event)
    try:
        dict_of_volunteers_at_event.update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
            volunteer=volunteer,
            new_role_and_group=new_role_and_group
        )
    except Exception as e:
        print(
            "Can't copy across role data for %s with new role %s, error %s, conflicting change made?"
            % (volunteer.name, str(new_role_and_group), str(e))
        )

    update_dict_of_all_event_data_for_volunteers(
        object_store=object_store,
        dict_of_all_event_data=dict_of_volunteers_at_event
    )


def swap_roles_and_groups_for_volunteers_in_allocation(
    object_store: ObjectStore,
    event: Event,
    original_day: Day,
    original_volunteer: Volunteer,
    day_to_swap_with: Day,
    volunteer_to_swap_with: Volunteer,
):

    dict_of_volunteers_with_roles_and_groups_at_event = get_dict_of_volunteers_with_roles_and_groups_at_event(object_store=object_store,
                                                                                                              event=event)
    try:
        dict_of_volunteers_with_roles_and_groups_at_event.swap_roles_and_groups_for_volunteers_in_allocation(
            original_volunteer=original_volunteer,
            volunteer_to_swap_with=volunteer_to_swap_with,
            original_day=original_day,
            day_to_swap_with=day_to_swap_with
        )
    except Exception as e:
        print(
            "Can't swap roles/group for %s,%s on %s, %s, error %s, conflicting change made?"
            % (original_volunteer.name, volunteer_to_swap_with.name, original_day.name, day_to_swap_with.name, str(e))
        )

    update_dict_of_volunteers_with_roles_and_groups_at_event(object_store=object_store,
                                                             dict_of_volunteers_with_roles_and_groups_at_event=dict_of_volunteers_with_roles_and_groups_at_event)


def update_volunteer_notes_at_event(
    object_store: ObjectStore, event: Event, volunteer: Volunteer, new_notes: str
):
    registration_data = get_dict_of_registration_data_for_volunteers_at_event(event=event, object_store=object_store)
    data_for_volunteer = registration_data.get_data_for_volunteer(volunteer)
    data_for_volunteer.notes = new_notes
    update_dict_of_registration_data_for_volunteers_at_event(object_store=object_store,
                                                             dict_of_registration_data=registration_data)


def update_role_at_event_for_volunteer_on_day(
    object_store: ObjectStore,
    event: Event,
    volunteer: Volunteer,
    day: Day,
    new_role: RoleWithSkills
):
    if new_role.is_no_role_set():
        delete_role_at_event_for_volunteer_on_day(
            object_store=object_store,
            event=event,
            volunteer=volunteer,
            day=day
        )
    else:
        update_role_at_event_for_volunteer_on_day_if_switching_roles(
            object_store=object_store,
            event=event,
            volunteer=volunteer,
            day=day,
            new_role=new_role,
        )


def update_role_at_event_for_volunteer_on_day_if_switching_roles(
    object_store: ObjectStore,
    event: Event,
    volunteer: Volunteer,
    day: Day,
    new_role: RoleWithSkills
):
    dict_of_volunteers_with_roles_and_groups_at_event = get_dict_of_volunteers_with_roles_and_groups_at_event(object_store=object_store,
                                                                                                              event=event)
    try:
        dict_of_volunteers_with_roles_and_groups_at_event.update_role_at_event_for_volunteer_on_day_if_switching_roles(
            volunteer=volunteer,
            day=day,
            new_role=new_role
        )
    except Exception as e:
        print(
            "Can't modify role for volunteer to %s to %s, error %s, conflicting change made?"
            % (volunteer.name, new_role.name, str(e))
        )

    update_dict_of_volunteers_with_roles_and_groups_at_event(object_store=object_store,
                                                             dict_of_volunteers_with_roles_and_groups_at_event=dict_of_volunteers_with_roles_and_groups_at_event)


def update_group_at_event_for_volunteer_on_day(
    object_store: ObjectStore,
    event: Event,
    volunteer: Volunteer,
    day: Day,
    new_group: Group
):
    dict_of_volunteers_with_roles_and_groups_at_event = get_dict_of_volunteers_with_roles_and_groups_at_event(object_store=object_store,
                                                                                                              event=event)
    try:
        dict_of_volunteers_with_roles_and_groups_at_event.update_group_at_event_for_volunteer_on_day(
            volunteer=volunteer,
            day=day,
            new_group=new_group
        )
    except Exception as e:
        print(
            "Can't modify group for volunteer to %s to %s, error %s, conflicting change made?"
            % (volunteer.name, new_group.name, str(e))
        )

    update_dict_of_volunteers_with_roles_and_groups_at_event(object_store=object_store,
                                                             dict_of_volunteers_with_roles_and_groups_at_event=dict_of_volunteers_with_roles_and_groups_at_event)

