from typing import Dict

import pandas as pd
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData

from app.backend.reporting.rollcall_report.configuration import (
    AdditionalParametersForRollcallReport,
)
from app.backend.reporting.allocation_report.allocation_report import (
    add_club_boat_asterix,
)
from app.objects.events import Event

from app.data_access.storage_layer.store import Store
from app.objects.groups import GROUP_UNALLOCATED

from app.backend.data.group_allocations import GroupAllocationsData
from app.objects.utils import drop_duplicates_in_list_of_ids


def get_dict_of_df_for_reporting_rollcalls_given_event_and_parameters(
    interface: abstractInterface,
    event: Event,
    additional_parameters: AdditionalParametersForRollcallReport,
) -> Dict[str, pd.DataFrame]:
    dict_of_df = get_dict_of_df_for_reporting_rollcalls_with_flags(
        interface=interface,
        event=event,
        include_unallocated_cadets=additional_parameters.include_unallocated_cadets,
        display_full_names=additional_parameters.display_full_names,
        add_asterix_for_club_boats=additional_parameters.add_asterix_for_club_boats,
        include_emergency_contacts=additional_parameters.incude_emergency_contacts,
        include_health_data=additional_parameters.include_health_data,
    )

    return dict_of_df


def get_dict_of_df_for_reporting_rollcalls_with_flags(
    interface: abstractInterface,
    event: Event,
    display_full_names: bool = False,
    include_unallocated_cadets: bool = False,
    add_asterix_for_club_boats: bool = True,
    include_emergency_contacts: bool = True,
    include_health_data: bool = True,
) -> Dict[str, pd.DataFrame]:
    data_api = interface.data
    group_allocations_data = GroupAllocationsData(data_api)
    cadets_at_event_data = CadetsAtEventIdLevelData(data_api)

    list_of_groups = group_allocations_data.get_list_of_groups_at_event(event)
    if include_unallocated_cadets:
        list_of_groups.append(GROUP_UNALLOCATED)

    list_of_df = []
    list_of_cadet_ids = []
    for group in list_of_groups:
        if group is GROUP_UNALLOCATED:
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
                interface=interface,
                list_of_cadets_with_groups=list_of_cadets_with_groups,
                event=event,
            )

        list_of_cadet_ids_this_group = list_of_cadets_with_groups.list_of_cadet_ids()

        ID = "id"

        df = list_of_cadets_with_groups.to_df_of_str(
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

        list_of_df.append(df_with_attendance)
        list_of_cadet_ids += list_of_cadet_ids_this_group

    df = pd.concat(list_of_df, axis=0)

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

    return {"": df}
