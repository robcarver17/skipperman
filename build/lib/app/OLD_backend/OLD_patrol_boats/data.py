from app.objects.utils import in_x_not_in_y

from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache
from app.data_access.store.data_access import DataLayer
from app.data_access.store.DEPRECATE_volunteers_with_patrol_boats import PatrolBoatData
from app.objects.events import Event
from app.objects_OLD.patrol_boats import (
    ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats,
)
from app.objects.patrol_boats import ListOfPatrolBoats


def get_list_of_volunteers_allocated_to_patrol_boat_at_event_on_any_data(
    cache: AdHocCache, event: Event
) -> ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats:
    list_of_voluteers_at_event_with_patrol_boats = (
        get_list_of_voluteers_at_event_with_patrol_boats_from_cache(
            cache=cache, event=event
        )
    )
    return (
        list_of_voluteers_at_event_with_patrol_boats.assigned_to_any_boat_on_any_day()
    )


def get_list_of_voluteers_at_event_with_patrol_boats_from_cache(
    cache: AdHocCache, event: Event
) -> ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats:
    list_of_voluteers_at_event_with_patrol_boats = cache.get_from_cache(
        get_list_of_voluteers_at_event_with_patrol_boats, event=event
    )

    return list_of_voluteers_at_event_with_patrol_boats


def get_list_of_voluteers_at_event_with_patrol_boats(
    data_layer: DataLayer, event: Event
) -> ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats:
    patrol_boat_data = PatrolBoatData(data_layer)
    list_of_voluteers_at_event_with_patrol_boats = (
        patrol_boat_data.get_list_of_volunteers_at_event_with_patrol_boat_and_role(
            event
        )
    )

    return list_of_voluteers_at_event_with_patrol_boats


def load_list_of_patrol_boats_at_event_from_cache(
    cache: AdHocCache, event: Event
) -> ListOfPatrolBoats:
    return cache.get_from_cache(
        get_list_of_unique_boats_at_event_including_unallocated, event=event
    )


def get_list_of_unique_boats_at_event_including_unallocated(
    data_layer: DataLayer, event: Event
) -> ListOfPatrolBoats:
    patrol_boat_data = PatrolBoatData(data_layer)
    list_of_boats_at_event = (
        patrol_boat_data.list_of_unique_boats_at_event_including_unallocated(event)
    )
    return list_of_boats_at_event


def get_sorted_list_of_boats_excluding_boats_already_at_event(
    cache: AdHocCache, event: Event
) -> ListOfPatrolBoats:
    patrol_boat_data = PatrolBoatData(cache.data_layer)
    list_of_all_patrol_boats = patrol_boat_data.get_list_of_patrol_boats()

    list_of_patrol_boats_at_event = load_list_of_patrol_boats_at_event_from_cache(
        cache=cache, event=event
    )
    boats_not_already_at_event = in_x_not_in_y(
        x=list_of_all_patrol_boats, y=list_of_patrol_boats_at_event
    )
    sorted_boats_not_already_at_event = [
        boat for boat in list_of_all_patrol_boats if boat in boats_not_already_at_event
    ]

    return ListOfPatrolBoats(sorted_boats_not_already_at_event)
