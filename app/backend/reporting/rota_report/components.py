from dataclasses import dataclass

import pandas as pd
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.reporting.rota_report.configuration import TEAM_NAME, ROLE, VOLUNTEER, GROUP, BOAT
from app.objects.constants import missing_data
from app.objects.groups import GROUP_UNALLOCATED
from app.objects.patrol_boats import ListOfPatrolBoats, ListOfVolunteersAtEventWithPatrolBoats
from app.objects.volunteers import ListOfVolunteers
from app.objects.volunteers_in_roles import ListOfVolunteersInRoleAtEvent, VolunteerInRoleAtEventWithTeamName

from app.backend.data.resources import PatrolBoatsData
from app.backend.data.volunteers import VolunteerData
from app.backend.data.volunteer_rota import VolunteerRotaData

@dataclass
class DataForDfConstruction:
    all_volunteers: ListOfVolunteers
    all_patrol_boats: ListOfPatrolBoats
    all_volunteers_and_boats: ListOfVolunteersAtEventWithPatrolBoats
    volunteers_in_role_at_event: ListOfVolunteersInRoleAtEvent

    @classmethod
    def construct_for_event(cls, event, interface: abstractInterface):
        volunteer_data = VolunteerData(interface.data)
        patrol_boat_data = PatrolBoatsData(interface.data)
        volunteers_in_role = VolunteerRotaData(interface.data)

        all_volunteers = volunteer_data.get_list_of_volunteers()
        all_patrol_boats = patrol_boat_data.get_list_of_patrol_boats()
        all_volunteers_and_boats = patrol_boat_data.get_list_of_voluteers_at_event_with_patrol_boats(event)
        volunteers_in_role_at_event = volunteers_in_role.get_list_of_volunteers_in_roles_at_event(event)

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
    return  volunteer_in_role_at_event_with_team_name.volunteer_in_role_at_event.role

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

    return group.group_name

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

    return boat_name



