from typing import List

from app.data_access.data_layer.data_layer import DataLayer
from app.OLD_backend.data.patrol_boats import PatrolBoatsData
from app.OLD_backend.rota.warnings import process_warning_list
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.primtive_with_id.patrol_boats import PatrolBoat


def warn_on_pb2_drivers(data_layer: DataLayer, event: Event) -> List[str]:
    patrol_boats = PatrolBoatsData(data_layer)
    boats_at_event = patrol_boats.list_of_unique_boats_at_event_including_unallocated(
        event
    )
    list_of_warnings = []
    for patrol_boat in boats_at_event:
        list_of_warnings += warn_on_pb2_drivers_for_boat(
            data_layer=data_layer, event=event, patrol_boat=patrol_boat
        )

    list_of_warnings = process_warning_list(list_of_warnings)

    return list_of_warnings


def warn_on_pb2_drivers_for_boat(
    data_layer: DataLayer, event: Event, patrol_boat: PatrolBoat
) -> List[str]:
    list_of_warnings = [
        warn_on_pb2_drivers_for_boat_on_day(
            data_layer=data_layer, event=event, patrol_boat=patrol_boat, day=day
        )
        for day in event.weekdays_in_event()
    ]

    return list_of_warnings


def warn_on_pb2_drivers_for_boat_on_day(
    data_layer: DataLayer, event: Event, patrol_boat: PatrolBoat, day: Day
) -> str:
    patrol_boat_data = PatrolBoatsData(data_layer)
    at_least_one_volunteer_on_boat_on_day_has_boat_skill = (
        patrol_boat_data.at_least_one_volunteer_on_boat_on_day_has_boat_skill(
            event=event, patrol_boat=patrol_boat, day=day
        )
    )
    if not at_least_one_volunteer_on_boat_on_day_has_boat_skill:
        return "%s on %s has no PB2 qualified person on board" % (
            patrol_boat.name,
            day.name,
        )
    else:
        return ""
