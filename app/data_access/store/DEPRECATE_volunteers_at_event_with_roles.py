from app.objects.day_selectors import Day

from app.data_access.store.DEPRECATE_volunteers_at_event import VolunteersAtEventData

from app.objects.events import Event

from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache

from app.data_access.store.data_access import DataLayer
from app.objects.volunteer_roles_and_groups_with_id import (
    ListOfVolunteersWithIdInRoleAtEvent,
    RoleAndGroupDEPRECATE,
)

from app.objects_OLD.volunteers_in_roles import (
    ListOfVolunteersAtEventWithSkillsAndRoles,
    VolunteerAtEventWithSkillsAndRoles,
    RoleAndGroupByDayDict,
    VolunteerAtEventWithSkills_DEPRECATE,
    ListOfVolunteersAtEventWithSkills,
)


class VolunteersAtEventWithRolesData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api
        self.cache = AdHocCache(data_api)

    def get_list_of_volunteers_at_event_with_skills_and_roles(
        self, event: Event
    ) -> ListOfVolunteersAtEventWithSkillsAndRoles:
        list_of_volunteers_at_event_with_skills = (
            self.get_list_of_volunteers_at_event_with_skills(event=event)
        )
        list_of_volunteers_at_event_with_skills_and_roles = [
            self.get_volunteer_at_event_with_skills_and_roles(
                volunteer_at_event_with_skills=volunteer_at_event_with_skills
            )
            for volunteer_at_event_with_skills in list_of_volunteers_at_event_with_skills
        ]
        return ListOfVolunteersAtEventWithSkillsAndRoles(
            list_of_volunteers_at_event_with_skills_and_roles
        )

    def get_volunteer_at_event_with_skills_and_roles(
        self, volunteer_at_event_with_skills: VolunteerAtEventWithSkills_DEPRECATE
    ) -> VolunteerAtEventWithSkillsAndRoles:
        role_and_group_by_day = (
            self.get_role_and_group_across_days_for_volunteer_at_event(
                volunteer_at_event_with_skills=volunteer_at_event_with_skills
            )
        )
        return VolunteerAtEventWithSkillsAndRoles.from_volunteer_at_event_with_skills(
            volunteer_at_event_with_skills=volunteer_at_event_with_skills,
            role_and_group_by_day=role_and_group_by_day,
        )

    def get_role_and_group_across_days_for_volunteer_at_event(
        self, volunteer_at_event_with_skills: VolunteerAtEventWithSkills_DEPRECATE
    ) -> RoleAndGroupByDayDict:
        dict_of_roles_and_groups = dict(
            [
                (
                    day,
                    self.get_role_and_group_by_day_for_volunteer_at_event(
                        day=day,
                        volunteer_at_event_with_skills=volunteer_at_event_with_skills,
                    ),
                )
                for day in volunteer_at_event_with_skills.volunteer_event_data.availablity
            ]
        )

        return RoleAndGroupByDayDict(dict_of_roles_and_groups)

    def get_role_and_group_by_day_for_volunteer_at_event(
        self,
        day: Day,
        volunteer_at_event_with_skills: VolunteerAtEventWithSkills_DEPRECATE,
    ) -> RoleAndGroupDEPRECATE:
        list_of_volunteers_with_ids_in_roles_at_event = (
            self.get_list_of_volunteers_with_ids_in_roles_at_event(
                volunteer_at_event_with_skills.volunteer_event_data.event
            )
        )
        volunteer_with_role_and_group = list_of_volunteers_with_ids_in_roles_at_event.member_matching_volunteer_id_and_day(
            volunteer_id=volunteer_at_event_with_skills.volunteer.id,
            day=day,
            return_empty_if_missing=True,
        )

        return volunteer_with_role_and_group.role_and_group

    def get_list_of_volunteers_with_ids_in_roles_at_event(
        self, event: Event
    ) -> ListOfVolunteersWithIdInRoleAtEvent:
        return self.data_api.get_list_of_volunteers_in_roles_at_event(event)

    def get_list_of_volunteers_at_event_with_skills(
        self, event: Event
    ) -> ListOfVolunteersAtEventWithSkills:
        return self.cache.get_from_cache(
            get_list_of_volunteers_at_event_with_skills, event=event
        )


def get_list_of_volunteers_at_event_with_skills(
    data_layer: DataLayer, event: Event
) -> ListOfVolunteersAtEventWithSkills:
    volunteers_at_event_data = VolunteersAtEventData(data_layer)
    return volunteers_at_event_data.get_list_of_volunteers_at_event_with_skills(event)
