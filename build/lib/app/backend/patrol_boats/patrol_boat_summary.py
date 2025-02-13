from typing import List

import pandas as pd
from app.data_access.store.object_store import ObjectStore

from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.patrol_boats import ListOfPatrolBoats, PatrolBoat
from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_all_event_data_for_volunteers,
)
from app.backend.patrol_boats.list_of_patrol_boats import get_list_of_patrol_boats

from app.objects.composed.volunteers_at_event_with_patrol_boats import (
    DictOfVolunteersAtEventWithPatrolBoatsByDay,
)


def get_summary_list_of_patrol_boat_allocations_for_events(
    object_store: ObjectStore, event: Event
) -> PandasDFTable:
    all_volunteer_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )
    dict_of_volunteers_at_event_with_patrol_boats = (
        all_volunteer_event_data.dict_of_volunteers_at_event_with_patrol_boats
    )

    list_of_boats_at_event = (
        dict_of_volunteers_at_event_with_patrol_boats.list_of_unique_boats_at_event_including_unallocated()
    )
    list_of_all_boats = get_list_of_patrol_boats(object_store)
    sorted_list_of_boats_at_event = (
        list_of_boats_at_event.sort_from_other_list_of_boats(list_of_all_boats)
    )

    results_as_dict = dict(
        [
            (
                day.name,
                get_summary_list_of_boat_allocations_for_day_by_boat(
                    day=day,
                    dict_of_voluteers_at_event_with_patrol_boats=dict_of_volunteers_at_event_with_patrol_boats,
                    list_of_boats_at_event=sorted_list_of_boats_at_event,
                ),
            )
            for day in event.days_in_event()
        ]
    )
    boat_index = [boat.name for boat in sorted_list_of_boats_at_event]

    summary_df = pd.DataFrame(results_as_dict, index=boat_index)
    summary_df.columns = event.days_in_event_as_list_of_string()

    summary_table = PandasDFTable(summary_df)

    return summary_table


def get_summary_list_of_boat_allocations_for_day_by_boat(
    day: Day,
    dict_of_voluteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
    list_of_boats_at_event: ListOfPatrolBoats,
) -> List[int]:
    return [
        get_number_of_volunteers_allocated_to_day_and_boat_for_day_by_boat(
            day=day,
            dict_of_voluteers_at_event_with_patrol_boats=dict_of_voluteers_at_event_with_patrol_boats,
            patrol_boat=patrol_boat,
        )
        for patrol_boat in list_of_boats_at_event
    ]


def get_number_of_volunteers_allocated_to_day_and_boat_for_day_by_boat(
    day: Day,
    dict_of_voluteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
    patrol_boat: PatrolBoat,
) -> int:
    return dict_of_voluteers_at_event_with_patrol_boats.number_of_volunteers_and_boats_assigned_to_boat_and_day(
        patrol_boat=patrol_boat, day=day
    )
