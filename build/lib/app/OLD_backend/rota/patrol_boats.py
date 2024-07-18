from dataclasses import dataclass

from app.data_access.data_layer.ad_hoc_cache import AdHocCache

from app.data_access.data_layer.data_layer import DataLayer

from app.objects.exceptions import missing_data

from app.OLD_backend.volunteers.volunteers import (
    get_volunteer_from_id,
    get_sorted_list_of_volunteers,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.volunteers import SORT_BY_FIRSTNAME, VolunteerData
from typing import List

import pandas as pd

from app.OLD_backend.data.volunteer_rota import VolunteerRotaData
from app.data_access.configuration.skills_and_roles import volunteer_roles

from app.OLD_backend.rota.volunteer_rota import (
    SwapData,
    get_volunteer_role_at_event_on_day,
)

from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.OLD_backend.data.patrol_boats import PatrolBoatsData
from app.objects.primtive_with_id.patrol_boats import PatrolBoat, ListOfPatrolBoats
from app.objects.utils import in_x_not_in_y, in_both_x_and_y
from app.objects.primtive_with_id.volunteers import Volunteer, ListOfVolunteers
from app.objects.patrol_boats import DEPRECATE_ListOfVolunteersAtEventWithPatrolBoats


def get_summary_list_of_boat_allocations_for_events(
    cache: AdHocCache, event: Event
) -> PandasDFTable:
    list_of_voluteers_at_event_with_patrol_boats = cache.get_from_cache(get_list_of_voluteers_at_event_with_patrol_boats, event=event)
    list_of_boats_at_event = cache.get_from_cache(get_list_of_unique_boats_at_event_including_unallocated, event=event)

    results_as_dict = dict(
        [
            (
                day.name,
                get_summary_list_of_boat_allocations_for_day_by_boat(
                    day=day,
                    list_of_voluteers_at_event_with_patrol_boats=list_of_voluteers_at_event_with_patrol_boats,
                    list_of_boats_at_event=list_of_boats_at_event,
                ),
            )
            for day in event.weekdays_in_event()
        ]
    )
    boat_index = [boat.name for boat in list_of_boats_at_event]

    summary_df = pd.DataFrame(results_as_dict, index=boat_index)
    summary_df.columns = event.weekdays_in_event_as_list_of_string()

    summary_table = PandasDFTable(summary_df)

    return summary_table


def  get_list_of_voluteers_at_event_with_patrol_boats(data_layer: DataLayer, event: Event) -> DEPRECATE_ListOfVolunteersAtEventWithPatrolBoats:
    patrol_boat_data = PatrolBoatsData(data_layer)
    list_of_voluteers_at_event_with_patrol_boats = (
        patrol_boat_data.get_volunteers_allocated_to_patrol_boats_at_event(event)
    )
    return list_of_voluteers_at_event_with_patrol_boats

def get_list_of_unique_boats_at_event_including_unallocated(data_layer: DataLayer, event: Event) -> ListOfPatrolBoats:
    patrol_boat_data = PatrolBoatsData(data_layer)
    list_of_boats_at_event = (
        patrol_boat_data.list_of_unique_boats_at_event_including_unallocated(event)
    )
    return list_of_boats_at_event


def get_summary_list_of_boat_allocations_for_day_by_boat(
    day: Day, list_of_voluteers_at_event_with_patrol_boats, list_of_boats_at_event
) -> List[int]:
    return [
        get_number_of_volunteers_allocated_to_day_and_boat_for_day_by_boat(day=day,
                                                                           list_of_voluteers_at_event_with_patrol_boats=list_of_voluteers_at_event_with_patrol_boats,
                                                                           patrol_boat=patrol_boat)
        for patrol_boat in list_of_boats_at_event
    ]

def get_number_of_volunteers_allocated_to_day_and_boat_for_day_by_boat(
    day: Day, list_of_voluteers_at_event_with_patrol_boats: DEPRECATE_ListOfVolunteersAtEventWithPatrolBoats, patrol_boat: PatrolBoat
) -> int:
    return \
        len(
            list_of_voluteers_at_event_with_patrol_boats.list_of_volunteers_and_boats_assigned_to_boat_and_day(
                patrol_boat=patrol_boat, day=day
            )
        )


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


def get_sorted_volunteer_ids_allocated_to_patrol_boat_at_event_on_days_sorted_by_role(
    data_layer: DataLayer, patrol_boat: PatrolBoat, day: Day, event: Event
) -> List[str]:
    patrol_boat_data = PatrolBoatsData(data_layer)
    list_of_volunteer_ids = (
        patrol_boat_data.list_of_volunteer_ids_assigned_to_boat_and_day(
            event=event, day=day, patrol_boat=patrol_boat
        )
    )

    return sort_list_of_volunteer_ids_for_day_and_event_by_role(
        data_layer=data_layer,
        list_of_volunteer_ids=list_of_volunteer_ids,
        day=day,
        event=event,
    )



def sort_list_of_volunteer_ids_for_day_and_event_by_role(
    data_layer: DataLayer,
    list_of_volunteer_ids: List[str],
    day: Day,
    event: Event,
) -> List[str]:
    new_list = []
    for role in volunteer_roles:
        list_of_volunteer_ids_for_this_role = [
            volunteer_id
            for volunteer_id in list_of_volunteer_ids
            if get_volunteer_role_at_event_on_day(
                data_layer=data_layer, day=day, volunteer_id=volunteer_id, event=event
            )
            == role
        ]
        new_list += list_of_volunteer_ids_for_this_role

    remaining_not_in_any_role = in_x_not_in_y(x=list_of_volunteer_ids, y=new_list)
    new_list += remaining_not_in_any_role

    return new_list


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

def get_list_of_volunteers_allocated_to_patrol_boat_at_event_on_any_data(
data_layer: DataLayer, event: Event
) -> ListOfVolunteers:
    patrol_boat_data = PatrolBoatsData(data_layer)
    return patrol_boat_data.get_list_of_volunteers_allocated_to_patrol_boat_at_event_on_any_data(
        event
    ).sort_by_firstname()

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
