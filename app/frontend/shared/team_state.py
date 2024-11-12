from app.objects.roles_and_teams import Team

from app.backend.volunteers.roles_and_teams import (
    get_team_from_list_of_given_name_of_team,
    get_team_from_id,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface

TEAM = "team"


def update_state_for_specific_team_given_team_as_str(
    interface: abstractInterface, team_selected: str
):
    team = get_team_from_list_of_given_name_of_team(
        object_store=interface.object_store, team_selected=team_selected
    )
    print("STATE FOR TEAM %s %s" % (str(team), team.id))
    update_state_with_team_id(interface=interface, team_id=team.id)


def update_state_with_team_id(interface: abstractInterface, team_id: str):
    interface.set_persistent_value(key=TEAM, value=team_id)


def get_team_from_state(interface: abstractInterface) -> Team:
    team_id = get_team_id_selected_from_state(interface)
    team = get_team_from_id(object_store=interface.object_store, team_id=team_id)
    print("GET STATE FOR TEAM %s %s" % (str(team), team.id))

    return team


def get_team_id_selected_from_state(interface: abstractInterface) -> str:
    return str(interface.get_persistent_value(TEAM))
