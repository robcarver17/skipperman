from typing import Dict

import pandas as pd

from app.data_access.store.object_store import ObjectStore

from app.backend.reporting.rollcall_report.configuration import (
    AdditionalParametersForRollcallReport,
)
from app.backend.reporting.allocation_report.allocation_report import (
    add_club_boat_asterix,
)
from app.objects.events import Event

from app.objects.groups import unallocated_group, Group
from app.objects.cadets import ListOfCadets


def get_dict_of_df_for_reporting_rollcalls_given_event_and_parameters(
    object_store: ObjectStore,
    event: Event,
    additional_parameters: AdditionalParametersForRollcallReport,
) -> Dict[str, pd.DataFrame]:
    dict_of_df = get_dict_of_df_for_reporting_rollcalls_with_flags(
        object_store=object_store,
        event=event,
        include_unallocated_cadets=additional_parameters.include_unallocated_cadets,
        display_full_names=additional_parameters.display_full_names,
        add_asterix_for_club_boats=additional_parameters.add_asterix_for_club_boats,
        include_emergency_contacts=additional_parameters.incude_emergency_contacts,
        include_health_data=additional_parameters.include_health_data,
    )

    return dict_of_df

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import get_dict_of_all_event_info_for_cadets
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets

def get_dict_of_df_for_reporting_rollcalls_with_flags(
        object_store: ObjectStore,    event: Event,
    display_full_names: bool = False,
    include_unallocated_cadets: bool = False,
    add_asterix_for_club_boats: bool = True,
    include_emergency_contacts: bool = True,
    include_health_data: bool = True,
) -> Dict[str, pd.DataFrame]:

    dict_of_all_event_data = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)
    list_of_groups = group_allocations_data.get_list_of_groups_at_event(event)
    if include_unallocated_cadets:
        list_of_groups.append(unallocated_group)

    list_of_df = []
    list_of_cadets_at_event = ListOfCadets([])
    for group in list_of_groups:
        df_with_attendance = get_block_of_df_for_group_at_event(
            dict_of_all_event_data=dict_of_all_event_data,
            group=group,
            list_of_cadets_at_event=list_of_cadets_at_event
        )

        list_of_df.append(df_with_attendance)


    df = pd.concat(list_of_df, axis=0)
    df = add_extra_to_reporting_df(df=df, dict_of_all_event_data=dict_of_all_event_data)

    return {"": df}

def get_block_of_df_for_group_at_event(        dict_of_all_event_data: DictOfAllEventInfoForCadets,
                                       group: Group,
                                               list_of_cadets_at_event: ListOfCadets) -> pd.DataFrame:
    if group is unallocated_group:
        list_of_cadet_ids_with_groups = (
            group_allocations_data.active_cadet_ids_at_event_for_unallocated_cadets(
                event=event
            )
        )
    else:
        list_of_cadet_ids_with_groups = (
            group_allocations_data.active_cadet_ids_with_groups_for_group_at_event(
                event=event, group=group
            )
        )

    list_of_cadets_with_groups = group_allocations_data.get_list_of_cadets_with_group_given_list_of_cadets_with_ids_and_groups(
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups
    )

    if add_asterix_for_club_boats:
        list_of_cadets_with_groups = add_club_boat_asterix(
            object_store=object_store,
            list_of_cadets_with_groups=list_of_cadets_with_groups,
            event=event,
        )

    list_of_cadet_ids_this_group = list_of_cadets_with_groups.list_of_cadet_ids()

    ID = "id"

    df = list_of_cadets_with_groups.as_df_of_str(
        display_full_names=display_full_names
    )
    df = pd.concat(
        [df, pd.DataFrame(list_of_cadet_ids_this_group, columns=[ID])], axis=1
    )
    df = df.drop_duplicates()

    list_of_cadet_ids_this_group = df.pop(ID).values.tolist()

    both_attendance = group_allocations_data.get_joint_attendance_matrix_for_cadet_ids_in_group_at_event(
        event=event, list_of_cadet_ids=list_of_cadet_ids_this_group, group=group
    )

    attendance_data_df = both_attendance.as_pd_data_frame()
    attendance_data_df.index = df.index

    df_with_attendance = pd.concat([df, attendance_data_df], axis=1)

    list_of_cadet_ids += list_of_cadet_ids_this_group

    return df_with_attendance

def add_extra_to_reporting_df(
        df: pd.DataFrame,
        dict_of_all_event_data: DictOfAllEventInfoForCadets,    event: Event,
    include_emergency_contacts: bool = True,
    include_health_data: bool = True,
) -> pd.DataFrame:

    ## add emergency contacts
    if include_emergency_contacts:
        contact_list = (
            cadets_at_event_data.get_emergency_contact_for_list_of_cadet_ids_at_event(
                list_of_cadet_ids=list_of_cadet_ids, event=event
            )
        )
        contact_list_df = pd.DataFrame(contact_list, columns=["Emergency contact"])
        contact_list_df.index = df.index
        df = pd.concat([df, contact_list_df], axis=1)

    ## add health data
    if include_health_data:
        health_list = (
            cadets_at_event_data.get_health_notes_for_list_of_cadet_ids_at_event(
                list_of_cadet_ids=list_of_cadet_ids, event=event
            )
        )
        health_list_df = pd.DataFrame(health_list, columns=["Medical notes"])
        health_list_df.index = df.index
        df = pd.concat([df, health_list_df], axis=1)

    return df

