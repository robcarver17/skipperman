from typing import Dict, List, Tuple

import pandas as pd

from app.backend.reporting.rota_report.teams import sort_df_by_role
from app.data_access.store.object_store import ObjectStore

from app.backend.reporting.patrol_boat_report.configuration import (
    BOAT,
    GROUP, LOCATIONS, LOCATION, DESIGNATION, VOLUNTEER
)
from app.backend.reporting.rota_report.configuration import ROLE
from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_all_event_data_for_volunteers,
)
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    RoleAndGroupAndTeam,
)
from app.objects.composed.volunteers_with_all_event_data import (
    DictOfAllEventDataForVolunteers,
)

from app.objects.day_selectors import DaySelector, Day
from app.objects.events import Event
from app.objects.groups import unallocated_group
from app.objects.patrol_boats import ListOfPatrolBoats, PatrolBoat
from app.objects.volunteers import ListOfVolunteers, Volunteer


def get_df_for_reporting_patrol_boats_with_flags(
    object_store: ObjectStore,
    event: Event,
    days_to_show: DaySelector,
) -> Dict[str, pd.DataFrame]:
    volunteer_event_data = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )

    list_of_days = days_to_show.align_with_list_of_days(
        event.days_in_event()
    ).days_available()

    dict_of_df = dict(
        [
            (
                day.name,
                get_and_transform_df_for_reporting_patrol_boats_for_day(
                    volunteer_event_data=volunteer_event_data,
                    day=day,
                ),
            )
            for day in list_of_days
        ]
    )

    dict_of_df_excluding_empty = dict(
        [(day_name, df) for day_name, df in dict_of_df.items() if len(df) > 0]
    )

    print("days in dict %s" % str(dict_of_df_excluding_empty.keys()))

    return dict_of_df_excluding_empty


def get_and_transform_df_for_reporting_patrol_boats_for_day(
    day: Day,
    volunteer_event_data: DictOfAllEventDataForVolunteers,
) -> pd.DataFrame:
    df_for_reporting_volunteers_for_day = get_df_for_reporting_patrol_boats_for_day(
        day=day, volunteer_event_data=volunteer_event_data
    )
    if len(df_for_reporting_volunteers_for_day) == 0:
        return pd.DataFrame()

    df_for_reporting_volunteers_for_day = apply_sorts_and_transforms_to_df(
        df_for_reporting_volunteers_for_day=df_for_reporting_volunteers_for_day,
    )

    return df_for_reporting_volunteers_for_day


def get_df_for_reporting_patrol_boats_for_day(
    day: Day, volunteer_event_data: DictOfAllEventDataForVolunteers
) -> pd.DataFrame:
    list_of_locations = LOCATIONS
    list_of_team_df = []
    for location in list_of_locations:
        team_df = get_df_for_location_on_day(
            volunteer_event_data=volunteer_event_data,
            location=location,
            day=day,
        )

        list_of_team_df.append(team_df)

    if len(list_of_team_df)==0:
        return pd.DataFrame()

    concat_df = pd.concat(list_of_team_df, axis=0)

    return concat_df


def get_df_for_location_on_day(
    volunteer_event_data: DictOfAllEventDataForVolunteers, location:str, day: Day
) -> pd.DataFrame:
    boat_designations = unique_list_of_boat_designations_for_event_on_day(volunteer_event_data=volunteer_event_data, day=day)
    all_df = [get_df_for_designation_and_location_on_day(volunteer_event_data=volunteer_event_data,
                                                         location=location,
                                                         designation=designation,
                                                         day=day) for designation in boat_designations]

    if len(all_df)==0:
        return pd.DataFrame()

    df = pd.concat(all_df, axis=0)

    return df

def get_df_for_designation_and_location_on_day(    volunteer_event_data: DictOfAllEventDataForVolunteers,
                                                   location:str,
                                                   day: Day,
                                                   designation: str):

    list_of_relevant_boats = boats_in_location_and_designation(volunteer_event_data=volunteer_event_data,
                                                               day=day,
                                                               location=location, designation=designation)

    all_df = [get_df_for_designation_and_location_and_boat_on_day(
        volunteer_event_data=volunteer_event_data,
        day=day,
        boat=boat,
        location=location,
        designation=designation
    ) for boat in list_of_relevant_boats]

    if len(all_df)==0:
        return pd.DataFrame()

    df = pd.concat(all_df, axis=0)

    return df

