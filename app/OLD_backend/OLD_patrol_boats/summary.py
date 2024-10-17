from typing import List

import pandas as pd
from app.OLD_backend.OLD_patrol_boats.data import load_list_of_patrol_boats_at_event_from_cache
from app.OLD_backend.OLD_patrol_boats.data import get_list_of_voluteers_at_event_with_patrol_boats_from_cache
from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache
from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects_OLD.patrol_boats import ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats
from app.objects.patrol_boats import ListOfPatrolBoats, PatrolBoat


def get_summary_list_of_patrol_boat_allocations_for_events(
    cache: AdHocCache, event: Event
) -> PandasDFTable:
    list_of_voluteers_at_event_with_patrol_boats = get_list_of_voluteers_at_event_with_patrol_boats_from_cache(cache=cache, event=event)
    list_of_boats_at_event = load_list_of_patrol_boats_at_event_from_cache(cache=cache, event=event)

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




def get_summary_list_of_boat_allocations_for_day_by_boat(
    day: Day, list_of_voluteers_at_event_with_patrol_boats: ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats,
        list_of_boats_at_event: ListOfPatrolBoats
) -> List[int]:
    return [
        get_number_of_volunteers_allocated_to_day_and_boat_for_day_by_boat(day=day,
                                                                           list_of_voluteers_at_event_with_patrol_boats=list_of_voluteers_at_event_with_patrol_boats,
                                                                           patrol_boat=patrol_boat)
        for patrol_boat in list_of_boats_at_event
    ]


def get_number_of_volunteers_allocated_to_day_and_boat_for_day_by_boat(
    day: Day, list_of_voluteers_at_event_with_patrol_boats: ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats, patrol_boat: PatrolBoat
) -> int:
    return \
            list_of_voluteers_at_event_with_patrol_boats.number_of_volunteers_and_boats_assigned_to_boat_and_day(
                patrol_boat=patrol_boat, day=day
            )


