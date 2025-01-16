from typing import Dict, List

import pandas as pd

from app.backend.registration_data.cadet_registration_data import get_availability_dict_for_cadets_at_event
from app.objects.cadets import  Cadet
from app.objects.composed.food_at_event import DictOfCadetsWithFoodRequirementsAtEvent
from app.objects.volunteers import Volunteer

from app.backend.food.active_cadets_and_volunteers_with_food import \
    get_dict_of_active_volunteers_with_food_requirements_at_event, get_dict_of_active_cadets_with_food_requirements_at_event
from app.backend.registration_data.volunteer_registration_data import get_availability_dict_for_volunteers_at_event
from app.data_access.store.object_store import ObjectStore

from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.day_selectors import DaySelector, Day
from app.objects.events import Event


def summarise_food_data_by_day(
    object_store: ObjectStore, event: Event, copy_index: bool = False
) -> PandasDFTable:
    ## rows: cadets/ volunteers. columns: day and numbers
    row_for_volunteers = summarise_food_data_by_day_for_volunteers(
        object_store=object_store, event=event
    )
    row_for_cadets = summarise_food_data_by_day_for_cadets(
        object_store=object_store, event=event
    )

    df = pd.concat([row_for_cadets, row_for_volunteers], axis=0)
    df.loc["Total"] = df.sum(numeric_only=True, axis=0)

    if copy_index:
        df.insert(0, "", df.index)

    return PandasDFTable(df)



def summarise_food_data_by_day_for_volunteers(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:
    volunteers_with_food = get_dict_of_active_volunteers_with_food_requirements_at_event(object_store=object_store, event=event)

    availability_dict = get_availability_dict_for_volunteers_at_event(object_store=object_store, event=event)

    range_of_days_worked = list(range(1, len(event.days_in_event()) + 1))
    summary_over_required = {}
    for days_required in range_of_days_worked:
        summary_dict = {}
        for day in event.days_in_event():
            list_to_count = [
                1
                for volunteer, food_requirements in volunteers_with_food.items()
                if volunteer_is_available_on_day_and_meets_days_required_target(
                    volunteer=volunteer,
                    availability_dict=availability_dict,
                    day=day,
                    days_required=days_required,
                )
            ]
            summary_dict[day.name] = sum(list_to_count)
        summary_dict["Count"] = count_number_of_volunteers_meeting_days_required_target(
            availability_dict=availability_dict, days_required=days_required
        )

        summary_over_required["%d day volunteer" % days_required] = summary_dict

    return pd.DataFrame(summary_over_required).transpose()


def summarise_food_data_by_day_for_cadets(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:

    cadets_with_food_requirements= get_dict_of_active_cadets_with_food_requirements_at_event(object_store=object_store, event=event)
    availability_dict = get_availability_dict_for_cadets_at_event(object_store=object_store, event=event)

    summary_over_age_brackets = {}
    for age_window in age_brackets:
        summary_dict = {}

        for day in event.days_in_event():
            list_to_count = [
                1
                for cadet in cadets_with_food_requirements.list_of_cadets()
                if cadet_has_right_age_and_is_available_on_day(
                    cadet=cadet,
                    day=day,
                    age_window=age_window,
                    availability_dict=availability_dict,
                )
            ]
            summary_dict[day.name] = sum(list_to_count)

        summary_dict["Count"] = count_cadets_with_right_age(
            cadets_with_food_requirements=cadets_with_food_requirements,
            age_window=age_window,
        )

        summary_over_age_brackets[
            "Cadet %s" % bracket_to_str(age_window)
        ] = summary_dict

    return pd.DataFrame(summary_over_age_brackets).transpose()


def volunteer_is_available_on_day_and_meets_days_required_target(
    volunteer: Volunteer,
    availability_dict: Dict[Volunteer, DaySelector],
    day: Day,
    days_required: int,
):
    available_on_day = availability_dict[volunteer].available_on_day(day)
    meets_requirement = does_volunteer_meet_days_required_target(
        volunteer=volunteer,
        availability_dict=availability_dict,
        days_required=days_required,
    )

    return available_on_day and meets_requirement


def does_volunteer_meet_days_required_target(
    volunteer: Volunteer, availability_dict: Dict[Volunteer, DaySelector], days_required: int
):
    days_worked = len(availability_dict[volunteer].days_available())
    meets_requirement = days_worked == days_required

    return meets_requirement


def count_number_of_volunteers_meeting_days_required_target(
    availability_dict: Dict[Volunteer, DaySelector], days_required: int
):
    list_of_volunteers = list(availability_dict.keys())
    count = [
        1
        for volunteer in list_of_volunteers
        if does_volunteer_meet_days_required_target(
            volunteer=volunteer,
            availability_dict=availability_dict,
            days_required=days_required,
        )
    ]

    return len(count)


max_possible_age = 150
age_brackets = [[0, 9], [10, 12], [13, 15], [16, max_possible_age]]


def cadet_has_right_age_and_is_available_on_day(
    cadet: Cadet,
    availability_dict: Dict[Cadet, DaySelector],
    day: Day,
    age_window: List[int],
) -> bool:
    available = availability_dict[cadet].available_on_day(day)
    right_age = cadet_has_right_age(
        cadet=cadet, age_window=age_window
    )

    return available and right_age


def count_cadets_with_right_age(
    cadets_with_food_requirements: DictOfCadetsWithFoodRequirementsAtEvent,
    age_window: List[int],
):
    list_to_count = [
        1
        for cadet in cadets_with_food_requirements.list_of_cadets()
        if cadet_has_right_age(
            cadet=cadet,
            age_window=age_window,
        )
    ]

    return len(list_to_count)


def cadet_has_right_age(
    cadet: Cadet, age_window: List[int]
) -> bool:
    age = cadet.approx_age_years()
    max_age = age_window[1]
    min_age = age_window[0]

    right_age = age >= float(min_age) and age < float(max_age + 1)

    return right_age


def bracket_to_str(age_window: List[int]):
    max_age = age_window[1]
    min_age = age_window[0]

    if max_age == max_possible_age:
        return "%d+" % min_age

    return "%d - %d" % (min_age, max_age)
