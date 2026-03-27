from typing import List

import pandas as pd
from app.data_access.store.object_store import ObjectStore

from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.patrol_boats import ListOfPatrolBoats, PatrolBoat

from app.objects.composed.volunteers_at_event_with_patrol_boats import (
    DictOfVolunteersAtEventWithPatrolBoatsByDay,
)
from app.backend.patrol_boats.volunteers_at_event_on_patrol_boats import (
    get_dict_of_patrol_boats_by_day_for_volunteer_at_event,
)

from app.backend.patrol_boats.volunteers_at_event_on_patrol_boats import (
    get_sorted_list_of_patrol_boats_at_event,
)


def get_summary_list_of_patrol_boat_allocations_for_events(
    object_store: ObjectStore, event: Event
) -> PandasDFTable:
    dict_of_volunteers_at_event_with_patrol_boats = (
        get_dict_of_patrol_boats_by_day_for_volunteer_at_event(
            object_store=object_store, event=event
        )
    )

    sorted_list_of_boats_at_event = get_sorted_list_of_patrol_boats_at_event(
        object_store=object_store, event=event
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
            for day in event.volunteer_days_in_event()
        ]
    )
    boat_index = [boat.name for boat in sorted_list_of_boats_at_event]

    summary_df = pd.DataFrame(results_as_dict, index=boat_index)
    summary_df.columns = event.volunteer_days_in_event_as_list_of_string()

    if len(summary_df) > 0:
        summary_df.loc["TOTAL"] = summary_df.sum(axis=0, numeric_only=True)

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
