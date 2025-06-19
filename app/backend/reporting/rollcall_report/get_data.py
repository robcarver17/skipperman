from typing import Dict

import pandas as pd

from app.data_access.store.object_store import ObjectStore

from app.backend.reporting.rollcall_report.configuration import (
    AdditionalParametersForRollcallReport,
    GROUP_NAME_COLUMN_HEADING_FOR_SPOTTER_SHEET,
)
from app.objects.composed.people_at_event_with_club_dinghies import (
    DictOfPeopleAndClubDinghiesAtEvent,
)
from app.objects.events import Event

from app.objects.groups import unallocated_group, Group
from app.objects.cadets import ListOfCadets, Cadet
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
    get_attendance_matrix_for_list_of_cadets_at_event_with_passed_event_info,
)
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets


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


def get_dict_of_df_for_reporting_rollcalls_with_flags(
    object_store: ObjectStore,
    event: Event,
    display_full_names: bool,
    include_unallocated_cadets: bool,
    add_asterix_for_club_boats: bool,
    include_emergency_contacts: bool,
    include_health_data: bool,
) -> Dict[str, pd.DataFrame]:

    dict_of_all_event_data = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event, active_only=True
    )
    list_of_groups = (
        dict_of_all_event_data.dict_of_cadets_with_days_and_groups.all_groups_at_event()
    )
    if include_unallocated_cadets:
        list_of_groups.append(unallocated_group)

    list_of_df = []
    for group in list_of_groups:
        df_with_attendance = get_block_of_df_for_group_at_event(
            dict_of_all_event_data=dict_of_all_event_data,
            group=group,
            add_asterix_for_club_boats=add_asterix_for_club_boats,
            display_full_names=display_full_names,
            include_emergency_contacts=include_emergency_contacts,
            include_health_data=include_health_data,
        )
        list_of_df.append(df_with_attendance)

    df = pd.concat(list_of_df, axis=0)
    print("here")
    print(df)

    return {"Roll call": df}  ## single sheet in spreadsheet


def get_block_of_df_for_group_at_event(
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    group: Group,
    display_full_names: bool,
    add_asterix_for_club_boats: bool,
    include_emergency_contacts: bool,
    include_health_data: bool,
) -> pd.DataFrame:

    list_of_cadets_in_group = dict_of_all_event_data.cadets_in_group_during_event(group)
    list_of_cadets_in_group = list_of_cadets_in_group.sort_by_name()
    df = get_names_and_groups_block_of_df_for_group_at_event(
        dict_of_all_event_data=dict_of_all_event_data,
        list_of_cadets_in_group=list_of_cadets_in_group,
        group=group,
        display_full_names=display_full_names,
        add_asterix_for_club_boats=add_asterix_for_club_boats,
    )

    df = add_attendance_to_rollcall_df(
        df=df,
        dict_of_all_event_data=dict_of_all_event_data,
        list_of_cadets_in_group=list_of_cadets_in_group,
    )

    df = add_extra_to_reporting_df(
        df=df,
        dict_of_all_event_data=dict_of_all_event_data,
        list_of_cadets_in_group=list_of_cadets_in_group,
        include_health_data=include_health_data,
        include_emergency_contacts=include_emergency_contacts,
    )

    return df


def get_names_and_groups_block_of_df_for_group_at_event(
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    group: Group,
    list_of_cadets_in_group: ListOfCadets,
    display_full_names: bool,
    add_asterix_for_club_boats: bool,
) -> pd.DataFrame:

    names_as_series = get_names_as_series_group_at_event(
        dict_of_all_event_data=dict_of_all_event_data,
        list_of_cadets_in_group=list_of_cadets_in_group,
        display_full_names=display_full_names,
        add_asterix_for_club_boats=add_asterix_for_club_boats,
    )
    group_as_series = pd.Series([group.name] * len(names_as_series))
    df = pd.concat([names_as_series, group_as_series], axis=1)
    df.columns = ["Name", GROUP_NAME_COLUMN_HEADING_FOR_SPOTTER_SHEET]

    return df