def get_df_for_designation_and_location_and_boat_on_day(    volunteer_event_data: DictOfAllEventDataForVolunteers, day: Day, boat: PatrolBoat,
                                                            location: str, designation: str):
    list_of_volunteers_with_roles_and_groups = get_list_of_volunteers_with_roles_and_groups(
        volunteer_event_data=volunteer_event_data,
        day=day,
        boat=boat
    )
    all_rows = [get_row_for_volunteer_on_boat_on_day(
        volunteer=volunteer,
        role_and_group=role_and_group,
        boat=boat,
        location=location,
        designation=designation
    ) for volunteer, role_and_group in list_of_volunteers_with_roles_and_groups]

    as_df= pd.DataFrame(all_rows)
    if len(as_df)==0:
        return pd.DataFrame()

    as_df = sort_df_by_role(
        df_for_reporting_volunteers_for_day=as_df,
        volunteer_event_data=volunteer_event_data,

    )


    return as_df


def get_list_of_volunteers_with_roles_and_groups(volunteer_event_data: DictOfAllEventDataForVolunteers, day: Day, boat: PatrolBoat)\
        -> List[Tuple[Volunteer, RoleAndGroupAndTeam]]:
    list_of_volunteers = get_volunteers_on_boat_on_day(
        volunteer_event_data=volunteer_event_data,
        day=day,
        boat=boat
    )

    list_of_volunteers_with_roles_and_groups = [(volunteer,
                                                 volunteer_event_data.dict_of_volunteers_at_event_with_days_and_roles.days_and_roles_for_volunteer(volunteer).role_and_group_and_team_on_day(day))
                                                for volunteer in list_of_volunteers]

    return list_of_volunteers_with_roles_and_groups

def get_row_for_volunteer_on_boat_on_day(    volunteer: Volunteer,
                                             role_and_group: RoleAndGroupAndTeam,
                                             boat: PatrolBoat,
                                             location: str, designation: str
                                             ):
    return {
        LOCATION: location,
        DESIGNATION: designation,
        BOAT: boat.name,
        VOLUNTEER: volunteer.name,
        ROLE: role_and_group.role.name,
        GROUP: get_group_string(role_and_group)
    }




def get_group_string(
    role_and_group: RoleAndGroupAndTeam
) -> str:

    requires_group = role_and_group.role.associate_sailing_group
    if not requires_group:
        return ""

    group = role_and_group.group
    if group is unallocated_group:
        return ""

    return group.name



def get_volunteers_on_boat_on_day( volunteer_event_data: DictOfAllEventDataForVolunteers, day: Day, boat: PatrolBoat) -> ListOfVolunteers:
    return volunteer_event_data.dict_of_volunteers_at_event_with_patrol_boats.volunteers_assigned_to_boat_on_day(patrol_boat=boat,
                                                                                                          day=day)

def boats_in_location_and_designation(volunteer_event_data: DictOfAllEventDataForVolunteers, day: Day, location:str, designation: str) -> ListOfPatrolBoats:
    get_label_function = volunteer_event_data.dict_of_volunteers_at_event_with_patrol_boats.label_for_boat_at_event_on_day
    dict_of_boats_and_locations = volunteer_event_data.dict_of_volunteers_at_event_with_patrol_boats.get_dict_of_patrol_boats_with_locations()
    list_of_boats = [boat for boat, location_of_boat in dict_of_boats_and_locations.items()
                     if location_of_boat==location and get_label_function(patrol_boat=boat, day=day)==designation]

    return ListOfPatrolBoats(list_of_boats)

def unique_list_of_boat_designations_for_event_on_day(volunteer_event_data: DictOfAllEventDataForVolunteers, day: Day):
    return volunteer_event_data.dict_of_volunteers_at_event_with_patrol_boats.unique_set_of_labels_at_event(day=day)

def apply_sorts_and_transforms_to_df(
    df_for_reporting_volunteers_for_day: pd.DataFrame,
):

    df_for_reporting_volunteers_for_day = apply_textual_transforms_to_df(
        df_for_reporting_volunteers_for_day=df_for_reporting_volunteers_for_day
    )

    return df_for_reporting_volunteers_for_day



def apply_textual_transforms_to_df(df_for_reporting_volunteers_for_day: pd.DataFrame):
    df_for_reporting_volunteers_for_day[ROLE] = df_for_reporting_volunteers_for_day[
        ROLE
    ].apply(text_given_role)
    df_for_reporting_volunteers_for_day[GROUP] = df_for_reporting_volunteers_for_day[
        GROUP
    ].apply(text_given_group)

    return df_for_reporting_volunteers_for_day


def text_given_role(role: str) -> str:
    if len(role) == 0:
        return ""
    return role + ":"


def text_given_group(group: str) -> str:
    if len(group) == 0:
        return ""
    return "- %s" % group

