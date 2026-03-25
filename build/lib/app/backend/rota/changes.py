from app.backend.registration_data.volunteer_registration_data import (
    get_availability_volunteer_at_event,
)
from app.backend.volunteers.volunteers_with_roles_and_groups_at_event import (
    get_role_and_groups_for_event_and_volunteer,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.groups import Group

from app.objects.composed.volunteer_roles import RoleWithSkills
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    RoleAndGroupAndTeam,
)
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.volunteers import Volunteer
from app.backend.patrol_boats.changes import (
    delete_volunteer_from_patrol_boat_on_day_at_event,
)


def update_volunteer_notes_at_event(
    interface: abstractInterface, event: Event, volunteer: Volunteer, new_notes: str
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event.update_volunteer_notes_at_event,
        event_id=event.id,
        volunteer_id=volunteer.id,
        new_notes=new_notes,
    )


def update_role_and_group_at_event_for_volunteer_on_all_days_when_available(
    interface: abstractInterface,
    event: Event,
    volunteer: Volunteer,
    new_role_and_group: RoleAndGroupAndTeam,
    allow_replacement: bool,
):
    availability = get_availability_volunteer_at_event(
        object_store=interface.object_store, event=event, volunteer=volunteer
    )
    for day in availability.days_available():
        update_role_and_group_at_event_for_volunteer_on_day(
            interface=interface,
            event=event,
            volunteer=volunteer,
            day=day,
            new_role=new_role_and_group.role,
            new_group=new_role_and_group.group,
            allow_replacement=allow_replacement,
        )


def swap_roles_and_groups_for_volunteers_in_allocation(
    interface: abstractInterface,
    event: Event,
    original_day: Day,
    original_volunteer: Volunteer,
    day_to_swap_with: Day,
    volunteer_to_swap_with: Volunteer,
):
    original_volunteer_roles_and_groups = get_role_and_groups_for_event_and_volunteer(
        object_store=interface.object_store,
        event=event,
        volunteer=original_volunteer,
    ).role_and_group_on_day(original_day)

    swap_volunteer_roles_and_groups = get_role_and_groups_for_event_and_volunteer(
        object_store=interface.object_store,
        event=event,
        volunteer=volunteer_to_swap_with,
    ).role_and_group_on_day(day_to_swap_with)

    try:
        update_role_and_group_at_event_for_volunteer_on_day(
            interface=interface,
            event=event,
            volunteer=original_volunteer,
            day=original_day,
            new_role=swap_volunteer_roles_and_groups.role,
            new_group=swap_volunteer_roles_and_groups.group,
            allow_replacement=True,
        )
        update_role_and_group_at_event_for_volunteer_on_day(
            interface=interface,
            event=event,
            volunteer=volunteer_to_swap_with,
            day=day_to_swap_with,
            new_role=original_volunteer_roles_and_groups.role,
            new_group=original_volunteer_roles_and_groups.group,
            allow_replacement=True,
        )

    except Exception as e:
        print(
            "Can't swap roles/group for %s,%s on %s, %s, error %s, conflicting change made?"
            % (
                original_volunteer.name,
                volunteer_to_swap_with.name,
                original_day.name,
                day_to_swap_with.name,
                str(e),
            )
        )


def update_role_and_group_for_volunteer_given_specific_day_at_event(
    interface: abstractInterface,
    event: Event,
    volunteer: Volunteer,
    day: Day,
    existing_role: RoleWithSkills,
    new_role: RoleWithSkills,
    existing_group: Group,
    new_group: Group,
    allow_replacement: bool,
):
    role_matches = new_role == existing_role
    group_matches = new_group == existing_group
    ## Note use of if/elif not to make code easier to read
    if role_matches:
        if group_matches:
            ## no changes
            return
        elif not group_matches:
            ## change to group not role
            update_group_only_at_event_for_volunteer_on_day(
                interface=interface,
                event=event,
                volunteer=volunteer,
                day=day,
                new_group=new_group,
                allow_replacement=allow_replacement,
            )
    elif not role_matches:
        if group_matches:
            ### change to role only
            update_role_only_at_event_for_volunteer_on_day(
                interface=interface,
                event=event,
                volunteer=volunteer,
                day=day,
                new_role=new_role,
                allow_replacement=allow_replacement,
            )
        elif not group_matches:
            ## change to role and group

            update_role_and_group_at_event_for_volunteer_on_day(
                interface=interface,
                event=event,
                volunteer=volunteer,
                day=day,
                new_role=new_role,
                new_group=new_group,
                allow_replacement=True,
            )


def update_role_and_group_at_event_for_volunteer_on_day(
    interface: abstractInterface,
    event: Event,
    volunteer: Volunteer,
    day: Day,
    new_role: RoleWithSkills,
    new_group: Group,
    allow_replacement: bool,
):
    print("update %s on %s to %s, %s" % (volunteer, day, new_role, new_group))
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_in_roles_at_event.update_role_and_group_at_event_for_volunteer_on_day,
        event_id=event.id,
        volunteer_id=volunteer.id,
        day=day,
        new_role_id=new_role.id,
        new_group_id=new_group.id,
        allow_replacement=allow_replacement,
    )


def update_role_only_at_event_for_volunteer_on_day(
    interface: abstractInterface,
    event: Event,
    volunteer: Volunteer,
    day: Day,
    new_role: RoleWithSkills,
    allow_replacement: bool,
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_in_roles_at_event.update_role_only_at_event_for_volunteer_on_day,
        event_id=event.id,
        volunteer_id=volunteer.id,
        day=day,
        new_role_id=new_role.id,
        allow_replacement=allow_replacement,
    )


def update_group_only_at_event_for_volunteer_on_day(
    interface: abstractInterface,
    event: Event,
    volunteer: Volunteer,
    day: Day,
    new_group: Group,
    allow_replacement: bool,
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_in_roles_at_event.update_group_only_at_event_for_volunteer_on_day,
        event_id=event.id,
        volunteer_id=volunteer.id,
        day=day,
        new_group_id=new_group.id,
        allow_replacement=allow_replacement,
    )


def delete_role_and_possibly_powerboat_at_event_for_volunteer_on_day(
    interface: abstractInterface,
    volunteer: Volunteer,
    day: Day,
    event: Event,
    delete_power_boat: bool = True,
):
    delete_role_at_event_for_volunteer_on_day(
        interface=interface, event=event, volunteer=volunteer, day=day
    )
    if delete_power_boat:
        delete_volunteer_from_patrol_boat_on_day_at_event(
            interface=interface, event=event, volunteer=volunteer, day=day
        )


def delete_role_at_event_for_volunteer_on_day(
    interface: abstractInterface, volunteer: Volunteer, day: Day, event: Event
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_in_roles_at_event.delete_role_at_event_for_volunteer_on_day,
        event_id=event.id,
        day=day,
        volunteer_id=volunteer.id,
    )


def delete_role_at_event_for_volunteer_across_all_days(
    interface: abstractInterface, volunteer: Volunteer, event: Event
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_in_roles_at_event.delete_role_at_event_for_volunteer_across_all_days,
        event_id=event.id,
        volunteer_id=volunteer.id,
    )
