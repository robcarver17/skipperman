from typing import Dict

from app.data_access.composed.composed_base import ComposedBaseData
from app.objects.cadets import ListOfCadets
from app.objects.composed.cadet_volunteer_associations import (
    DictOfCadetsAssociatedWithVolunteer,
)
from app.objects.composed.people_at_event_with_club_dinghies import (
    DictOfPeopleAndClubDinghiesAtEvent,
)
from app.objects.composed.roles_and_teams import DictOfTeamsWithRoles
from app.objects.composed.volunteer_roles import ListOfRolesWithSkills
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    DictOfDaysRolesAndGroupsAndTeams,
)
from app.objects.composed.volunteers_at_event_with_patrol_boats import (
    DictOfVolunteersAtEventWithPatrolBoatsByDay,
    PatrolBoatByDayDict, DictOfLabelsForEvent,
)
from app.objects.composed.volunteers_at_event_with_registration_data import (
    DictOfRegistrationDataForVolunteerAtEvent,
)
from app.objects.composed.volunteers_last_role_across_events import (
    DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents,
)
from app.objects.composed.volunteers_with_all_event_data import (
    DictOfAllEventDataForVolunteers,
    AllEventDataForVolunteer,
)
from app.objects.composed.volunteers_with_skills import (
    DictOfVolunteersWithSkills,
    SkillsDict,
)
from app.objects.events import Event
from app.objects.groups import ListOfGroups
from app.objects.volunteers import Volunteer


class ComposedDataAllEventInfoForVolunteers(ComposedBaseData):
    def get_dict_of_all_event_info_for_volunteers(
        self, event: Event
    ) -> DictOfAllEventDataForVolunteers:
        dict_of_registration_data_for_volunteers_at_event = self.object_store.get(
            self.object_store.data_api.data_list_of_volunteers_at_event.get_dict_of_registration_data_for_volunteers_at_event,
            event_id=event.id,
        )
        dict_of_volunteers_with_skills = self.object_store.get(
            self.object_store.data_api.data_list_of_volunteer_skills.get_dict_of_volunteers_with_skills
        )
        dict_of_volunteers_at_event_with_days_and_roles = self.object_store.get(
            self.object_store.data_api.data_list_of_volunteers_in_roles_at_event.get_dict_of_volunteers_with_roles_and_groups_at_event,
            event_id=event.id,
        )

        dict_of_volunteers_at_event_with_patrol_boats = self.object_store.get(
            self.object_store.data_api.data_list_of_volunteers_at_event_with_patrol_boats.get_dict_of_patrol_boats_by_day_for_volunteer_at_event,
            event_id=event.id,
        )
        dict_of_cadets_associated_with_volunteers = self.object_store.get(
            self.object_store.data_api.data_list_of_cadet_volunteer_associations.get_dict_of_cadets_associated_with_volunteers
        )

        dict_of_people_and_club_dinghies_at_event = self.object_store.get(
            self.object_store.data_api.data_list_of_volunteers_at_event_with_club_dinghies.read_dict_of_volunteers_and_club_dinghies_at_event,
            event_id=event.id,
        )

        dict_of_volunteers_with_most_common_role_and_group_across_events = self.object_store.get(
            self.object_store.data_api.data_list_of_last_roles_across_events_for_volunteers.get_dict_of_volunteers_with_last_role_and_group_across_events
        )
        dict_of_teams_and_roles = self.object_store.get(
            self.object_store.data_api.data_list_of_teams_and_roles_with_ids.get_dict_of_teams_and_roles
        )
        list_of_groups = self.object_store.get(
            self.object_store.data_api.data_list_of_groups.read
        )
        list_of_roles_with_skills = self.object_store.get(
            self.object_store.data_api.data_list_of_roles.read_list_of_roles_with_skills
        )
        dict_of_patrol_boat_labels_for_event=self.object_store.get(self.object_store.data_api.data_list_of_patrol_boat_labels.get_dict_of_patrol_boat_labels_for_event,
                                                                   event_id=event.id)

        return compose_dict_of_all_event_data_for_volunteers(
            event=event,
            dict_of_cadets_associated_with_volunteers=dict_of_cadets_associated_with_volunteers,
            dict_of_volunteers_with_skills=dict_of_volunteers_with_skills,
            dict_of_people_and_club_dinghies_at_event=dict_of_people_and_club_dinghies_at_event,
            dict_of_registration_data_for_volunteers_at_event=dict_of_registration_data_for_volunteers_at_event,
            dict_of_volunteers_at_event_with_days_and_roles=dict_of_volunteers_at_event_with_days_and_roles,
            dict_of_volunteers_with_most_common_role_and_group_across_events=dict_of_volunteers_with_most_common_role_and_group_across_events,
            dict_of_volunteers_at_event_with_patrol_boats=dict_of_volunteers_at_event_with_patrol_boats,
            dict_of_teams_and_roles=dict_of_teams_and_roles,
            list_of_groups=list_of_groups,
            list_of_roles_with_skills=list_of_roles_with_skills,
            dict_of_patrol_boat_labels_for_event=dict_of_patrol_boat_labels_for_event
        )


