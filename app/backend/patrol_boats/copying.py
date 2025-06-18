from app.backend.patrol_boats.volunteers_at_event_on_patrol_boats import \
    get_dict_of_patrol_boats_by_day_for_volunteer_at_event, update_dict_of_patrol_boats_by_day_for_volunteer_at_event
from app.data_access.store.object_store import ObjectStore
from app.objects.composed.volunteers_on_patrol_boats_with_skills_and_roles import (
    VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
)
from app.objects.events import Event


def volunteer_has_at_least_one_allocated_role_which_matches_others(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> bool:
    list_of_volunteers_in_roles = (
        volunteer_at_event_on_boat.role_and_group_by_day.list_of_roles_and_groups
    )
    if len(list_of_volunteers_in_roles) == 0:
        return False
    return list_of_volunteers_in_roles.count(list_of_volunteers_in_roles[0]) == len(
        list_of_volunteers_in_roles
    )


def is_possible_to_copy_boat_allocation(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
):
    on_same_boat_for_all_days = volunteer_is_on_same_boat_for_all_days(
        volunteer_at_event_on_boat
    )
    single_day = len(volunteer_at_event_on_boat.availability.days_available()) == 1
    copy_button_required = (not on_same_boat_for_all_days) and (not single_day)

    return copy_button_required


def is_possible_to_copy_boat_and_role_allocation(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
):
    boat_possible = is_possible_to_copy_boat_allocation(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )
    role_possible = is_possible_to_copy_roles(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )

    return boat_possible and role_possible


def is_possible_to_copy_fill_boat_and_role_allocation(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
):
    boat_possible = volunteer_has_at_least_one_allocated_boat_and_empty_spaces_to_fill(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )
    role_possible = volunteer_has_at_least_one_allocated_role_and_empty_spaces_to_fill(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )

    return boat_possible and role_possible


def volunteer_has_at_least_one_allocated_role_and_empty_spaces_to_fill(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> bool:
    list_of_volunteers_in_roles = (
        volunteer_at_event_on_boat.role_and_group_by_day.list_of_roles()
    )
    available_days = volunteer_at_event_on_boat.availability.days_available()
    empty_spaces = len(available_days) - len(list_of_volunteers_in_roles)
    at_least_one_allocated = len(list_of_volunteers_in_roles) > 0
    has_empty_spaces = empty_spaces > 0

    return at_least_one_allocated and has_empty_spaces


def is_required_to_copy_overwrite_boat_and_role_allocation(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
):
    boat_possible = not volunteer_has_at_least_one_allocated_boat_which_matches_others(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )
    role_possible = not volunteer_has_at_least_one_allocated_role_which_matches_others(
        volunteer_at_event_on_boat=volunteer_at_event_on_boat
    )

    return boat_possible and role_possible


def volunteer_is_on_same_boat_for_all_days(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> bool:
    list_of_boat_allocations = (
        volunteer_at_event_on_boat.patrol_boat_by_day.list_of_boats
    )
    number_of_days_in_event = volunteer_at_event_on_boat.event.duration
    number_of_allocated_days = len(list_of_boat_allocations)
    unique_boats = set(list_of_boat_allocations)

    allocated_for_all_days = number_of_allocated_days == number_of_days_in_event
    on_one_boat_entire_event = len(unique_boats) == 1

    return allocated_for_all_days and on_one_boat_entire_event


def volunteer_has_at_least_one_allocated_boat_and_empty_spaces_to_fill(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> bool:
    number_of_days_available_at_event = len(
        volunteer_at_event_on_boat.availability.days_available()
    )
    number_of_allocated_days = (
        volunteer_at_event_on_boat.patrol_boat_by_day.number_of_days_assigned_to_any_boat()
    )
    empty_spaces = number_of_days_available_at_event - number_of_allocated_days

    at_least_one_boat = number_of_allocated_days > 0
    has_empty_spaces = empty_spaces > 0

    return at_least_one_boat and has_empty_spaces


def volunteer_has_at_least_one_allocated_boat_which_matches_others(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> bool:
    list_of_boat_allocations = (
        volunteer_at_event_on_boat.patrol_boat_by_day.list_of_boats
    )

    if len(list_of_boat_allocations) == 0:
        return False

    return list_of_boat_allocations.count(list_of_boat_allocations[0]) == len(
        list_of_boat_allocations
    )


def is_possible_to_copy_roles(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> bool:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match

    role_today = volunteer_at_event_on_boat.role_and_group.role
    if role_today.is_no_role_set():
        return False

    all_roles = volunteer_at_event_on_boat.role_and_group_by_day.list_of_roles()

    no_roles_to_copy = len(all_roles) == 0
    all_roles_match = len(set(all_roles)) <= 1
    single_day = len(volunteer_at_event_on_boat.availability.days_available()) == 1

    if all_roles_match or no_roles_to_copy or single_day:
        return False
    else:
        return True


def copy_patrol_boat_labels_across_event(object_store: ObjectStore, event: Event, overwrite: bool = False):
    dict_of_voluteers_at_event_with_patrol_boats = (
        get_dict_of_patrol_boats_by_day_for_volunteer_at_event(
            object_store=object_store, event=event
        )
    )

    dict_of_voluteers_at_event_with_patrol_boats.copy_patrol_boat_labels_across_event(overwrite)
    update_dict_of_patrol_boats_by_day_for_volunteer_at_event(object_store=object_store,
                                                              dict_of_volunteers_at_event_with_patrol_boats=dict_of_voluteers_at_event_with_patrol_boats)

