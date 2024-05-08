from typing import Dict

import pandas as pd
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.cadets_at_event import CadetsAtEventData

from app.backend.reporting.rollcall_report.configuration import AdditionalParametersForRollcallReport
from app.backend.reporting.allocation_report.allocation_report import add_club_boat_asterix
from app.objects.events import Event

from app.data_access.storage_layer.api import DataLayer
from app.data_access.storage_layer.store import Store

from app.backend.data.group_allocations import GroupAllocationsData

store = Store()

def get_dict_of_df_for_reporting_rollcalls_given_event_and_parameters(interface: abstractInterface,
    event: Event, additional_parameters: AdditionalParametersForRollcallReport)->  Dict[str, pd.DataFrame]:
    dict_of_df = get_dict_of_df_for_reporting_rollcalls_with_flags(
        interface=interface,
        event=event,
        include_unallocated_cadets=additional_parameters.include_unallocated_cadets,
        display_full_names=additional_parameters.display_full_names,
        add_asterix_for_club_boats=additional_parameters.add_asterix_for_club_boats,
        include_emergency_contacts=additional_parameters.incude_emergency_contacts,
        include_health_data = additional_parameters.include_health_data
    )

    return dict_of_df


def get_dict_of_df_for_reporting_rollcalls_with_flags(
    interface: abstractInterface,
    event: Event,
    display_full_names: bool = False,
    include_unallocated_cadets: bool = False,
    add_asterix_for_club_boats: bool = True,
    include_emergency_contacts: bool = True,
        include_health_data: bool = True
) -> Dict[str, pd.DataFrame]:

    data_api = interface.data
    group_allocations = GroupAllocationsData(data_api)
    cadets_at_event_data = CadetsAtEventData(data_api)

    list_of_cadets_with_groups = group_allocations.get_list_of_cadets_with_group_at_event(event=event, include_unallocated_cadets=include_unallocated_cadets)
    if add_asterix_for_club_boats:
        list_of_cadets_with_groups = add_club_boat_asterix(interface=interface, list_of_cadets_with_groups=list_of_cadets_with_groups, event=event)

    df = list_of_cadets_with_groups.to_df_of_str(display_full_names=display_full_names)

    ## add availabilty
    list_of_cadets = list_of_cadets_with_groups.list_of_cadets()
    list_of_cadet_ids = list_of_cadets.list_of_ids
    attendance_data = cadets_at_event_data.get_attendance_matrix_for_list_of_cadet_ids_at_event(event=event,
        list_of_cadet_ids=list_of_cadet_ids)
    attendance_data_df = attendance_data.as_pd_data_frame()

    df = pd.concat([df, attendance_data_df], axis=1)

    ## add emergency contacts
    if include_emergency_contacts:
        contact_list = cadets_at_event_data.get_emergency_contact_for_list_of_cadet_ids_at_event(list_of_cadet_ids=list_of_cadet_ids, event=event)
        contact_list_df = pd.DataFrame(contact_list, columns = ["Emergency contact"])
        df = pd.concat([df, contact_list_df], axis=1)

    ## add health data
    if include_health_data:
        health_list = cadets_at_event_data.get_health_notes_for_list_of_cadet_ids_at_event(list_of_cadet_ids=list_of_cadet_ids, event=event)
        health_list_df = pd.DataFrame(health_list, columns=['Medical notes'])
        df = pd.concat([df, health_list_df], axis=1)

    print(df)

    return {"": df}
