from typing import List

import pandas as pd

from app.backend.data.volunteer_allocation import load_list_of_volunteers_at_event
from app.backend.data.volunteer_rota import load_volunteers_in_role_at_event
from app.backend.data.volunteers import load_list_of_volunteer_skills
from app.backend.volunteers.volunteer_rota import get_volunteer_role_at_event_on_day
from app.data_access.configuration.configuration import VOLUNTEER_ROLES

from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.constants import missing_data
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.backend.data.resources import load_list_of_voluteers_at_event_with_patrol_boats, save_list_of_voluteers_at_event_with_patrol_boats, load_list_of_patrol_boats
from app.objects.patrol_boats import PatrolBoat
from app.objects.utils import in_x_not_in_y, in_both_x_and_y
from app.objects.volunteers import Volunteer


def get_summary_list_of_boat_allocations_for_events(event: Event) -> PandasDFTable:
    list_of_patrol_boats = load_list_of_patrol_boats()
    list_of_voluteers_at_event_with_patrol_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
    list_of_boats_at_event = list_of_voluteers_at_event_with_patrol_boats.list_of_unique_boats_at_event_including_unallocated(list_of_patrol_boats)

    results_as_dict = dict([
        (day.name,
            get_summary_list_of_boat_allocations_for_day_by_boat(day=day, list_of_voluteers_at_event_with_patrol_boats=list_of_voluteers_at_event_with_patrol_boats,
                                                                 list_of_boats_at_event=list_of_boats_at_event))

        for day in event.weekdays_in_event()
    ])
    boat_index = [boat.name for boat in list_of_boats_at_event]

    summary_df= pd.DataFrame(results_as_dict, index=boat_index)
    summary_df.columns = event.weekdays_in_event_as_list_of_string()

    return PandasDFTable(summary_df)

def get_summary_list_of_boat_allocations_for_day_by_boat( day: Day, list_of_voluteers_at_event_with_patrol_boats,
                                                         list_of_boats_at_event) -> list:
    return  [
        len(list_of_voluteers_at_event_with_patrol_boats.
        list_of_volunteer_ids_assigned_to_boat_and_day(patrol_boat=patrol_boat,
                                                        day=day)
                                                                                                )
    for patrol_boat in list_of_boats_at_event]

def add_named_boat_to_event_with_no_allocation(name_of_boat_added: str, event: Event):
    list_of_voluteers_at_event_with_patrol_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
    list_of_patrol_boats = load_list_of_patrol_boats()
    patrol_boat_id = list_of_patrol_boats.id_given_name(name_of_boat_added)
    list_of_voluteers_at_event_with_patrol_boats.add_unallocated_boat(patrol_boat_id=patrol_boat_id)
    save_list_of_voluteers_at_event_with_patrol_boats(event=event,
                                                      volunteers_with_boats_at_event=list_of_voluteers_at_event_with_patrol_boats)


def remove_patrol_boat_and_all_associated_volunteer_connections_from_event(event: Event, patrol_boat_name: str):
    list_of_patrol_boats = load_list_of_patrol_boats()
    patrol_boat_id = list_of_patrol_boats.id_given_name(patrol_boat_name)
    print("deleting id %s" % patrol_boat_id)
    list_of_voluteers_at_event_with_patrol_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
    list_of_voluteers_at_event_with_patrol_boats.remove_patrol_boat_id_and_all_associated_volunteer_connections_from_event(patrol_boat_id)
    save_list_of_voluteers_at_event_with_patrol_boats(event=event,
                                                      volunteers_with_boats_at_event=list_of_voluteers_at_event_with_patrol_boats)

def get_volunteer_ids_allocated_to_patrol_boat_at_event_on_days_sorted_by_role(boat_at_event: PatrolBoat,
                                                                               day: Day,
                                                                               event: Event):

    list_of_voluteers_at_event_with_patrol_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
    list_of_volunteer_ids = list_of_voluteers_at_event_with_patrol_boats.list_of_volunteer_ids_assigned_to_boat_and_day(day=day,
                                                                                                       patrol_boat=boat_at_event)

    return sort_list_of_volunteer_ids_for_day_and_event_by_role(
        list_of_volunteer_ids=list_of_volunteer_ids,
        day=day,
     event=event
    )

