from dataclasses import dataclass

from app.backend.patrol_boats.volunteers_at_event_on_patrol_boats import (
    get_dict_of_patrol_boats_by_day_for_volunteer_at_event,
    update_dict_of_patrol_boats_by_day_for_volunteer_at_event,
)

from app.data_access.store.object_store import ObjectStore

from app.backend.rota.changes import swap_roles_and_groups_for_volunteers_in_allocation

from app.objects.volunteers import Volunteer

from app.objects.abstract_objects.abstract_interface import abstractInterface
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
    volunteer_to_swap_with: Volunteer
    original_volunteer: Volunteer


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
    try:
        swap_patrol_boats_for_volunteers_in_allocation(
            object_store=interface.object_store,
            event=swap_data.event,
            volunteer_to_swap_with=swap_data.volunteer_to_swap_with,
            original_volunteer=swap_data.original_volunteer,
            day_to_swap_with=swap_data.day_to_swap_with,
            original_day=swap_data.original_day,
        )
    except Exception as e:
        interface.log_error(
            "Swap boats of %s and %s failed on day %s, error %s"
            % (
                swap_data.volunteer_to_swap_with.name,
                swap_data.original_volunteer.name,
                swap_data.day_to_swap_with.name,
                str(e),
            )
        )


def swap_patrol_boats_for_volunteers_in_allocation(
    object_store: ObjectStore,
    event: Event,
    original_day: Day,
    original_volunteer: Volunteer,
    day_to_swap_with: Day,
    volunteer_to_swap_with: Volunteer,
):
    patrol_boat_data = get_dict_of_patrol_boats_by_day_for_volunteer_at_event(
        object_store=object_store, event=event
    )

    patrol_boat_data.swap_patrol_boats_for_volunteers_in_allocation(
        original_volunteer=original_volunteer,
        volunteer_to_swap_with=volunteer_to_swap_with,
        day_to_swap_with=day_to_swap_with,
        original_day=original_day,
    )

    update_dict_of_patrol_boats_by_day_for_volunteer_at_event(
        dict_of_volunteers_at_event_with_patrol_boats=patrol_boat_data,
        object_store=object_store,
    )


def swap_roles_for_volunteers_in_allocation_using_swapdata(
    interface: abstractInterface, swap_data: SwapData
):
    try:
        swap_roles_and_groups_for_volunteers_in_allocation(
            object_store=interface.object_store,
            event=swap_data.event,
            volunteer_to_swap_with=swap_data.volunteer_to_swap_with,
            original_volunteer=swap_data.original_volunteer,
            day_to_swap_with=swap_data.day_to_swap_with,
            original_day=swap_data.original_day,
        )
    except Exception as e:
        interface.log_error(
            "Swap roles of %s and %s failed on day %s, error %s"
            % (
                swap_data.volunteer_to_swap_with.name,
                swap_data.original_volunteer.name,
                swap_data.day_to_swap_with.name,
                str(e),
            )
        )
