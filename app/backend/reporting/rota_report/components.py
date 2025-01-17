import pandas as pd

from app.objects.composed.volunteer_with_group_and_role_at_event import (
    VolunteerWithRoleGroupAndTeamAtEvent,
)
from app.objects.composed.volunteers_with_all_event_data import (
    DictOfAllEventDataForVolunteers,
)
from app.objects.roles_and_teams import Team


from app.backend.reporting.rota_report.configuration import (
    TEAM_NAME,
    ROLE,
    VOLUNTEER,
    GROUP,
    BOAT,
)
from app.objects.groups import unallocated_group


def df_row_for_volunteer_in_role_at_event(
    volunteer_event_data: DictOfAllEventDataForVolunteers,
    team: Team,
    volunteer_with_role_and_group_and_team: VolunteerWithRoleGroupAndTeamAtEvent,
) -> pd.Series:
    team_name_str = team.name
    role_str = get_role_string(volunteer_with_role_and_group_and_team)
    volunteer_name_str = get_volunteer_string(volunteer_with_role_and_group_and_team)
    group_str = get_group_string(volunteer_with_role_and_group_and_team)
    boat_str = get_boat_string(
        volunteer_with_role_and_group_and_team=volunteer_with_role_and_group_and_team,
        volunteer_event_data=volunteer_event_data,
    )

    as_dict = {
        TEAM_NAME: team_name_str,
        ROLE: role_str,
        VOLUNTEER: volunteer_name_str,
        GROUP: group_str,
        BOAT: boat_str,
    }

    return pd.Series(as_dict)


def get_role_string(
    volunteer_with_role_and_group_and_team: VolunteerWithRoleGroupAndTeamAtEvent,
) -> str:
    return volunteer_with_role_and_group_and_team.role.name


def get_volunteer_string(
    volunteer_with_role_and_group_and_team: VolunteerWithRoleGroupAndTeamAtEvent,
) -> str:
    return volunteer_with_role_and_group_and_team.volunteer.name


def get_group_string(
    volunteer_with_role_and_group_and_team: VolunteerWithRoleGroupAndTeamAtEvent,
) -> str:

    requires_group = volunteer_with_role_and_group_and_team.role.associate_sailing_group
    if not requires_group:
        return ""

    group = volunteer_with_role_and_group_and_team.group
    if group is unallocated_group:
        return ""

    return group.name


def get_boat_string(
    volunteer_with_role_and_group_and_team: VolunteerWithRoleGroupAndTeamAtEvent,
    volunteer_event_data: DictOfAllEventDataForVolunteers,
) -> str:
    day = volunteer_with_role_and_group_and_team.day
    volunteer = volunteer_with_role_and_group_and_team.volunteer
    all_volunteers_and_boats = (
        volunteer_event_data.dict_of_volunteers_at_event_with_patrol_boats
    )
    boats = all_volunteers_and_boats.patrol_boats_for_volunteer(volunteer=volunteer)
    boat_on_day = boats.boat_on_day(day, None)

    if boat_on_day is None:
        return ""

    return boat_on_day.name
