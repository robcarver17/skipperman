from app.OLD_backend.reporting.all_event_data.all_event_cadet_data import (
    get_df_for_cadets_event_data_dump,
)
from app.OLD_backend.reporting.all_event_data.all_event_clothing_and_food_data import (
    get_df_for_food_event_data_dump,
    get_df_for_clothing_event_data_dump,
)
from app.OLD_backend.reporting.all_event_data.all_event_volunteer_data import (
    get_df_for_volunteers_event_data_dump,
)
from app.OLD_backend.reporting.all_event_data.components import (
    pseudo_reporting_options_for_event_data_dump,
    ROW_ID,
)

from app.OLD_backend.data.mapped_events import MappedEventsData

from app.objects.events import Event

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.reporting.process_stages.create_file_from_list_of_columns import (
    create_csv_report_from_dict_of_df_and_return_filename,
)


def create_csv_event_report_and_return_filename(
    interface: abstractInterface, event: Event
):
    dict_of_df = {}
    dict_of_df["Raw data"] = get_raw_event_data(interface=interface, event=event)
    if event.contains_cadets:
        dict_of_df["Cadets"] = get_df_for_cadets_event_data_dump(
            interface=interface, event=event
        )
    if event.contains_volunteers:
        dict_of_df["Volunteers"] = get_df_for_volunteers_event_data_dump(
            interface=interface, event=event
        )
    if event.contains_food:
        dict_of_df["Food"] = get_df_for_food_event_data_dump(
            interface=interface, event=event
        )
    if event.contains_clothing:
        dict_of_df["Clothing"] = get_df_for_clothing_event_data_dump(
            interface=interface, event=event
        )

    print_options = pseudo_reporting_options_for_event_data_dump(event)
    path_and_filename_with_extension = (
        create_csv_report_from_dict_of_df_and_return_filename(
            dict_of_df=dict_of_df, print_options=print_options
        )
    )

    return path_and_filename_with_extension


def get_raw_event_data(interface: abstractInterface, event: Event):
    mapped_events_data = MappedEventsData(interface.data)
    data = mapped_events_data.get_mapped_wa_event(event)

    df = data.to_df()
    df[ROW_ID] = data.list_of_row_ids()
    df = df.sort_values(ROW_ID)

    return df