def get_names_as_series_group_at_event(
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    list_of_cadets_in_group: ListOfCadets,
    display_full_names: bool,
    add_asterix_for_club_boats: bool,
) -> pd.Series:

    if add_asterix_for_club_boats:
        list_of_cadets_in_group_for_names = add_club_boat_asterix_to_list_of_cadets_with_club_boat_on_any_day(
            list_of_cadets=list_of_cadets_in_group,
            dict_of_cadets_at_event_with_club_dinghies=dict_of_all_event_data.dict_of_cadets_and_club_dinghies_at_event,
        )
    else:
        list_of_cadets_in_group_for_names = list_of_cadets_in_group

    if display_full_names:
        list_of_cadet_names = [
            cadet.name for cadet in list_of_cadets_in_group_for_names
        ]
    else:
        list_of_cadet_names = [
            cadet.initial_and_surname for cadet in list_of_cadets_in_group_for_names
        ]

    names_as_series = pd.Series(list_of_cadet_names)

    return names_as_series


def add_club_boat_asterix_to_list_of_cadets_with_club_boat_on_any_day(
    list_of_cadets: ListOfCadets,
    dict_of_cadets_at_event_with_club_dinghies: DictOfPeopleAndClubDinghiesAtEvent,
) -> ListOfCadets:
    return ListOfCadets(
        [
            add_club_boat_asterix_to_cadet_with_club_boat_on_any_day(
                cadet=cadet,
                dict_of_cadets_at_event_with_club_dinghies=dict_of_cadets_at_event_with_club_dinghies,
            )
            for cadet in list_of_cadets
        ]
    )


def add_club_boat_asterix_to_cadet_with_club_boat_on_any_day(
    cadet: Cadet,
    dict_of_cadets_at_event_with_club_dinghies: DictOfPeopleAndClubDinghiesAtEvent,
) -> Cadet:
    has_dinghy = dict_of_cadets_at_event_with_club_dinghies.club_dinghys_for_person(
        cadet
    ).has_any_dinghy_on_any_day()

    if has_dinghy:
        return cadet.add_asterix_to_name()
    else:
        return cadet


def add_attendance_to_rollcall_df(
    df: pd.DataFrame,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    list_of_cadets_in_group: ListOfCadets,
) -> pd.DataFrame:

    attendance = (
        get_attendance_matrix_for_list_of_cadets_at_event_with_passed_event_info(
            all_event_info=dict_of_all_event_data,
            list_of_cadets=list_of_cadets_in_group,
        )
    )
    attendance_data_df = attendance.as_pd_data_frame()
    attendance_data_df.index = df.index

    df_with_attendance = pd.concat([df, attendance_data_df], axis=1)

    return df_with_attendance


def add_extra_to_reporting_df(
    df: pd.DataFrame,
    dict_of_all_event_data: DictOfAllEventInfoForCadets,
    list_of_cadets_in_group: ListOfCadets,
    include_emergency_contacts: bool = True,
    include_health_data: bool = True,
) -> pd.DataFrame:

    ## add emergency contacts
    if include_emergency_contacts:
        contact_list = dict_of_all_event_data.dict_of_cadets_with_registration_data.get_emergency_contact_for_list_of_cadets_at_event(
            list_of_cadets_in_group
        )
        contact_list_df = pd.DataFrame(contact_list, columns=["Emergency contact"])
        contact_list_df.index = df.index
        df = pd.concat([df, contact_list_df], axis=1)

    ## add health data
    if include_health_data:
        health_list = dict_of_all_event_data.dict_of_cadets_with_registration_data.get_health_notes_for_list_of_cadets_at_event(
            list_of_cadets_in_group
        )
        health_list_df = pd.DataFrame(health_list, columns=["Medical notes"])
        health_list_df.index = df.index
        df = pd.concat([df, health_list_df], axis=1)

    return df
