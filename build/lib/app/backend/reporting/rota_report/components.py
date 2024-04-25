from dataclasses import dataclass

import pandas as pd

from app.backend.data.volunteer_rota import load_volunteers_in_role_at_event
from app.backend.data.volunteers import DEPRECATE_load_all_volunteers
from app.backend.data.resources import load_list_of_patrol_boats, load_list_of_voluteers_at_event_with_patrol_boats
from app.backend.reporting.rota_report.configuration import TEAM_NAME, ROLE, VOLUNTEER, GROUP, BOAT
from app.objects.constants import missing_data
from app.objects.groups import GROUP_UNALLOCATED
from app.objects.patrol_boats import ListOfPatrolBoats, ListOfVolunteersAtEventWithPatrolBoats
from app.objects.volunteers import ListOfVolunteers
from app.objects.volunteers_in_roles import ListOfVolunteersInRoleAtEvent, VolunteerInRoleAtEventWithTeamName


@dataclass
class DataForDfConstruction:
    all_volunteers: ListOfVolunteers
    all_patrol_boats: ListOfPatrolBoats
    all_volunteers_and_boats: ListOfVolunteersAtEventWithPatrolBoats
    volunteers_in_role_at_event: ListOfVolunteersInRoleAtEvent

    @classmethod
    def construct_for_event(cls, event):
        all_volunteers = DEPRECATE_load_all_volunteers()
        all_patrol_boats = load_list_of_patrol_boats()
        all_volunteers_and_boats = load_list_of_voluteers_at_event_with_patrol_boats(event)
        volunteers_in_role_at_event = load_volunteers_in_role_at_event(event)

        return cls(
            all_volunteers=all_volunteers,
            all_patrol_boats=all_patrol_boats,
            all_volunteers_and_boats=all_volunteers_and_boats,
            volunteers_in_role_at_event=volunteers_in_role_at_event
        )


def df_row_for_volunteer_in_role_at_event(volunteer_in_role_at_event_with_team_name: VolunteerInRoleAtEventWithTeamName, data_for_df: DataForDfConstruction) -> pd.Series:
    team_name_str = get_team_name_string(volunteer_in_role_at_event_with_team_name=volunteer_in_role_at_event_with_team_name)
    role_str = get_role_string(volunteer_in_role_at_event_with_team_name=volunteer_in_role_at_event_with_team_name)
    volunteer_name_str = get_volunteer_string(volunteer_in_role_at_event_with_team_name=volunteer_in_role_at_event_with_team_name, data_for_df=data_for_df)
    group_str = get_group_string(volunteer_in_role_at_event_with_team_name=volunteer_in_role_at_event_with_team_name)
    boat_str = get_boat_string(volunteer_in_role_at_event_with_team_name=volunteer_in_role_at_event_with_team_name, data_for_df=data_for_df)

    as_dict = {TEAM_NAME: team_name_str,
               ROLE: role_str,
               VOLUNTEER: volunteer_name_str,
               GROUP: group_str,
               BOAT: boat_str
               }

    return pd.Series(as_dict)

def get_team_name_string(volunteer_in_role_at_event_with_team_name: VolunteerInRoleAtEventWithTeamName) -> str:
    return volunteer_in_role_at_event_with_team_name.team_name ## not printed

def get_role_string(volunteer_in_role_at_event_with_team_name: VolunteerInRoleAtEventWithTeamName)-> str:
    return  text_given_role(volunteer_in_role_at_event_with_team_name.volunteer_in_role_at_event.role)

def get_volunteer_string(volunteer_in_role_at_event_with_team_name: VolunteerInRoleAtEventWithTeamName, data_for_df: DataForDfConstruction)-> str:
    volunteer_id = volunteer_in_role_at_event_with_team_name.volunteer_in_role_at_event.volunteer_id
    volunteer = data_for_df.all_volunteers.object_with_id(volunteer_id)
    volunteer_name_str = volunteer.name

    return volunteer_name_str

def get_group_string(volunteer_in_role_at_event_with_team_name: VolunteerInRoleAtEventWithTeamName)-> str:
    requires_group = volunteer_in_role_at_event_with_team_name.volunteer_in_role_at_event.requires_group
    if not requires_group:
        return ''

    group = volunteer_in_role_at_event_with_team_name.volunteer_in_role_at_event.group
    if group is GROUP_UNALLOCATED:
        return ''

    group_str = text_given_group(group.group_name)

    return group_str

def get_boat_string(volunteer_in_role_at_event_with_team_name: VolunteerInRoleAtEventWithTeamName, data_for_df: DataForDfConstruction) -> str:

    day = volunteer_in_role_at_event_with_team_name.volunteer_in_role_at_event.day
    all_volunteers_and_boats = data_for_df.all_volunteers_and_boats
    volunteer_id = volunteer_in_role_at_event_with_team_name.volunteer_in_role_at_event.volunteer_id

    boat_id_for_volunteer = all_volunteers_and_boats.which_boat_id_is_volunteer_on_today(day=day,
                                                                                      volunteer_id=volunteer_id)
    if boat_id_for_volunteer is missing_data:
        return ''

    return get_boat_string_if_boat_allocated(boat_id_for_volunteer=boat_id_for_volunteer,
                                             data_for_df=data_for_df)

def get_boat_string_if_boat_allocated(boat_id_for_volunteer: str,
                                     data_for_df: DataForDfConstruction) -> str:

    all_boats = data_for_df.all_patrol_boats
    boat = all_boats.object_with_id(boat_id_for_volunteer)
    boat_name = boat.name

    boat_str = text_given_boat(boat_name)

    return boat_str



def text_given_role(role: str)-> str:
    return role+":"

def text_given_group(group: str) -> str:
    return "- %s" % group

def text_given_boat(boat: str) -> str:
    return "(%s)" % boat

