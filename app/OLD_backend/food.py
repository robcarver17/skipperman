from typing import Dict, List

import pandas as pd
from app.OLD_backend.cadets import cadet_name_from_id

from app.OLD_backend.volunteers.volunteers import get_volunteer_name_from_id

from app.objects.volunteers import ListOfVolunteers

from app.OLD_backend.data.volunteers import VolunteerData

from app.objects.cadets import ListOfCadets

from app.OLD_backend.data.cadets import CadetData

from app.objects.day_selectors import DaySelector, Day

from app.OLD_backend.data.volunteer_allocation import VolunteerAllocationData

from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.OLD_backend.reporting.options_and_parameters.print_options import PrintOptions
from app.OLD_backend.reporting.process_stages.create_file_from_list_of_columns import (
    create_csv_report_from_dict_of_df_and_return_filename,
)

from app.objects.food import (
    FoodRequirements,
    ListOfCadetsWithFoodRequirementsAtEvent,
    CadetWithFoodRequirementsAtEvent,
    VolunteerWithFoodRequirementsAtEvent,
)

from app.OLD_backend.data.food import FoodData
from app.objects.events import Event

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_tables import PandasDFTable


def is_cadet_with_id_already_at_event_with_food(
    interface: abstractInterface, event: Event, cadet_id: str
) -> bool:
    food_data = FoodData(interface.data)
    cadets_with_food = food_data.get_list_of_cadets_with_food_at_event(event)

    return cadet_id in cadets_with_food.list_of_cadet_ids()


def add_new_cadet_with_food_to_event(
    interface: abstractInterface,
    event: Event,
    food_requirements: FoodRequirements,
    cadet_id: str,
):
    food_data = FoodData(interface.data)
    food_data.add_new_cadet_with_food_to_event(
        event=event, cadet_id=cadet_id, food_requirements=food_requirements
    )


