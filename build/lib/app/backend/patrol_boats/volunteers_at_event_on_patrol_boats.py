from typing import List


from app.backend.patrol_boats.list_of_patrol_boats import get_list_of_patrol_boats

from app.objects.day_selectors import Day
from app.objects.patrol_boats import ListOfPatrolBoats, PatrolBoat, no_patrol_boat
from app.objects.volunteers import ListOfVolunteers, Volunteer

from app.objects.composed.volunteers_at_event_with_patrol_boats import (
    DictOfVolunteersAtEventWithPatrolBoatsByDay,
)
from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_patrol_boats_by_day_for_volunteer_at_event,
)

def no_volunteers_on_patrol_boats_at_event(object_store: ObjectStore, event: Event):
    dict_of_patrol_boat_data = get_dict_of_patrol_boats_by_day_for_volunteer_at_event(object_store=object_store, event=event)
    list_of_volunteers = dict_of_patrol_boat_data.list_of_volunteers_allocated_to_patrol_boat_at_event_on_any_day()

    return len(list_of_volunteers)==0


def get_dict_of_patrol_boats_by_day_for_volunteer_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfVolunteersAtEventWithPatrolBoatsByDay:
    return object_store.get(
        object_definition=object_definition_for_dict_of_patrol_boats_by_day_for_volunteer_at_event,
        event_id=event.id,
    )


def update_dict_of_patrol_boats_by_day_for_volunteer_at_event(
    object_store: ObjectStore,
    dict_of_volunteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
):
    object_store.update(
        object_definition=object_definition_for_dict_of_patrol_boats_by_day_for_volunteer_at_event,
        event_id=dict_of_volunteers_at_event_with_patrol_boats.event.id,
        new_object=dict_of_volunteers_at_event_with_patrol_boats,
    )


def get_list_of_volunteers_allocated_to_patrol_boat_at_event_on_any_day(
    object_store: ObjectStore, event: Event
) -> ListOfVolunteers:
    list_of_voluteers_at_event_with_patrol_boats = (
        get_dict_of_patrol_boats_by_day_for_volunteer_at_event(
            object_store=object_store, event=event
        )
    )
    return (
        list_of_voluteers_at_event_with_patrol_boats.list_of_volunteers_allocated_to_patrol_boat_at_event_on_any_day()
    )


def load_list_of_patrol_boats_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfPatrolBoats:

    patrol_boat_data = get_dict_of_patrol_boats_by_day_for_volunteer_at_event(
        object_store=object_store, event=event
    )
    list_of_boats_at_event = (
        patrol_boat_data.list_of_unique_boats_at_event_including_unallocated()
    )
    all_patrol_boats = patrol_boat_data.list_of_all_patrol_boats

    sorted_list =  all_patrol_boats.sort_from_other_list_of_boats(list_of_boats_at_event)

    return sorted_list


def get_name_of_boat_allocated_to_volunteer_on_day_at_event(
    object_store: ObjectStore, event: Event, volunteer: Volunteer, day: Day, default=""
) -> str:

    boat = get_boat_allocated_to_volunteer_on_day_at_event(
        object_store=object_store,
        event=event,
        volunteer=volunteer,
        day=day,
        default=None,
    )
    if boat is None:
        return default

    return boat.name


def get_boat_allocated_to_volunteer_on_day_at_event(
    object_store: ObjectStore,
    event: Event,
    volunteer: Volunteer,
    day: Day,
    default=no_patrol_boat,
) -> PatrolBoat:

    patrol_boat_data = get_dict_of_patrol_boats_by_day_for_volunteer_at_event(
        object_store=object_store, event=event
    )
    boat_dict = patrol_boat_data.patrol_boats_for_volunteer(volunteer)

    return boat_dict.boat_on_day(day, default=default)


def get_list_of_visible_boat_names_excluding_boats_already_at_event(
    object_store: ObjectStore, event: Event
) -> List[str]:
    patrol_boat_data = get_dict_of_patrol_boats_by_day_for_volunteer_at_event(
        object_store=object_store, event=event
    )
    list_of_boats_at_event = (
        patrol_boat_data.list_of_unique_boats_at_event_including_unallocated()
    )
    names_of_boats_at_event = list_of_boats_at_event.list_of_names()

    all_boats = get_list_of_patrol_boats(object_store)

    return [boat.name for boat in all_boats if (not boat.name in names_of_boats_at_event) and (not boat.hidden)]


def get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day(
    object_store: ObjectStore, day: Day, event: Event
) -> List[str]:
    list_of_voluteers_at_event_with_patrol_boats = (
        get_dict_of_patrol_boats_by_day_for_volunteer_at_event(
            object_store=object_store, event=event
        )
    )
    list_of_voluteers_on_day = list_of_voluteers_at_event_with_patrol_boats.volunteers_assigned_to_any_boat_on_given_day(
        day
    )

    return list_of_voluteers_on_day.list_of_ids