def sort_list_of_volunteer_ids_for_day_and_event_by_role(list_of_volunteer_ids: List[str],
                                                         day: Day,
                                                         event: Event) -> List[str]:

    new_list = []
    for role in VOLUNTEER_ROLES:
        list_of_volunteer_ids_for_this_role = [volunteer_id             for volunteer_id in list_of_volunteer_ids
        if get_volunteer_role_at_event_on_day(day=day, volunteer_id=volunteer_id, event=event)==role
        ]
        new_list+=list_of_volunteer_ids_for_this_role

    remaining_not_in_any_role = in_x_not_in_y(x=list_of_volunteer_ids, y=new_list)
    new_list+=remaining_not_in_any_role

    return new_list

def get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day(
                                                               day: Day,
                                                               event: Event):

    list_of_voluteers_at_event_with_patrol_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
    return list_of_voluteers_at_event_with_patrol_boats.list_of_volunteer_ids_assigned_to_any_boat_on_day(day=day)


def get_sorted_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(
            event: Event,
            day: Day,
            boat_at_event: PatrolBoat
        ) -> List[str]:


    volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day = get_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(
        event=event,
        day=day
    )

    sorted_volunteer_ids = sort_volunteer_ids_by_role_and_skills(
        volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day = volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
        day=day,
        event=event
    )

    return sorted_volunteer_ids


def get_volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day(event: Event,
                                                                                       day: Day):

    volunteer_ids_already_allocated = get_volunteer_ids_allocated_to_any_patrol_boat_at_event_on_day(event=event, day=day)
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event)
    list_of_volunteer_ids_at_event = list_of_volunteers_at_event.list_of_volunteer_ids

    volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day = in_x_not_in_y(
        x=list_of_volunteer_ids_at_event,
        y=volunteer_ids_already_allocated
    )

    return volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day

def sort_volunteer_ids_by_role_and_skills(volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day: List[str],
                                          event: Event,
                                          day: Day) -> List[str]:

    sorted_list_of_ids = []
    volunteer_ids_in_boat_related_roles_on_day_of_event= get_volunteer_ids_in_boat_related_roles_on_day_of_event(event=event, day=day)
    add_to_list_of_ids(list_of_ids_to_draw_from=volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
                       list_of_existing_ids=sorted_list_of_ids,
                       list_to_add_from=volunteer_ids_in_boat_related_roles_on_day_of_event)

    volunteer_ids_in_boat_related_roles_on_any_day_of_event= get_volunteer_ids_in_boat_related_roles_on_any_day_of_event(event)
    add_to_list_of_ids(list_of_ids_to_draw_from=volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
                       list_of_existing_ids=sorted_list_of_ids,
                       list_to_add_from=volunteer_ids_in_boat_related_roles_on_any_day_of_event)

    all_volunteer_ids_allocated_to_any_boat_or_day = get_all_volunteer_ids_allocated_to_any_boat_or_day(event)
    add_to_list_of_ids(list_of_ids_to_draw_from=volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
                       list_of_existing_ids=sorted_list_of_ids,
                       list_to_add_from=all_volunteer_ids_allocated_to_any_boat_or_day)

    list_of_volunteer_ids_with_boat_skills = get_list_of_volunteer_ids_with_boat_skills()
    add_to_list_of_ids(list_of_ids_to_draw_from=volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
                       list_of_existing_ids=sorted_list_of_ids,
                       list_to_add_from=list_of_volunteer_ids_with_boat_skills)

    ## Everyone else
    add_to_list_of_ids(list_of_ids_to_draw_from=volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day,
                       list_of_existing_ids=sorted_list_of_ids,
                       list_to_add_from=volunteer_ids_for_volunteers_at_event_but_not_yet_on_patrol_boats_on_given_day)

    return sorted_list_of_ids


def remove_volunteer_from_patrol_boat_on_day_at_event(volunteer_id: str, day: Day,
                                                      event: Event):

    list_of_voluteers_at_event_with_patrol_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
    list_of_voluteers_at_event_with_patrol_boats.remove_volunteer_from_patrol_boat_on_day_at_event(
        volunteer_id=volunteer_id,
        day=day
    )
    save_list_of_voluteers_at_event_with_patrol_boats(event=event, volunteers_with_boats_at_event=list_of_voluteers_at_event_with_patrol_boats)


def volunteer_is_on_same_boat_for_all_days(event: Event,
                                           volunteer_id: str) -> bool:
    list_of_voluteers_at_event_with_patrol_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
    return list_of_voluteers_at_event_with_patrol_boats.volunteer_is_on_same_boat_for_all_days(volunteer_id=volunteer_id, event=event)


