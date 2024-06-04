from typing import List, Dict

import pandas as pd
from app.backend.data.dinghies import DinghiesData

from app.backend.data.group_allocations import GroupAllocationsData

from app.objects.utils import we_are_not_the_same

from app.objects.mapped_wa_event import RegistrationStatus, empty_status

from app.objects.day_selectors import DaySelector, Day, EMPTY_DAY_SELECTOR

from app.objects.cadet_at_event import IdentifiedCadetAtEvent

from app.backend.cadets import cadet_name_from_id

from app.backend.data.cadets import CadetData

from app.backend.data.cadets_at_event import CadetsAtEventData

from app.backend.data.mapped_events import MappedEventsData

from app.backend.reporting.options_and_parameters.print_options import PrintOptions

from app.objects.events import Event

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.reporting.options_and_parameters.report_options import ReportingOptions
from app.backend.reporting.process_stages.create_file_from_list_of_columns import create_csv_report_from_dict_of_df_and_return_filename
from app.data_access.xls_and_csv import save_dict_of_df_as_spreadsheet_file


def create_csv_event_report_and_return_filename(
        interface: abstractInterface,
        event: Event
):
    dict_of_df = {}
    dict_of_df['Raw data'] = get_raw_event_data(interface=interface, event=event)
    if event.contains_cadets:
        dict_of_df['Cadets'] = get_df_for_cadets_event_data_dump(interface=interface, event=event)
    if event.contains_volunteers:
        dict_of_df['Volunteers'] = get_df_for_volunteers_event_data_dump(interface=interface, event=event)
    if event.contains_food:
        dict_of_df['Food'] = get_df_for_food_event_data_dump(interface=interface, event=event)
    if event.contains_clothing:
        dict_of_df['Clothing'] = get_df_for_clothing_event_data_dump(interface=interface, event=event)

    print_options = pseudo_reporting_options_for_event_data_dump(event)
    path_and_filename_with_extension = create_csv_report_from_dict_of_df_and_return_filename(dict_of_df=dict_of_df,
                                                                                             print_options=print_options)

    return path_and_filename_with_extension

def pseudo_reporting_options_for_event_data_dump(event: Event) -> PrintOptions:

    print_options = PrintOptions(filename='event_data_%s' % event.event_name,
                                 publish_to_public=False,
                                 output_pdf=False)

    return print_options

ROW_ID = 'row_id'

def get_raw_event_data(
        interface: abstractInterface,
        event: Event
):
    mapped_events_data = MappedEventsData(interface.data)
    data = mapped_events_data.get_mapped_wa_event(event)

    df = data.to_df()
    df[ROW_ID] = data.list_of_row_ids()
    df = df.sort_values(ROW_ID)

    return df

def get_df_for_cadets_event_data_dump(
        interface: abstractInterface,
        event: Event
):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    list_of_identified_cadets =cadets_at_event_data.get_list_of_identified_cadets_at_event(event)
    list_of_row_ids = [identified_cadet.row_id for identified_cadet in list_of_identified_cadets]
    list_of_cadet_names = [cadet_name_or_test(interface=interface,identified_cadet=identified_cadet) for identified_cadet in list_of_identified_cadets]
    list_of_cadet_ids = [identified_cadet.cadet_id for identified_cadet in list_of_identified_cadets]

    list_of_availability = [data_from_cadets_at_event_data_or_empty(interface=interface, event=event, cadet_id=cadet_id, keyname='availability', default=EMPTY_DAY_SELECTOR).days_available_as_str()
                            for cadet_id in list_of_cadet_ids]

    list_of_status = [data_from_cadets_at_event_data_or_empty(interface=interface, event=event, cadet_id=cadet_id, keyname='status', default=empty_status).name
                            for cadet_id in list_of_cadet_ids]
    list_of_notes = [data_from_cadets_at_event_data_or_empty(interface=interface, event=event, cadet_id=cadet_id, keyname='notes')
                            for cadet_id in list_of_cadet_ids]
    list_of_health = [data_from_cadets_at_event_data_or_empty(interface=interface, event=event, cadet_id=cadet_id, keyname='health')
                            for cadet_id in list_of_cadet_ids]
    list_of_club_dinghy = [club_dinghy_for_cadet(interface=interface, event=event, cadet_id=cadet_id)
                           for cadet_id in list_of_cadet_ids]

    df = pd.DataFrame({ROW_ID: list_of_row_ids,
                         'Cadet': list_of_cadet_names,
                       'Status': list_of_status,
                       'Attendance': list_of_availability,
                       'Notes': list_of_notes,
                       'Health': list_of_health,
                       'Club dinghy': list_of_club_dinghy})

    if event.contains_groups:
        list_of_groups = [group_string_for_cadet(interface=interface, event=event, cadet_id=cadet_id) for cadet_id in list_of_cadet_ids]
        list_of_groups = pd.DataFrame(list_of_groups, columns=['Group'])
        df = pd.concat([df, list_of_groups], axis=1)

    df = df.sort_values(ROW_ID)

    return df

