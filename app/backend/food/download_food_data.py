from typing import Dict, List

import pandas as pd

from app.backend.reporting.options_and_parameters.print_options import PrintOptions
from app.backend.reporting.process_stages.create_file_from_list_of_columns import (
    create_csv_report_from_dict_of_df_and_return_filename,
)
from app.data_access.store.object_store import ObjectStore

from app.backend.food.summarise_food import summarise_food_data_by_day
from app.objects.cadets import Cadet
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects.food import FoodRequirements
from app.objects.volunteers import Volunteer

from app.backend.food.active_cadets_and_volunteers_with_food import (
    get_dict_of_active_volunteers_with_food_requirements_at_event,
    get_dict_of_active_cadets_with_food_requirements_at_event,
)


def download_food_data_and_return_filename(
    object_store: ObjectStore, event: Event
) -> str:
    dict_of_df = get_food_data_for_download(object_store=object_store, event=event)
    print_options = pseudo_reporting_options_for_food_data_export(event)
    path_and_filename_with_extension = (
        create_csv_report_from_dict_of_df_and_return_filename(
            dict_of_df=dict_of_df, print_options=print_options
        )
    )

    return path_and_filename_with_extension


def get_food_data_for_download(
    object_store: ObjectStore, event: Event
) -> Dict[str, pd.DataFrame]:
    return dict(
        summary=summarise_food_data_by_day(
            object_store=object_store, event=event, copy_index=True
        ),
        allergies=get_list_of_allergies_as_df(object_store=object_store, event=event),
        volunteers=get_list_of_volunteers_with_food_as_df(
            object_store=object_store, event=event
        ),
        cadets=get_list_of_cadets_with_food_as_df(
            object_store=object_store, event=event
        ),
    )


def get_list_of_allergies_as_df(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:
    ## List of allergies by group with total in brackets (pseudo data frame). List includes (Cadet or Volunteer) and if volunteer # of days. For catering.
    list_of_food_requirements = get_combined_list_of_food_requirement_items(
        object_store=object_store, event=event
    )

    list_of_required_df = []
    for food_required in list_of_food_requirements:
        list_of_required_df.append(
            get_allergy_list_as_df_for_cadets_and_volunteers(
                object_store=object_store,
                event=event,
                specific_food_required=food_required,
            )
        )

    return pd.concat(list_of_required_df, axis=0)


def get_combined_list_of_food_requirement_items(
    object_store: ObjectStore, event: Event
) -> List[FoodRequirements]:
    cadet_food_requirements = get_dict_of_active_cadets_with_food_requirements_at_event(
        object_store=object_store, event=event
    )
    list_of_requirements_for_cadets = (
        cadet_food_requirements.unique_list_of_food_requirements()
    )

    volunteer_food_requirements = (
        get_dict_of_active_volunteers_with_food_requirements_at_event(
            object_store=object_store, event=event
        )
    )
    list_of_requirements_for_volunteers = (
        volunteer_food_requirements.unique_list_of_food_requirements()
    )

    return list(
        set(list_of_requirements_for_volunteers + list_of_requirements_for_cadets)
    )


def get_allergy_list_as_df_for_cadets_and_volunteers(
    object_store: ObjectStore, event: Event, specific_food_required: FoodRequirements
):
    volunteer_df = get_allergy_list_as_df_for_volunteers(
        object_store=object_store,
        event=event,
        specific_food_required=specific_food_required,
    )
    cadet_df = get_allergy_list_as_df_for_cadets(
        object_store=object_store,
        event=event,
        specific_food_required=specific_food_required,
    )
    both_df = pd.concat([cadet_df, volunteer_df], axis=0)

    header_line = pd.Series(
        dict(
            type="", name="%s (%d)" % (specific_food_required.describe(), len(both_df))
        )
    )

    return pd.concat([header_line, both_df], axis=0)


def get_allergy_list_as_df_for_volunteers(
    object_store: ObjectStore, event: Event, specific_food_required: FoodRequirements
):
    volunteer_food_requirements = (
        get_dict_of_active_volunteers_with_food_requirements_at_event(
            object_store=object_store, event=event
        )
    )
    subset = volunteer_food_requirements.subset_matches_food_required_description(
        specific_food_required
    )

    list_of_names = subset.list_of_volunteers()

    df = pd.DataFrame(dict(type=["Volunteer"] * len(list_of_names), name=list_of_names))
    df = df.sort_values("name")

    return df


def get_allergy_list_as_df_for_cadets(
    object_store: ObjectStore, event: Event, specific_food_required: FoodRequirements
):
    cadet_food_requirements = get_dict_of_active_cadets_with_food_requirements_at_event(
        object_store=object_store, event=event
    )
    subset = cadet_food_requirements.subset_matches_food_required_description(
        specific_food_required
    )

    list_of_names = subset.list_of_cadets()

    df = pd.DataFrame(dict(type=["Cadet"] * len(list_of_names), name=list_of_names))
    df = df.sort_values("name")

    return df


from app.backend.registration_data.volunteer_registration_data import (
    get_availability_dict_for_volunteers_at_event,
)


def get_list_of_volunteers_with_food_as_df(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:
    ## List of volunteer names grouped by how many days volunteering then alphabetical. List includes # of days. For wristband collection.
    volunteers_with_food = (
        get_dict_of_active_volunteers_with_food_requirements_at_event(
            object_store=object_store, event=event
        )
    )
    availability_dict = get_availability_dict_for_volunteers_at_event(
        object_store=object_store, event=event
    )

    df = pd.DataFrame(
        [
            row_for_volunteer_in_data(
                volunteer=volunteer,
                availability_dict=availability_dict,
                food_required=food_required,
            )
            for volunteer, food_required in volunteers_with_food.items()
        ]
    )

    df = df.sort_values("days_available")

    return df


def row_for_volunteer_in_data(
    volunteer: Volunteer,
    availability_dict: Dict[Volunteer, DaySelector],
    food_required: FoodRequirements,
) -> pd.Series:
    availability_for_volunteer = availability_dict[volunteer]

    return pd.Series(
        dict(
            name=volunteer.name,
            food_requirement=food_required.describe(),
            days_available=availability_for_volunteer.days_available(),
        )
    )


def get_list_of_cadets_with_food_as_df(
    object_store: ObjectStore, event: Event
) -> pd.DataFrame:
    cadets_with_food = get_dict_of_active_cadets_with_food_requirements_at_event(
        object_store=object_store, event=event
    )

    df = pd.DataFrame(
        [
            row_for_cadet_in_table(cadet=cadet, food_requirements=food_requirements)
            for cadet, food_requirements in cadets_with_food.items()
        ]
    )
    df = df.sort_values("name")

    return df


def row_for_cadet_in_table(
    cadet: Cadet, food_requirements: FoodRequirements
) -> pd.Series:

    return pd.Series(
        dict(
            name=cadet.name,
            age=int(cadet.approx_age_years()),
            food_requirement=food_requirements.describe(),
        )
    )


def pseudo_reporting_options_for_food_data_export(event: Event) -> PrintOptions:
    print_options = PrintOptions(
        filename="food_data_%s" % event.event_name,
        publish_to_public=False,
        output_pdf=False,
    )
    return print_options
