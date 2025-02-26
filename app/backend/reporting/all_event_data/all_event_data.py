from typing import Dict

import pandas as pd

from app.backend.registration_data.raw_mapped_registration_data import (
    get_raw_mapped_registration_data,
)
from app.backend.reporting.all_event_data.all_event_cadet_data import (
    get_df_for_cadets_event_data_dump,
)
from app.backend.reporting.all_event_data.all_event_clothing_and_food_data import (
    get_df_for_food_event_data_dump,
    get_df_for_clothing_event_data_dump,
)
from app.backend.reporting.all_event_data.all_event_volunteer_data import (
    get_df_for_volunteers_event_data_dump,
)
from app.backend.reporting.all_event_data.components import (
    pseudo_reporting_options_for_event_data_dump,
    ROW_ID,
)

from app.data_access.store.object_store import ObjectStore

from app.objects.events import Event

from app.backend.reporting.process_stages.create_file_from_list_of_columns import (
    create_csv_report_from_dict_of_df_and_return_filename,
)


def create_csv_event_report_and_return_filename(
    object_store: ObjectStore, event: Event
):
    dict_of_df = {}
    dict_of_df["Raw data"] = get_raw_event_data(object_store=object_store, event=event)
    dict_of_df["Cadets"] = get_df_for_cadets_event_data_dump(
        object_store=object_store, event=event
    )
    dict_of_df["Volunteers"] = get_df_for_volunteers_event_data_dump(
        object_store=object_store, event=event
    )
    #dict_of_df["Food"] = get_df_for_food_event_data_dump(
    #    object_store=object_store, event=event
    #)
    #dict_of_df["Clothing"] = get_df_for_clothing_event_data_dump(
    #    object_store=object_store, event=event
    #)

    dict_of_df = clear_empty_df_in_dict(dict_of_df)

    print_options = pseudo_reporting_options_for_event_data_dump(event)
    path_and_filename_with_extension = (
        create_csv_report_from_dict_of_df_and_return_filename(
            dict_of_df=dict_of_df, print_options=print_options
        )
    )

    return path_and_filename_with_extension


def clear_empty_df_in_dict(dict_of_df: Dict[str, pd.DataFrame]):
    new_df_dict = dict()
    for tab_name, df in dict_of_df.items():
        if len(df) > 0:
            new_df_dict[tab_name] = df

    return new_df_dict


def get_raw_event_data(object_store: ObjectStore, event: Event) -> pd.DataFrame:
    mapped_events_data = get_raw_mapped_registration_data(
        object_store=object_store, event=event
    )

    df = mapped_events_data.as_df_of_str()
    df[ROW_ID] = mapped_events_data.list_of_row_ids()
    df = df.sort_values(ROW_ID)

    return df
