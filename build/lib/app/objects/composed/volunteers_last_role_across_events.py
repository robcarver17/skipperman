from typing import Dict, List, Union

from app.objects.composed.volunteer_with_group_and_role_at_event import RoleAndGroup, RoleAndGroupAndTeam
from app.objects.last_role_for_volunteer import ListOfMostCommonRoleForVolunteersAcrossEventsWithId

from app.objects.volunteers import Volunteer, ListOfVolunteers


from app.objects.groups import  ListOfGroups
from app.objects.composed.roles_and_teams import (
    ListOfRolesWithSkills, DictOfTeamsWithRoles,
)

no_role_and_group =RoleAndGroup()

class DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents(
    Dict[Volunteer, RoleAndGroupAndTeam]
):
    def __init__(
        self,
        raw_dict: Dict[Volunteer, RoleAndGroupAndTeam],
        list_of_most_common_role_for_volunteers_across_events_id: ListOfMostCommonRoleForVolunteersAcrossEventsWithId,

    ):
        super().__init__(raw_dict)
        self._list_of_most_common_role_for_volunteers_across_events_with_id= list_of_most_common_role_for_volunteers_across_events_id

    def get_most_common_role_and_group_for_volunteer_or_none(self, volunteer: Volunteer) -> RoleAndGroupAndTeam:
        role_and_group = self.get(volunteer, no_role_and_group)
        return role_and_group

    def update_most_common_role_and_group_for_volunteer(self, volunteer: Volunteer,
                                                 role_with_skills_and_group_and_team: RoleAndGroupAndTeam):
        self[volunteer] = role_with_skills_and_group_and_team
        self.list_of_most_common_role_for_volunteers_across_events_with_id.update(
            volunteer_id=volunteer.id,
            role_id=role_with_skills_and_group_and_team.role.id,
            group_id=role_with_skills_and_group_and_team.group.id,
        )

    @property
    def list_of_most_common_role_for_volunteers_across_events_with_id(self):
        return self._list_of_most_common_role_for_volunteers_across_events_with_id

def compose_dict_of_volunteers_with_last_role_and_group_across_events(
    list_of_groups: ListOfGroups,
    list_of_roles_with_skills: ListOfRolesWithSkills,
        list_of_most_common_role_for_volunteers_across_events_with_id: ListOfMostCommonRoleForVolunteersAcrossEventsWithId,
        list_of_volunteers: ListOfVolunteers,
        dict_of_teams_and_roles: DictOfTeamsWithRoles
) -> DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents:

    raw_dict = compose_raw_dict_of_volunteers_with_most_common_role_and_group_across_events(
        list_of_volunteers=list_of_volunteers,
        list_of_groups=list_of_groups,
        list_of_roles_with_skills=list_of_roles_with_skills,
        list_of_most_common_role_for_volunteers_across_events_with_id=list_of_most_common_role_for_volunteers_across_events_with_id,
        dict_of_teams_and_roles=dict_of_teams_and_roles
    )

    return DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents(
        raw_dict=raw_dict,
        list_of_most_common_role_for_volunteers_across_events_id=list_of_most_common_role_for_volunteers_across_events_with_id,
    )


def compose_raw_dict_of_volunteers_with_most_common_role_and_group_across_events(
    list_of_groups: ListOfGroups,
    list_of_roles_with_skills: ListOfRolesWithSkills,
        list_of_most_common_role_for_volunteers_across_events_with_id: ListOfMostCommonRoleForVolunteersAcrossEventsWithId,
        list_of_volunteers: ListOfVolunteers,
        dict_of_teams_and_roles: DictOfTeamsWithRoles
) -> Dict[Volunteer, RoleAndGroupAndTeam]:

    raw_dict = {}

    for volunteer_with_last_role_and_group_with_id in list_of_most_common_role_for_volunteers_across_events_with_id:
        volunteer = list_of_volunteers.volunteer_with_id(volunteer_with_last_role_and_group_with_id.volunteer_id)
        group = list_of_groups.group_with_id(volunteer_with_last_role_and_group_with_id.group_id)
        role= list_of_roles_with_skills.role_with_id(volunteer_with_last_role_and_group_with_id.role_id)
        list_of_team_and_index = (
            dict_of_teams_and_roles.list_of_teams_and_index_given_role(role)
        )
        raw_dict[volunteer] = RoleAndGroupAndTeam(role=role, group=group, list_of_team_and_index=list_of_team_and_index)

    return raw_dict

