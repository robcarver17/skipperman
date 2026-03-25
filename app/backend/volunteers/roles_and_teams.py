from typing import List, Tuple

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.composed.roles_and_teams import DictOfTeamsWithRoles

from app.data_access.store.object_store import ObjectStore
from app.objects.composed.volunteer_roles import RoleWithSkills, ListOfRolesWithSkills
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    RoleAndGroup,
    ListOfRolesAndGroups,
)
from app.objects.utilities.exceptions import arg_not_passed

from app.objects.roles_and_teams import (
    ListOfTeams,
    ListOfRolesWithSkillIds,
    Team,
    ListOfTeamsAndRolesWithIds,
)
from app.backend.groups.list_of_groups import get_list_of_groups

from app.objects.roles_and_teams import no_role_allocated
from app.objects.groups import unallocated_group


def reorder_tuple_of_item_and_role_and_group(
    object_store: ObjectStore, list_of_tuples: List[Tuple[object, RoleAndGroup]]
) -> List[Tuple[object, RoleAndGroup]]:
    list_of_roles = get_list_of_roles(object_store)
    list_of_roles.append(no_role_allocated)
    list_of_groups = get_list_of_groups(object_store)
    list_of_groups.append(unallocated_group)

    list_of_roles_and_groups_in_tuple = ListOfRolesAndGroups(
        [tuple[1] for tuple in list_of_tuples]
    )
    unique_list_of_roles_and_groups = ListOfRolesAndGroups(
        set(list_of_roles_and_groups_in_tuple)
    )

    sorted_list_of_roles_and_groups = unique_list_of_roles_and_groups.sorted(
        list_of_groups=list_of_groups, list_of_roles=list_of_roles
    )
    sorted_list_of_tuples = []
    for role_and_group in sorted_list_of_roles_and_groups:
        for idx, role_and_group_in_tuple in enumerate(
            list_of_roles_and_groups_in_tuple
        ):
            if role_and_group_in_tuple == role_and_group:
                sorted_list_of_tuples.append(list_of_tuples[idx])

    return sorted_list_of_tuples


def reorder_roles_for_team_given_list_of_names(
    interface: abstractInterface, new_order_of_role_names: List[str], team: Team
):
    list_of_roles = get_list_of_roles(interface.object_store)
    ordered_list_of_roles = ListOfRolesWithSkills(
        [list_of_roles.matches_name(role_name) for role_name in new_order_of_role_names]
    )
    new_list_of_roles_with_ids = (
        ListOfTeamsAndRolesWithIds.create_new_list_for_team_from_ordered_role_ids(
            list_of_role_ids=ordered_list_of_roles.list_of_ids(), team_id=team.id
        )
    )

    interface.update(
        interface.object_store.data_api.data_list_of_teams_and_roles_with_ids.update_roles_for_team,
        team_id=team.id,
        new_list_of_roles_with_ids=new_list_of_roles_with_ids,
    )


def add_new_named_role_to_team(
    interface: abstractInterface, team: Team, new_role_name: str
):
    try:
        list_of_roles = get_list_of_roles(interface.object_store)
        role = list_of_roles.matches_name(new_role_name)
        interface.update(
            interface.object_store.data_api.data_list_of_teams_and_roles_with_ids.add_new_role_to_team,
            team_id=team.id,
            role_id=role.id,
        )
    except Exception as e:
        interface.log_error(
            "Can't add role %s to team %s, error: %s" % (new_role_name, team, str(e))
        )


def get_team_from_list_of_given_name_of_team(
    object_store: ObjectStore, team_selected: str
) -> Team:
    list_of_teams = get_list_of_teams(object_store)
    return list_of_teams.matching_team_name(team_selected)


def get_team_from_id(object_store: ObjectStore, team_id: str, default=arg_not_passed):
    list_of_teams = get_list_of_teams(object_store)
    return list_of_teams.team_with_id(team_id, default=default)


def modify_role_with_skills(
    interface: abstractInterface,
    existing_object: RoleWithSkills,
    new_object: RoleWithSkills,
):
    try:
        interface.update(
            interface.object_store.data_api.data_list_of_roles.update_role_with_skill,
            existing_role_with_skills=existing_object,
            new_role_with_skills=new_object,
        )
    except Exception as e:
        interface.log_error(
            "Cannot modify %s because %s" % (existing_object.name, str(e))
        )


def add_to_list_of_roles_with_skills(
    interface: abstractInterface, name_of_entry_to_add: str
):
    new_role = RoleWithSkills.from_name(name_of_entry_to_add)
    try:
        interface.update(
            interface.object_store.data_api.data_list_of_roles.add_role_with_skill,
            new_role=new_role,
        )
    except Exception as e:
        interface.log_error("Cannot add %s because %s" % (name_of_entry_to_add, str(e)))


def update_list_of_roles_with_skills(
    interface: abstractInterface, list_of_roles_with_skills: ListOfRolesWithSkills
):
    interface.update(
        interface.object_store.data_api.data_list_of_roles.write,
        list_of_roles=list_of_roles_with_skills.as_list_of_roles_with_skill_ids(),
    )


def get_list_of_roles_with_skills(object_store: ObjectStore) -> ListOfRolesWithSkills:
    return object_store.get(
        object_store.data_api.data_list_of_roles.read_list_of_roles_with_skills
    )


def add_new_team(interface: abstractInterface, name_of_entry_to_add: str):
    team = Team(name_of_entry_to_add)

    interface.update(
        interface.object_store.data_api.data_list_of_teams.add_new_team,
        new_team=team,
    )


def modify_team(interface: abstractInterface, existing_object: Team, new_object: Team):
    interface.update(
        interface.object_store.data_api.data_list_of_teams.modify_team,
        original_team=existing_object,
        new_team=new_object,
    )


def get_list_of_teams(object_store: ObjectStore) -> ListOfTeams:
    return object_store.get(object_store.data_api.data_list_of_teams.read)


def update_list_of_teams(interface: abstractInterface, list_of_teams: ListOfTeams):
    interface.update(
        interface.object_store.data_api.data_list_of_teams.write,
        list_of_teams=list_of_teams,
    )


def get_role_from_name(
    object_store: ObjectStore, role_name: str, default=arg_not_passed
) -> RoleWithSkills:
    list_of_roles = get_list_of_roles_with_skills(object_store)
    return list_of_roles.role_with_name(role_name, default=default)


def get_list_of_roles(object_store: ObjectStore) -> ListOfRolesWithSkillIds:
    return object_store.get(object_store.data_api.data_list_of_roles.read)


def order_list_of_roles(
    object_store: ObjectStore, list_of_roles: ListOfRolesWithSkillIds
):
    all_roles = get_list_of_roles(object_store)
    return all_roles.subset_from_list_of_ids_retaining_order(
        list_of_ids=list_of_roles.list_of_ids
    )


def get_dict_of_teams_and_roles(object_store: ObjectStore) -> DictOfTeamsWithRoles:
    return object_store.get(
        object_store.data_api.data_list_of_teams_and_roles_with_ids.get_dict_of_teams_and_roles
    )
