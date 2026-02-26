from typing import Dict

from app.objects.composed.volunteer_with_group_and_role_at_event import (
    RoleAndGroup,
    RoleAndGroupAndTeam,
)
from app.objects.last_role_for_volunteer import (
    ListOfMostCommonRoleForVolunteersAcrossEventsWithId,
    MostCommonRoleForVolunteerAcrossEventsWithId,
)

from app.objects.volunteers import Volunteer

no_role_and_group = RoleAndGroup()


class DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents(
    Dict[Volunteer, RoleAndGroupAndTeam]
):
    def get_most_common_role_and_group_for_volunteer_or_none(
        self, volunteer: Volunteer
    ) -> RoleAndGroupAndTeam:
        role_and_group = self.get(volunteer, no_role_and_group)
        return role_and_group

    def update_most_common_role_and_group_for_volunteer(
        self,
        volunteer: Volunteer,
        role_with_skills_and_group_and_team: RoleAndGroupAndTeam,
    ):
        self[volunteer] = role_with_skills_and_group_and_team
        self.list_of_most_common_role_for_volunteers_across_events_with_id.update(
            volunteer_id=volunteer.id,
            role_id=role_with_skills_and_group_and_team.role.id,
            group_id=role_with_skills_and_group_and_team.group.id,
        )

    @property
    def list_of_most_common_role_for_volunteers_across_events_with_id(self):
        return ListOfMostCommonRoleForVolunteersAcrossEventsWithId(
            [
                MostCommonRoleForVolunteerAcrossEventsWithId(
                    volunteer_id=volunteer.id,
                    role_id=most_common.role.id,
                    group_id=most_common.group.id,
                )
                for volunteer, most_common in self.items()
            ]
        )