def copy_across_allocation_of_boats_at_event(event: Event, day: Day, volunteer_id: str):
    list_of_voluteers_at_event_with_patrol_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
    list_of_voluteers_at_event_with_patrol_boats.copy_across_allocation_of_boats_at_event(day=day, volunteer_id=volunteer_id, event=event)
    save_list_of_voluteers_at_event_with_patrol_boats(event=event, volunteers_with_boats_at_event=list_of_voluteers_at_event_with_patrol_boats)


def swap_boats_for_volunteers_in_allocation(event: Event,
                                                                           original_day: Day,
                                                                           original_volunteer_id: str,
                                                                           day_to_swap_with: Day,
                                                                           volunteer_id_to_swap_with: str):

    list_of_voluteers_at_event_with_patrol_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
    list_of_voluteers_at_event_with_patrol_boats.swap_boats_for_volunteers_in_allocation(
        original_volunteer_id=original_volunteer_id,
        volunteer_id_to_swap_with=volunteer_id_to_swap_with,
        day_to_swap_with=day_to_swap_with,
        original_day=original_day
    )
    save_list_of_voluteers_at_event_with_patrol_boats(event=event, volunteers_with_boats_at_event=list_of_voluteers_at_event_with_patrol_boats)

def get_boat_name_allocated_to_volunteer_on_day_at_event(event: Event, day: Day, volunteer_id: str) -> str:
    list_of_voluteers_at_event_with_patrol_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
    patrol_boat_id = list_of_voluteers_at_event_with_patrol_boats.which_boat_id_is_volunteer_on_today(day=day, volunteer_id=volunteer_id)
    if patrol_boat_id is missing_data:
        return missing_data

    boats = load_list_of_patrol_boats()
    boat = boats.object_with_id(patrol_boat_id)

    return boat.name


def add_to_list_of_ids(list_of_ids_to_draw_from: List[str],
                       list_of_existing_ids: List[str],
                       list_to_add_from: List[str]):

    potential_new_ids = in_both_x_and_y(list_of_ids_to_draw_from, list_to_add_from)
    new_ids_excluding_already_in = in_x_not_in_y(x=potential_new_ids, y=list_of_existing_ids)

    list_of_existing_ids+=new_ids_excluding_already_in


def get_list_of_volunteer_ids_with_boat_skills()-> List[str]:
    volunteer_skills = load_list_of_volunteer_skills()
    list_of_volunteer_ids_with_boat_skills = volunteer_skills.list_of_volunteer_ids_with_boat_related_skill()

    return list_of_volunteer_ids_with_boat_skills


def get_volunteer_ids_in_boat_related_roles_on_day_of_event(event: Event, day: Day) -> List[str]:
    volunteers_in_role_at_event = load_volunteers_in_role_at_event(event)
    volunteer_ids_in_boat_related_roles_on_day_of_event = volunteers_in_role_at_event.list_of_volunteer_ids_in_boat_related_role_on_day(day)

    return volunteer_ids_in_boat_related_roles_on_day_of_event


def get_volunteer_ids_in_boat_related_roles_on_any_day_of_event(event: Event) -> List[str]:
    volunteers_in_role_at_event = load_volunteers_in_role_at_event(event)
    volunteer_ids_in_boat_related_roles_on_any_day_of_event = volunteers_in_role_at_event.list_of_volunteer_ids_in_boat_related_role_on_any_day()

    return volunteer_ids_in_boat_related_roles_on_any_day_of_event


def get_all_volunteer_ids_allocated_to_any_boat_or_day(
                                                               event: Event):

    list_of_voluteers_at_event_with_patrol_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
    return list_of_voluteers_at_event_with_patrol_boats.list_of_all_volunteer_ids_at_event()


def allocate_volunteer_to_boat_at_event_on_day(volunteer: Volunteer,
                                                  event: Event,
                                                  day: Day,
                                                  patrol_boat: PatrolBoat):

    list_of_voluteers_at_event_with_patrol_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
    list_of_voluteers_at_event_with_patrol_boats.add_volunteer_with_boat(
        volunteer_id=volunteer.id,
        day=day,
        patrol_boat_id=patrol_boat.id
    )
    save_list_of_voluteers_at_event_with_patrol_boats(event=event, volunteers_with_boats_at_event=list_of_voluteers_at_event_with_patrol_boats)