def is_volunteer_with_id_already_at_event_with_food(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> bool:
    food_data = FoodData(interface.data)
    volunteers_with_food = food_data.get_list_of_volunteeers_with_food_at_event(event)

    return volunteer_id in volunteers_with_food.list_of_volunteer_ids()


def add_new_volunteer_with_food_to_event(
    interface: abstractInterface,
    event: Event,
    food_requirements: FoodRequirements,
    volunteer_id: str,
):
    food_data = FoodData(interface.data)
    food_data.add_new_volunteer_with_food_to_event(
        event=event, volunteer_id=volunteer_id, food_requirements=food_requirements
    )


def update_cadet_food_data(
    interface: abstractInterface,
    event: Event,
    cadet_id: str,
    new_food_requirements: FoodRequirements,
):
    food_data = FoodData(interface.data)
    food_data.change_food_requirements_for_cadet(
        event=event, cadet_id=cadet_id, food_requirements=new_food_requirements
    )


def update_volunteer_food_data(
    interface: abstractInterface,
    event: Event,
    volunteer_id: str,
    new_food_requirements: FoodRequirements,
):
    food_data = FoodData(interface.data)
    food_data.change_food_requirements_for_volunteer(
        event=event, volunteer_id=volunteer_id, food_requirements=new_food_requirements
    )


def summarise_food_data_by_day(
    interface: abstractInterface, event: Event, copy_index: bool = False
) -> PandasDFTable:
    ## rows: cadets/ volunteers. columns: day and numbers
    row_for_volunteers = summarise_food_data_by_day_for_volunteers(
        interface=interface, event=event
    )
    row_for_cadets = summarise_food_data_by_day_for_cadets(
        interface=interface, event=event
    )

    df = pd.concat([row_for_cadets, row_for_volunteers], axis=0)
    df.loc["Total"] = df.sum(numeric_only=True, axis=0)

    if copy_index:
        df.insert(0, "", df.index)

    return PandasDFTable(df)


def summarise_food_data_by_day_for_cadets(
    interface: abstractInterface, event: Event
) -> pd.DataFrame:
    food_data = FoodData(interface.data)
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    cadet_data = CadetData(interface.data)
    all_cadets = cadet_data.get_list_of_cadets()

    cadets_with_food = food_data.list_of_active_cadets_with_food_at_event(event)
    availability_dict = (
        cadets_at_event_data.get_availability_dict_for_active_cadet_ids_at_event(event)
    )

    summary_over_age_brackets = {}
    for age_window in age_brackets:
        summary_dict = {}

        for day in event.weekdays_in_event():
            list_to_count = [
                1
                for cadet_with_food_requirements in cadets_with_food
                if cadet_has_right_age_and_is_available_on_day(
                    all_cadets=all_cadets,
                    cadet_id=cadet_with_food_requirements.cadet_id,
                    day=day,
                    age_window=age_window,
                    availability_dict=availability_dict,
                )
            ]
            summary_dict[day.name] = sum(list_to_count)

        summary_dict["Count"] = count_cadets_with_right_age(
            cadets_with_food_requirements=cadets_with_food,
            all_cadets=all_cadets,
            age_window=age_window,
        )

        summary_over_age_brackets[
            "Cadet %s" % bracket_to_str(age_window)
        ] = summary_dict

    return pd.DataFrame(summary_over_age_brackets).transpose()


def bracket_to_str(age_window: List[int]):
    max_age = age_window[1]
    min_age = age_window[0]

    if max_age == max_possible_age:
        return "%d+" % min_age

    return "%d - %d" % (min_age, max_age)


max_possible_age = 99
age_brackets = [[0, 9], [10, 12], [13, 15], [16, max_possible_age]]


def cadet_has_right_age_and_is_available_on_day(
    all_cadets: ListOfCadets,
    availability_dict: Dict[str, DaySelector],
    cadet_id: str,
    day: Day,
    age_window: List[int],
) -> bool:
    available = availability_dict[cadet_id].available_on_day(day)
    right_age = cadet_has_right_age(
        all_cadets=all_cadets, cadet_id=cadet_id, age_window=age_window
    )

    return available and right_age


def count_cadets_with_right_age(
    cadets_with_food_requirements: ListOfCadetsWithFoodRequirementsAtEvent,
    all_cadets: ListOfCadets,
    age_window: List[int],
):
    list_to_count = [
        1
        for cadet_with_food_requirements in cadets_with_food_requirements
        if cadet_has_right_age(
            all_cadets=all_cadets,
            cadet_id=cadet_with_food_requirements.cadet_id,
            age_window=age_window,
        )
    ]

    return len(list_to_count)


def cadet_has_right_age(
    all_cadets: ListOfCadets, cadet_id: str, age_window: List[int]
) -> bool:
    age = all_cadets.cadet_with_id(cadet_id=cadet_id).approx_age_years()
    max_age = age_window[1]
    min_age = age_window[0]

    right_age = age >= float(min_age) and age < float(max_age + 1)

    return right_age


def summarise_food_data_by_day_for_volunteers(
    interface: abstractInterface, event: Event
) -> pd.DataFrame:
    food_data = FoodData(interface.data)
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteers_with_food = food_data.list_of_active_volunteers_with_food_at_event(event)
    availability_dict = dict(
        [
            (
                volunteer_id,
                volunteer_allocation_data.get_volunteer_at_this_event(
                    event=event, volunteer_id=volunteer_id
                ).availablity,
            )
            for volunteer_id in volunteers_with_food.list_of_volunteer_ids()
        ]
    )

    range_of_days_worked = list(range(1, len(event.weekdays_in_event()) + 1))
    summary_over_required = {}
    for days_required in range_of_days_worked:
        summary_dict = {}
        for day in event.weekdays_in_event():
            list_to_count = [
                1
                for volunteer_with_food_requirements in volunteers_with_food
                if volunteer_id_is_available_on_day_and_meets_days_required_target(
                    volunteer_id=volunteer_with_food_requirements.volunteer_id,
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


def volunteer_id_is_available_on_day_and_meets_days_required_target(
    volunteer_id: str,
    availability_dict: Dict[str, DaySelector],
    day: Day,
    days_required: int,
):
    available_on_day = availability_dict[volunteer_id].available_on_day(day)
    meets_requirement = does_volunteer_meet_days_required_target(
        volunteer_id=volunteer_id,
        availability_dict=availability_dict,
        days_required=days_required,
    )

    return available_on_day and meets_requirement


def does_volunteer_meet_days_required_target(
    volunteer_id: str, availability_dict: Dict[str, DaySelector], days_required: int
):
    days_worked = len(availability_dict[volunteer_id].days_available())
    meets_requirement = days_worked == days_required

    return meets_requirement


def count_number_of_volunteers_meeting_days_required_target(
    availability_dict: Dict[str, DaySelector], days_required: int
):
    volunteer_ids = list(availability_dict.keys())
    count = [
        1
        for volunteer_id in volunteer_ids
        if does_volunteer_meet_days_required_target(
            volunteer_id=volunteer_id,
            availability_dict=availability_dict,
            days_required=days_required,
        )
    ]

    return len(count)


def download_food_data_and_return_filename(
    interface: abstractInterface, event: Event
) -> str:
    dict_of_df = get_food_data_for_download(interface=interface, event=event)
    print_options = pseudo_reporting_options_for_food_data_export(event)
    path_and_filename_with_extension = (
        create_csv_report_from_dict_of_df_and_return_filename(
            dict_of_df=dict_of_df, print_options=print_options
        )
    )

    return path_and_filename_with_extension


def get_food_data_for_download(
    interface: abstractInterface, event: Event
) -> Dict[str, pd.DataFrame]:
    return dict(
        summary=summarise_food_data_by_day(
            interface=interface, event=event, copy_index=True
        ),
        allergies=get_list_of_allergies_as_df(interface=interface, event=event),
        volunteers=get_list_of_volunteers_with_food_as_df(
            interface=interface, event=event
        ),
        cadets=get_list_of_cadets_with_food_as_df(interface=interface, event=event),
    )


def get_list_of_allergies_as_df(
    interface: abstractInterface, event: Event
) -> pd.DataFrame:
    ## List of allergies by group with total in brackets (pseudo data frame). List includes (Cadet or Volunteer) and if volunteer # of days. For catering.
    food_data = FoodData(interface.data)
    list_of_food_requirements = food_data.get_combined_list_of_food_requirement_items(
        event
    )

    list_of_required_df = []
    for food_required_str in list_of_food_requirements:
        list_of_required_df.append(
            get_allergy_list_as_df_for_cadets_and_volunteers(
                interface=interface, event=event, food_required_str=food_required_str
            )
        )

    return pd.concat(list_of_required_df, axis=0)


def get_allergy_list_as_df_for_cadets_and_volunteers(
    interface: abstractInterface, event: Event, food_required_str: str
):
    volunteer_df = get_allergy_list_as_df_for_volunteers(
        interface=interface, event=event, food_required_str=food_required_str
    )
    cadet_df = get_allergy_list_as_df_for_cadets(
        interface=interface, event=event, food_required_str=food_required_str
    )
    both_df = pd.concat([cadet_df, volunteer_df], axis=0)

    header_line = pd.Series(
        dict(type="", name="%s (%d)" % (food_required_str, len(both_df)))
    )

    return pd.concat([header_line, both_df], axis=0)


def get_allergy_list_as_df_for_volunteers(
    interface: abstractInterface, event: Event, food_required_str: str
):
    food_data = FoodData(interface.data)
    volunteers_with_food = food_data.list_of_active_volunteers_with_food_at_event(event)
    subset = volunteers_with_food.subset_matches_food_required_description(
        food_required_str
    )

    list_of_names = [
        get_volunteer_name_from_id(data_layer=interface.data, volunteer_id=volunteer_id)
        for volunteer_id in subset.list_of_volunteer_ids()
    ]

    df = pd.DataFrame(dict(type=["Volunteer"] * len(list_of_names), name=list_of_names))
    df = df.sort_values("name")

    return df


def get_allergy_list_as_df_for_cadets(
    interface: abstractInterface, event: Event, food_required_str: str
):
    food_data = FoodData(interface.data)
    cadets_with_food = food_data.list_of_active_cadets_with_food_at_event(event)
    subset = cadets_with_food.subset_matches_food_required_description(
        food_required_str
    )

    list_of_names = [
        cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id)
        for cadet_id in subset.list_of_cadet_ids()
    ]

    df = pd.DataFrame(dict(type=["Cadet"] * len(list_of_names), name=list_of_names))
    df = df.sort_values("name")

    return df


def get_list_of_volunteers_with_food_as_df(
    interface: abstractInterface, event: Event
) -> pd.DataFrame:
    ## List of volunteer names grouped by how many days volunteering then alphabetical. List includes # of days. For wristband collection.
    food_data = FoodData(interface.data)
    volunteer_data = VolunteerData(interface.data)
    volunteer_allocation_data = VolunteerAllocationData(interface.data)
    volunteers_with_food = food_data.list_of_active_volunteers_with_food_at_event(event)
    availability_dict = dict(
        [
            (
                volunteer_id,
                volunteer_allocation_data.get_volunteer_at_this_event(
                    event=event, volunteer_id=volunteer_id
                ).availablity,
            )
            for volunteer_id in volunteers_with_food.list_of_volunteer_ids()
        ]
    )

    df = pd.DataFrame(
        [
            row_for_volunteer_in_data(
                availability_dict=availability_dict,
                list_of_volunteers=volunteer_data.get_list_of_volunteers(),
                volunteer_with_food_at_event=volunteer_with_food_at_event,
            )
            for volunteer_with_food_at_event in volunteers_with_food
        ]
    )

    df = df.sort_values("days_available")

    return df


def row_for_volunteer_in_data(
    availability_dict: Dict[str, DaySelector],
    list_of_volunteers: ListOfVolunteers,
    volunteer_with_food_at_event: VolunteerWithFoodRequirementsAtEvent,
) -> pd.Series:
    volunteer = list_of_volunteers.object_with_id(
        volunteer_with_food_at_event.volunteer_id
    )
    return pd.Series(
        dict(
            name=volunteer.name,
            food_requirement=volunteer_with_food_at_event.food_requirements.describe(),
            days_available=len(
                availability_dict[
                    volunteer_with_food_at_event.volunteer_id
                ].days_available()
            ),
        )
    )


def get_list_of_cadets_with_food_as_df(
    interface: abstractInterface, event: Event
) -> pd.DataFrame:
    ## List of cadets for completeness (probably won't be used)
    food_data = FoodData(interface.data)
    cadet_data = CadetData(interface.data)
    all_cadets = cadet_data.get_list_of_cadets()

    cadets_with_food = food_data.list_of_active_cadets_with_food_at_event(event)

    df = pd.DataFrame(
        [
            row_for_cadet_in_table(
                all_cadets=all_cadets,
                cadet_with_food_requirements=cadet_with_food_requirements,
            )
            for cadet_with_food_requirements in cadets_with_food
        ]
    )
    df = df.sort_values("name")

    return df


def row_for_cadet_in_table(
    all_cadets: ListOfCadets,
    cadet_with_food_requirements: CadetWithFoodRequirementsAtEvent,
) -> pd.Series:
    cadet = all_cadets.cadet_with_id(cadet_with_food_requirements.cadet_id)
    return pd.Series(
        dict(
            name=cadet.name,
            age=int(cadet.approx_age_years()),
            food_requirement=cadet_with_food_requirements.food_requirements.describe(),
        )
    )


def pseudo_reporting_options_for_food_data_export(event: Event) -> PrintOptions:
    print_options = PrintOptions(
        filename="food_data_%s" % event.event_name,
        publish_to_public=False,
        output_pdf=False,
    )
    return print_options
