from typing import List

from app.objects.composed.roles_and_teams import DictOfTeamsWithRoles

from app.data_access.store.object_definitions import (
    object_definition_for_list_of_teams,
    object_definition_for_list_of_roles_with_skill_ids,
    object_definition_for_list_of_roles_with_skills,
    object_definition_for_dict_of_teams_with_roles,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.composed.volunteer_roles import ListOfRolesWithSkills, RoleWithSkills

from app.objects.roles_and_teams import ListOfTeams, ListOfRolesWithSkillIds, Team


def reorder_roles_for_team_given_list_of_names(
    object_store: ObjectStore, new_order_of_role_names: List[str], team: Team
):
    dict_of_teams_and_role = get_dict_of_teams_and_roles(object_store)
    dict_of_teams_and_role.reorder_roles_for_team_given_list_of_names(
        team=team, new_order_of_role_names=new_order_of_role_names
    )
    update_dict_of_teams_and_roles(
        object_store=object_store, dict_of_teams_and_roles=dict_of_teams_and_role
    )


def add_new_named_role_to_team(
    object_store: ObjectStore, team: Team, new_role_name: str
):
    dict_of_teams_and_role = get_dict_of_teams_and_roles(object_store)
    dict_of_teams_and_role.add_new_named_role_to_team(
        team=team, new_role_name=new_role_name
    )
    update_dict_of_teams_and_roles(
        object_store=object_store, dict_of_teams_and_roles=dict_of_teams_and_role
    )


def get_team_from_list_of_given_name_of_team(
    object_store: ObjectStore, team_selected: str
) -> Team:
    list_of_teams = get_list_of_teams(object_store)
    return list_of_teams.matching_team_name(team_selected)


def get_team_from_id(object_store: ObjectStore, team_id: str):
    list_of_teams = get_list_of_teams(object_store)
    return list_of_teams.object_with_id(team_id)


def modify_list_of_roles_with_skills(
    object_store: ObjectStore,
    existing_object: RoleWithSkills,
    new_object: RoleWithSkills,
):
    list_of_roles_with_skills = get_list_of_roles_with_skills(object_store)
    list_of_roles_with_skills.modify(existing_role=existing_object, new_role=new_object)
    try:
        list_of_roles_with_skills.check_for_duplicated_names()
        update_list_of_roles_with_skills(
            object_store=object_store,
            list_of_roles_with_skills=list_of_roles_with_skills,
        )
    except:
        raise Exception(
            "One or more duplicated role names in list - role names must be unique"
        )


def add_to_list_of_roles_with_skills(
    object_store: ObjectStore, name_of_entry_to_add: str
):
    list_of_roles_with_skills = get_list_of_roles_with_skills(object_store)
    list_of_roles_with_skills.add(name_of_entry_to_add)
    update_list_of_roles_with_skills(
        object_store=object_store, list_of_roles_with_skills=list_of_roles_with_skills
    )


def update_list_of_roles_with_skills(
    object_store: ObjectStore, list_of_roles_with_skills: ListOfRolesWithSkills
):
    object_store.update(
        list_of_roles_with_skills,
        object_definition=object_definition_for_list_of_roles_with_skills,
    )


def get_list_of_roles_with_skills(object_store: ObjectStore) -> ListOfRolesWithSkills:
    return object_store.get(object_definition_for_list_of_roles_with_skills)


def add_new_team(object_store: ObjectStore, name_of_entry_to_add: str):
    list_of_teams = get_list_of_teams(object_store)
    list_of_teams.add(name_of_entry_to_add)
    update_list_of_teams(object_store=object_store, list_of_teams=list_of_teams)


def modify_team(object_store: ObjectStore, existing_object: Team, new_object: Team):
    list_of_teams = get_list_of_teams(object_store)
    list_of_teams.replace(existing_team=existing_object, new_team=new_object)
    try:
        list_of_teams.check_for_duplicated_names()
    except:
        raise Exception("Duplicate names - team names have to be unique")
    update_list_of_teams(object_store=object_store, list_of_teams=list_of_teams)


def get_list_of_teams(object_store: ObjectStore) -> ListOfTeams:
    return object_store.get(object_definition_for_list_of_teams)


def update_list_of_teams(object_store: ObjectStore, list_of_teams: ListOfTeams):
    object_store.update(
        new_object=list_of_teams, object_definition=object_definition_for_list_of_teams
    )


def get_list_of_roles(object_store: ObjectStore) -> ListOfRolesWithSkillIds:
    return object_store.get(object_definition_for_list_of_roles_with_skill_ids)


def update_list_of_roles(
    object_store: ObjectStore, list_of_roles: ListOfRolesWithSkillIds
):
    object_store.update(
        new_object=list_of_roles,
        object_definition=object_definition_for_list_of_roles_with_skill_ids,
    )


def get_dict_of_teams_and_roles(object_store: ObjectStore) -> DictOfTeamsWithRoles:
    return object_store.get(object_definition_for_dict_of_teams_with_roles)


def update_dict_of_teams_and_roles(
    object_store: ObjectStore, dict_of_teams_and_roles: DictOfTeamsWithRoles
):
    object_store.update(
        new_object=dict_of_teams_and_roles,
        object_definition=object_definition_for_dict_of_teams_with_roles,
    )
