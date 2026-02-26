from copy import copy
from dataclasses import dataclass


from app.backend.rota.changes import swap_roles_and_groups_for_volunteers_in_allocation
from app.objects.abstract_objects.abstract_interface import abstractInterface
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
    interface: abstractInterface, swap_data: SwapData
):
    if swap_data.swapping_into_empty_boat:
        move_volunteer_into_empty_boat_using_swapdata(
            interface=interface, swap_data=swap_data
        )

    if swap_data.swap_roles:
        swap_roles_for_volunteers_in_allocation_using_swapdata(
            interface=interface, swap_data=swap_data
        )
    if swap_data.swap_boats:
        swap_boats_for_volunteers_in_allocation_using_swapdata(
            interface=interface, swap_data=swap_data
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
    interface: abstractInterface, swap_data: SwapData
):
    swap_patrol_boats_for_volunteers_in_allocation(
        interface=interface,
        event=swap_data.event,
        volunteer_to_swap_with=swap_data.volunteer_to_swap_with,
        original_volunteer=swap_data.original_volunteer,
        day_to_swap_with=swap_data.day_to_swap_with,
        original_day=swap_data.original_day,
    )


def swap_patrol_boats_for_volunteers_in_allocation(
    interface: abstractInterface,
    event: Event,
    original_day: Day,
    original_volunteer: Volunteer,
    day_to_swap_with: Day,
    volunteer_to_swap_with: Volunteer,
):
    original_volunteer_boat = copy(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_patrol_boats.existing_boat_id_for_volunteer_on_day(
            event_id=event.id, volunteer_id=original_volunteer.id, day=original_day
        )
    )
    volunteer_to_swap_with_boat = copy(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_patrol_boats.existing_boat_id_for_volunteer_on_day(
            event_id=event.id,
            volunteer_id=volunteer_to_swap_with.id,
            day=day_to_swap_with,
        )
    )
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_patrol_boats.delete_volunteer_from_patrol_boat_on_day_at_event,
        event_id=event.id,
        volunteer_id=original_volunteer.id,
        day=original_day,
    )
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_patrol_boats.delete_volunteer_from_patrol_boat_on_day_at_event,
        event_id=event.id,
        volunteer_id=volunteer_to_swap_with.id,
        day=day_to_swap_with,
    )
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_patrol_boats.add_new_boat_day_volunteer_allocation,
        event_id=event.id,
        volunteer_id=original_volunteer.id,
        day=day_to_swap_with,
        patrol_boat_id=volunteer_to_swap_with_boat,
    )
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_patrol_boats.add_new_boat_day_volunteer_allocation,
        event_id=event.id,
        volunteer_id=volunteer_to_swap_with.id,
        day=original_day,
        patrol_boat_id=original_volunteer_boat,
    )


def swap_roles_for_volunteers_in_allocation_using_swapdata(
    interface: abstractInterface, swap_data: SwapData
):
    swap_roles_and_groups_for_volunteers_in_allocation(
        interface=interface,
        event=swap_data.event,
        volunteer_to_swap_with=swap_data.volunteer_to_swap_with,
        original_volunteer=swap_data.original_volunteer,
        day_to_swap_with=swap_data.day_to_swap_with,
        original_day=swap_data.original_day,
    )


def move_volunteer_into_empty_boat_using_swapdata(
    interface: abstractInterface, swap_data: SwapData
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_patrol_boats.delete_volunteer_from_patrol_boat_on_day_at_event,
        event_id=swap_data.event.id,
        volunteer_id=swap_data.original_volunteer.id,
        day=swap_data.original_day,
    )
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event_with_patrol_boats.add_new_boat_day_volunteer_allocation,
        event_id=swap_data.event.id,
        volunteer_id=swap_data.original_volunteer.id,
        day=swap_data.day_to_swap_with,
        patrol_boat_id=swap_data.empty_boat_to_swap_into.id,
    )
