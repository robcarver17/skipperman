from typing import List

from app.OLD_backend.OLD_patrol_boats.data import (
    get_list_of_voluteers_at_event_with_patrol_boats_from_cache,
    load_list_of_patrol_boats_at_event_from_cache,
)

from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache

from app.backend.volunteers.warnings import process_warning_list
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.patrol_boats import PatrolBoat


def warn_on_pb2_drivers(cache: AdHocCache, event: Event) -> List[str]:
    list_of_boats_at_event = load_list_of_patrol_boats_at_event_from_cache(
        cache=cache, event=event
    )
    list_of_warnings = []
    for patrol_boat in list_of_boats_at_event:
        list_of_warnings += warn_on_pb2_drivers_for_boat(
            cache=cache, event=event, patrol_boat=patrol_boat
        )

    list_of_warnings = process_warning_list(list_of_warnings)

    return list_of_warnings


def warn_on_pb2_drivers_for_boat(
    cache: AdHocCache, event: Event, patrol_boat: PatrolBoat
) -> List[str]:
    list_of_warnings = [
        warn_on_pb2_drivers_for_boat_on_day(
            cache=cache, event=event, patrol_boat=patrol_boat, day=day
        )
        for day in event.weekdays_in_event()
    ]

    return list_of_warnings


def warn_on_pb2_drivers_for_boat_on_day(
    cache: AdHocCache, event: Event, patrol_boat: PatrolBoat, day: Day
) -> str:
    list_of_voluteers_at_event_with_patrol_boats = (
        get_list_of_voluteers_at_event_with_patrol_boats_from_cache(
            cache=cache, event=event
        )
    )
    assigned_to_boat_and_day = (
        list_of_voluteers_at_event_with_patrol_boats.assigned_to_boat_on_day(
            patrol_boat=patrol_boat, day=day
        )
    )
    with_pb2 = assigned_to_boat_and_day.volunteers_with_pb2()
    if len(with_pb2) == 0:
        return "%s on %s has no PB2 qualified person on board" % (
            patrol_boat.name,
            day.name,
        )
    else:
        return ""