def compose_dict_of_all_event_data_for_volunteers(
    event: Event,
    dict_of_registration_data_for_volunteers_at_event: DictOfRegistrationDataForVolunteerAtEvent,
    dict_of_volunteers_with_skills: DictOfVolunteersWithSkills,
    dict_of_volunteers_at_event_with_days_and_roles: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    dict_of_volunteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
    dict_of_cadets_associated_with_volunteers: DictOfCadetsAssociatedWithVolunteer,
    dict_of_people_and_club_dinghies_at_event: DictOfPeopleAndClubDinghiesAtEvent,
    dict_of_volunteers_with_most_common_role_and_group_across_events: DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents,
    dict_of_teams_and_roles: DictOfTeamsWithRoles,
    list_of_roles_with_skills: ListOfRolesWithSkills,
    list_of_groups: ListOfGroups,
dict_of_patrol_boat_labels_for_event: DictOfLabelsForEvent

) -> DictOfAllEventDataForVolunteers:
    raw_dict = compose_raw_dict_of_all_event_data_for_volunteers(
        dict_of_volunteers_with_skills=dict_of_volunteers_with_skills,
        dict_of_volunteers_at_event_with_patrol_boats=dict_of_volunteers_at_event_with_patrol_boats,
        dict_of_registration_data_for_volunteers_at_event=dict_of_registration_data_for_volunteers_at_event,
        dict_of_volunteers_at_event_with_days_and_roles=dict_of_volunteers_at_event_with_days_and_roles,
        dict_of_cadets_associated_with_volunteers=dict_of_cadets_associated_with_volunteers,
        dict_of_people_and_club_dinghies_at_event=dict_of_people_and_club_dinghies_at_event,
        dict_of_volunteers_with_most_common_role_and_group_across_events=dict_of_volunteers_with_most_common_role_and_group_across_events,
        event=event,
    )

    return DictOfAllEventDataForVolunteers(
        raw_dict=raw_dict,
        event=event,
        dict_of_volunteers_with_skills=dict_of_volunteers_with_skills,
        dict_of_volunteers_at_event_with_patrol_boats=dict_of_volunteers_at_event_with_patrol_boats,
        dict_of_registration_data_for_volunteers_at_event=dict_of_registration_data_for_volunteers_at_event,
        dict_of_volunteers_at_event_with_days_and_roles=dict_of_volunteers_at_event_with_days_and_roles,
        dict_of_cadets_associated_with_volunteers=dict_of_cadets_associated_with_volunteers,
        dict_of_people_and_club_dinghies_at_event=dict_of_people_and_club_dinghies_at_event,
        dict_of_volunteers_with_most_common_role_and_group_across_events=dict_of_volunteers_with_most_common_role_and_group_across_events,
        dict_of_teams_and_roles=dict_of_teams_and_roles,
        list_of_groups=list_of_groups,
        list_of_roles_with_skills=list_of_roles_with_skills,
        dict_of_patrol_boat_labels_for_event=dict_of_patrol_boat_labels_for_event
    )


def compose_raw_dict_of_all_event_data_for_volunteers(
    dict_of_registration_data_for_volunteers_at_event: DictOfRegistrationDataForVolunteerAtEvent,
    dict_of_volunteers_with_skills: DictOfVolunteersWithSkills,
    dict_of_volunteers_at_event_with_days_and_roles: DictOfVolunteersAtEventWithDictOfDaysRolesAndGroups,
    dict_of_volunteers_at_event_with_patrol_boats: DictOfVolunteersAtEventWithPatrolBoatsByDay,
    dict_of_cadets_associated_with_volunteers: DictOfCadetsAssociatedWithVolunteer,
    dict_of_people_and_club_dinghies_at_event: DictOfPeopleAndClubDinghiesAtEvent,
    dict_of_volunteers_with_most_common_role_and_group_across_events: DictOfVolunteersWithMostCommonRoleAndGroupAcrossEvents,
    event: Event,
) -> Dict[Volunteer, AllEventDataForVolunteer]:
    ## THis construction means if we delete from registration data they won't be seen elsewhere
    volunteers_at_event = (
        dict_of_registration_data_for_volunteers_at_event.list_of_volunteers_at_event()
    )

    return dict(
        [
            (
                volunteer,
                AllEventDataForVolunteer(
                    volunteer=volunteer,
                    registration_data=dict_of_registration_data_for_volunteers_at_event[
                        volunteer
                    ],
                    volunteer_skills=dict_of_volunteers_with_skills.get(
                        volunteer, SkillsDict()
                    ),
                    roles_and_groups=dict_of_volunteers_at_event_with_days_and_roles.get(
                        volunteer, DictOfDaysRolesAndGroupsAndTeams()
                    ),
                    patrol_boats=dict_of_volunteers_at_event_with_patrol_boats.get(
                        volunteer, PatrolBoatByDayDict()
                    ),
                    associated_cadets=dict_of_cadets_associated_with_volunteers.get(
                        volunteer, ListOfCadets([])
                    ),
                    club_boats=dict_of_people_and_club_dinghies_at_event.club_dinghys_for_person(
                        volunteer
                    ),
                    most_common_role_group_and_team_at_previous_events=dict_of_volunteers_with_most_common_role_and_group_across_events.get_most_common_role_and_group_for_volunteer_or_none(
                        volunteer
                    ),
                    event=event,
                ),
            )
            for volunteer in volunteers_at_event
        ]
    )
