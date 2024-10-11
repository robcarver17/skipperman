from dataclasses import dataclass

from app.data_access.store.data_layer import DataLayer

from app.objects.exceptions import missing_data

from app.OLD_backend.volunteers.volunteers import (
    get_volunteer_from_id,
    get_sorted_list_of_volunteers,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.volunteers import SORT_BY_FIRSTNAME, VolunteerData
from typing import List

from app.OLD_backend.data.volunteer_rota import VolunteerRotaData

from app.OLD_backend.rota.volunteer_rota import (
    SwapData,
)

from app.objects.day_selectors import Day
from app.objects.events import Event
from app.OLD_backend.data.patrol_boats import PatrolBoatsData
from app.objects.patrol_boats import PatrolBoat
from app.objects.utils import in_x_not_in_y, in_both_x_and_y
from app.objects.volunteers import Volunteer, ListOfVolunteers


def add_named_boat_to_event_with_no_allocation(
    interface: abstractInterface, name_of_boat_added: str, event: Event
):
    patrol_boat_data = PatrolBoatsData(interface.data)
    patrol_boat_data.add_named_boat_to_event_with_no_allocation(
        name_of_boat_added=name_of_boat_added, event=event
    )


def remove_patrol_boat_and_all_associated_volunteer_connections_from_event(
    interface: abstractInterface, event: Event, patrol_boat_name: str
):
    patrol_boat_data = PatrolBoatsData(interface.data)
    patrol_boat_data.remove_patrol_boat_and_all_associated_volunteer_connections_from_event(
        event=event, patrol_boat_name=patrol_boat_name
    )


def get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day(
    interface: abstractInterface, day: Day, event: Event
) -> List[str]:
    patrol_boat_data = PatrolBoatsData(interface.data)
    return (
        patrol_boat_data.get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day(
            event=event, day=day
        )
    )

def get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_any_day(
    data_layer: DataLayer, event: Event
) -> List[str]:
    patrol_boat_data = PatrolBoatsData(data_layer)
    return patrol_boat_data.get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_any_day(
        event
    )


def DEPRECATE_get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_any_day(
    interface: abstractInterface, event: Event
) -> List[str]:
    patrol_boat_data = PatrolBoatsData(interface.data)
    return patrol_boat_data.get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_any_day(
        event
    )


def get_sorted_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(
    data_layer: DataLayer,
    event: Event,
    day: Day,
) -> List[str]:
    volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day = get_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(
        data_layer=data_layer, event=event, day=day
    )

    sorted_volunteer_ids = sort_volunteer_ids_by_role_and_skills_and_then_name(
        data_layer=data_layer,
        event=event,
        day=day,
        volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day=volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
    )

    return sorted_volunteer_ids


def get_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(
    data_layer: DataLayer, event: Event, day: Day
):
    patrol_boat_data = PatrolBoatsData(data_layer)
    return patrol_boat_data.get_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(
        event=event, day=day
    )


def sort_volunteer_ids_by_role_and_skills_and_then_name(
    data_layer: DataLayer,
    volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day: List[
        str
    ],
    event: Event,
    day: Day,
) -> List[str]:
    sorted_list_of_volunteers = get_sorted_list_of_volunteers(
        data_layer=data_layer, sort_by=SORT_BY_FIRSTNAME
    )

    sorted_list_of_ids = []

    volunteer_ids_in_boat_related_roles_on_day_of_event = (
        get_volunteer_ids_in_boat_related_roles_on_day_of_event(
            data_layer=data_layer, event=event, day=day
        )
    )
    add_to_list_of_volunteer_ids(
        list_of_ids_to_draw_from=volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
        list_of_existing_ids=sorted_list_of_ids,
        list_to_add_from=volunteer_ids_in_boat_related_roles_on_day_of_event,
        sorted_list_of_volunteers=sorted_list_of_volunteers,
    )

    volunteer_ids_in_boat_related_roles_on_any_day_of_event = (
        get_volunteer_ids_in_boat_related_roles_on_any_day_of_event(
            data_layer=data_layer, event=event
        )
    )
    add_to_list_of_volunteer_ids(
        list_of_ids_to_draw_from=volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
        list_of_existing_ids=sorted_list_of_ids,
        list_to_add_from=volunteer_ids_in_boat_related_roles_on_any_day_of_event,
        sorted_list_of_volunteers=sorted_list_of_volunteers,
    )

    all_volunteer_ids_allocated_to_any_boat_or_day = (
        get_all_volunteer_ids_allocated_to_any_boat_or_day(
            data_layer=data_layer, event=event
        )
    )
    add_to_list_of_volunteer_ids(
        list_of_ids_to_draw_from=volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
        list_of_existing_ids=sorted_list_of_ids,
        list_to_add_from=all_volunteer_ids_allocated_to_any_boat_or_day,
        sorted_list_of_volunteers=sorted_list_of_volunteers,
    )

    list_of_volunteer_ids_with_boat_skills = get_list_of_volunteer_ids_who_can_drive_safety_boat(
        data_layer=data_layer
    )
    add_to_list_of_volunteer_ids(
        list_of_ids_to_draw_from=volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
        list_of_existing_ids=sorted_list_of_ids,
        list_to_add_from=list_of_volunteer_ids_with_boat_skills,
        sorted_list_of_volunteers=sorted_list_of_volunteers,
    )

    ## Everyone else

    add_to_list_of_volunteer_ids(
        list_of_ids_to_draw_from=volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
        list_of_existing_ids=sorted_list_of_ids,
        list_to_add_from=volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
        sorted_list_of_volunteers=sorted_list_of_volunteers,
    )

    return sorted_list_of_ids


def remove_volunteer_from_patrol_boat_on_day_at_event(
    interface: abstractInterface, volunteer_id: str, day: Day, event: Event
):
    patrol_boat_data = PatrolBoatsData(interface.data)
    patrol_boat_data.remove_volunteer_with_id_from_patrol_boat_on_day_at_event(
        volunteer_id=volunteer_id, event=event, day=day
    )


def copy_across_earliest_allocation_of_boats_at_event(
    interface: abstractInterface, event: Event, volunteer_id: str, allow_overwrite: bool
):
    earliest_day = earliest_day_with_boat_for_volunteer(
        interface=interface, event=event, volunteer_id=volunteer_id
    )
    if earliest_day is None:
        return
    copy_across_boats_at_event(
        interface=interface,
        event=event,
        volunteer_id=volunteer_id,
        day=earliest_day,
        allow_overwrite=allow_overwrite,
    )


def copy_across_boats_at_event(
    interface: abstractInterface,
    event: Event,
    volunteer_id: str,
    day: Day,
    allow_overwrite: bool,
):
    patrol_boat_data = PatrolBoatsData(interface.data)

    try:
        patrol_boat_data.copy_across_allocation_of_boats_at_event(
            event=event,
            day=day,
            volunteer_id=volunteer_id,
            allow_overwrite=allow_overwrite,
        )
    except Exception as e:
        name = get_volunteer_from_id(
            data_layer=interface.data, volunteer_id=volunteer_id
        )
        interface.log_error(
            "Can't copy across boat data for %s on %s, error %s, conflicting change made?"
            % (name, day.name, str(e))
        )


def earliest_day_with_boat_for_volunteer(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> Day:
    patrol_boat_data = PatrolBoatsData(interface.data)
    for day in event.weekdays_in_event():
        if (
            patrol_boat_data.get_boat_allocated_to_volunteer_on_day_at_event(
                event=event, volunteer_id=volunteer_id, day=day
            )
            is missing_data
        ):
            continue
        return day

    return None


def swap_boats_for_volunteers_in_allocation(
    interface: abstractInterface, swap_data: SwapData
):
    patrol_boat_data = PatrolBoatsData(interface.data)
    patrol_boat_data.swap_boats_for_volunteers_in_allocation(
        event=swap_data.event,
        original_volunteer_id=swap_data.original_volunteer_id,
        volunteer_id_to_swap_with=swap_data.volunteer_id_to_swap_with,
        day_to_swap_with=swap_data.day_to_swap_with,
        original_day=swap_data.original_day,
    )


def get_boat_name_allocated_to_volunteer_on_day_at_event(
    interface: abstractInterface, event: Event, day: Day, volunteer_id: str
) -> str:
    patrol_boat_data = PatrolBoatsData(interface.data)
    return patrol_boat_data.get_boat_name_allocated_to_volunteer_on_day_at_event(
        event=event, day=day, volunteer_id=volunteer_id
    )


def add_to_list_of_volunteer_ids(
    list_of_ids_to_draw_from: List[str],
    list_of_existing_ids: List[str],
    list_to_add_from: List[str],
    sorted_list_of_volunteers: ListOfVolunteers,
):
    potential_new_ids = in_both_x_and_y(list_of_ids_to_draw_from, list_to_add_from)
    new_ids_excluding_already_in = in_x_not_in_y(
        x=potential_new_ids, y=list_of_existing_ids
    )
    sorted_new_ids_excluding_already_in = (
        sort_list_of_volunteer_ids_as_per_list_of_volunteers(
            list_of_volunteer_ids=new_ids_excluding_already_in,
            sorted_list_of_volunteers=sorted_list_of_volunteers,
        )
    )

    list_of_existing_ids += sorted_new_ids_excluding_already_in


def sort_list_of_volunteer_ids_as_per_list_of_volunteers(
    list_of_volunteer_ids: List[str], sorted_list_of_volunteers: ListOfVolunteers
):
    sorted_subset_list_of_volunteers = ListOfVolunteers.subset_from_list_of_ids(
        full_list=sorted_list_of_volunteers, list_of_ids=list_of_volunteer_ids
    )
    return sorted_subset_list_of_volunteers.list_of_ids


def get_list_of_volunteer_ids_who_can_drive_safety_boat(
    data_layer: DataLayer,
) -> List[str]:
    volunteer_data = VolunteerData(data_layer)
    list_of_volunteer_ids_with_boat_skills = (
        volunteer_data.list_of_volunteer_ids_who_can_drive_safety_boat()
    )

    return list_of_volunteer_ids_with_boat_skills


def get_volunteer_ids_in_boat_related_roles_on_day_of_event(
    data_layer: DataLayer, event: Event, day: Day
) -> List[str]:
    volunteer_rota_data = VolunteerRotaData(data_layer)
    volunteer_ids_in_boat_related_roles_on_day_of_event = (
        volunteer_rota_data.get_volunteer_ids_in_boat_related_roles_on_day_of_event(
            event=event, day=day
        )
    )

    return volunteer_ids_in_boat_related_roles_on_day_of_event


def get_volunteer_ids_in_boat_related_roles_on_any_day_of_event(
    data_layer: DataLayer, event: Event
) -> List[str]:
    volunteer_rota_data = VolunteerRotaData(data_layer)
    volunteer_ids_in_boat_related_roles_on_any_day_of_event = (
        volunteer_rota_data.get_volunteer_ids_in_boat_related_roles_on_any_day_of_event(
            event=event
        )
    )

    return volunteer_ids_in_boat_related_roles_on_any_day_of_event


def get_all_volunteer_ids_allocated_to_any_boat_or_day(
    data_layer: DataLayer, event: Event
):
    patrol_boat_data = PatrolBoatsData(data_layer)
    return patrol_boat_data.get_all_volunteer_ids_allocated_to_any_boat_or_day(event)


@dataclass
class BoatDayVolunteer:
    boat: PatrolBoat
    day: Day
    volunteer: Volunteer


NO_ADDITION_TO_MAKE = "No addition to make"


class ListOfBoatDayVolunteer(list):
    def __init__(self, input: List[BoatDayVolunteer]):
        super().__init__(input)

    def remove_no_additions(self):
        return ListOfBoatDayVolunteer(
            [bdv for bdv in self if not bdv is NO_ADDITION_TO_MAKE]
        )


def add_list_of_new_boat_day_volunteer_allocations_to_data_reporting_conflicts(
    interface: abstractInterface,
    list_of_volunteer_additions_to_boats: ListOfBoatDayVolunteer,
    event: Event,
):
    patrol_boat_data = PatrolBoatsData(interface.data)
    list_of_volunteers_at_event_with_boats = (
        patrol_boat_data.get_list_of_voluteers_at_event_with_patrol_boats(event)
    )
    for boat_day_volunteer in list_of_volunteer_additions_to_boats:
        try:
            list_of_volunteers_at_event_with_boats.add_volunteer_with_boat(
                volunteer_id=boat_day_volunteer.volunteer.id,
                day=boat_day_volunteer.day,
                patrol_boat_id=boat_day_volunteer.boat.id,
            )
        except Exception as e:
            interface.log_error(
                "Can't add volunteer %s to boat %s on day %s; error %s"
                % (
                    str(boat_day_volunteer.volunteer),
                    str(boat_day_volunteer.boat),
                    boat_day_volunteer.day.name,
                    str(e),
                )
            )

    patrol_boat_data.save_list_of_voluteers_at_event_with_patrol_boats(
        list_of_volunteers_at_event_with_patrol_boats=list_of_volunteers_at_event_with_boats,
        event=event,
    )
