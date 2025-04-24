from dataclasses import dataclass


from app.data_access.store.object_store import ObjectStore

from app.backend.rota.changes import swap_roles_and_groups_for_volunteers_in_allocation
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.patrol_boats import PatrolBoat

from app.objects.volunteers import Volunteer

from app.objects.composed.volunteers_on_patrol_boats_with_skills_and_roles import (
    VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
)
from app.objects.day_selectors import Day
from app.objects.events import Event


@dataclass
class SwapData:
    event: Event
    original_day: Day
    day_to_swap_with: Day
    swap_boats: bool
    swap_roles: bool
    original_volunteer: Volunteer
    volunteer_to_swap_with: Volunteer = arg_not_passed
    swapping_into_empty_boat: bool = False
    empty_boat_to_swap_into: PatrolBoat = arg_not_passed


def do_swapping_for_volunteers_boats_and_possibly_roles_in_boat_allocation(
        object_store: ObjectStore, swap_data: SwapData
):
    if swap_data.swapping_into_empty_boat:
        move_volunteer_into_empty_boat_using_swapdata(
            object_store=object_store, swap_data=swap_data
        )

    if swap_data.swap_roles:
        swap_roles_for_volunteers_in_allocation_using_swapdata(
            object_store=object_store, swap_data=swap_data
        )
    if swap_data.swap_boats:
        swap_boats_for_volunteers_in_allocation_using_swapdata(
            object_store=object_store, swap_data=swap_data
        )


def is_possible_to_swap_roles_on_one_day(
    volunteer_at_event_on_boat: VolunteerAtEventWithSkillsAndRolesAndPatrolBoatsOnSpecificday,
) -> bool:
    ## Only possible if: none of the roles require a group, and all the roles don't currently match
    role = volunteer_at_event_on_boat.role_and_group.role
    if role.is_no_role_set():
        return False

    return True


def swap_boats_for_volunteers_in_allocation_using_swapdata(
    object_store:ObjectStore, swap_data: SwapData
):
    swap_patrol_boats_for_volunteers_in_allocation(
        object_store=object_store,
        event=swap_data.event,
        volunteer_to_swap_with=swap_data.volunteer_to_swap_with,
        original_volunteer=swap_data.original_volunteer,
        day_to_swap_with=swap_data.day_to_swap_with,
        original_day=swap_data.original_day,
    )

from app.backend.volunteers.volunteers_at_event import get_dict_of_all_event_data_for_volunteers, update_dict_of_all_event_data_for_volunteers

def swap_patrol_boats_for_volunteers_in_allocation(
    object_store: ObjectStore,
    event: Event,
    original_day: Day,
    original_volunteer: Volunteer,
    day_to_swap_with: Day,
    volunteer_to_swap_with: Volunteer,
):
    all_event_data = get_dict_of_all_event_data_for_volunteers(object_store, event)
    all_event_data.swap_patrol_boats_for_volunteers_in_allocation(
        original_volunteer=original_volunteer,
        volunteer_to_swap_with=volunteer_to_swap_with,
        day_to_swap_with=day_to_swap_with,
        original_day=original_day,
    )

    update_dict_of_all_event_data_for_volunteers(object_store, dict_of_all_event_data=all_event_data)

def swap_roles_for_volunteers_in_allocation_using_swapdata(
    object_store: ObjectStore, swap_data: SwapData
):
    swap_roles_and_groups_for_volunteers_in_allocation(
        object_store=object_store,
        event=swap_data.event,
        volunteer_to_swap_with=swap_data.volunteer_to_swap_with,
        original_volunteer=swap_data.original_volunteer,
        day_to_swap_with=swap_data.day_to_swap_with,
        original_day=swap_data.original_day,
    )

def move_volunteer_into_empty_boat_using_swapdata(
    object_store: ObjectStore, swap_data: SwapData
):
    all_event_data = get_dict_of_all_event_data_for_volunteers(object_store, swap_data.event)
    all_event_data.move_volunteer_into_empty_boat(
        original_volunteer=swap_data.original_volunteer,
        day_to_swap_with=swap_data.day_to_swap_with,
        new_patrol_boat = swap_data.empty_boat_to_swap_into
    )

    update_dict_of_all_event_data_for_volunteers(object_store, dict_of_all_event_data=all_event_data)