def data_from_cadets_at_event_data_or_empty(interface: abstractInterface, event: Event, cadet_id: str, keyname: str, default=''):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    list_of_cadets_at_event = cadets_at_event_data.get_list_of_cadets_at_event(event)
    if not cadet_id in list_of_cadets_at_event.list_of_cadet_ids():
        return default

    return getattr(list_of_cadets_at_event.cadet_at_event(cadet_id), keyname)

def group_string_for_cadet(interface: abstractInterface, event: Event, cadet_id:str):
    group_data = GroupAllocationsData(interface.data)

    day_item_dict= dict([(day, group_data.get_list_of_cadet_ids_with_groups_at_event(event).group_for_cadet_id_on_day(day=day, cadet_id=cadet_id).group_name) for day in event.weekdays_in_event()])

    return day_item_dict_as_string_or_single_if_identical(day_item_dict)


def club_dinghy_for_cadet(interface: abstractInterface, event: Event, cadet_id: str):
    dinghy_data =DinghiesData(interface.data)
    day_item_dict= dict([(day, dinghy_data.name_of_club_dinghy_for_cadet_at_event_on_day_or_default(event=event, cadet_id=cadet_id, day=day)) for day in event.weekdays_in_event()])

    return day_item_dict_as_string_or_single_if_identical(day_item_dict)


def boat_class_for_cadet(interface: abstractInterface, event: Event, cadet_id: str):
    dinghy_data =DinghiesData(interface.data)
    list_at_event = dinghy_data.get_list_of_cadets_at_event_with_dinghies(event)

    #day_item_dict= dict([(day, dinghy_data.name_of_club_dinghy_for_cadet_at_event_on_day_or_default(event=event, cadet_id=cadet_id, day=day)) for day in event.weekdays_in_event()])

    #return day_item_dict_as_string_or_single_if_identical(day_item_dict)

def sail_number_for_cadet(interface: abstractInterface, event: Event, cadet_id: str):
    dinghy_data =DinghiesData(interface.data)


def partner_name_for_cadet(interface: abstractInterface, event: Event, cadet_id: str):
    dinghy_data =DinghiesData(interface.data)


def names_of_volunteers_for_cadet(interface: abstractInterface, event: Event, cadet_id: str):
    pass

def day_item_dict_as_string_or_single_if_identical(day_item_dict: Dict[Day,str]) -> str:
    if len(day_item_dict)==0:
        return ''
    all_values = list(day_item_dict.values())
    if we_are_not_the_same(all_values):
        items_as_list_of_str = ["%s:%s" % (day.name, item) for day,item in day_item_dict.items()]
        return ", ".join(items_as_list_of_str)
    else:
        return all_values[0] ## all the same

def cadet_name_or_test(interface: abstractInterface, identified_cadet: IdentifiedCadetAtEvent):
    if identified_cadet.is_test_cadet:
        return "Test"
    return cadet_name_from_id(interface=interface, cadet_id=identified_cadet.cadet_id)


def get_df_for_volunteers_event_data_dump(
        interface: abstractInterface,
        event: Event
):
    return pd.DataFrame()

def get_df_for_food_event_data_dump(
        interface: abstractInterface,
        event: Event
):
    return pd.DataFrame()

def get_df_for_clothing_event_data_dump(
        interface: abstractInterface,
        event: Event
):
    return pd.DataFrame()
