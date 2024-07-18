from typing import List

from app.objects.day_selectors import Day

from app.objects.events import Event

from app.OLD_backend.data.cadets import CadetData
from app.data_access.data_layer.ad_hoc_cache import AdHocCache

from app.data_access.data_layer.data_layer import DataLayer

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.exceptions import arg_not_passed
from app.objects.primtive_with_id.patrol_boats import ListOfPatrolBoats
from app.objects.primtive_with_id.volunteers import (
    ListOfVolunteers,
    Volunteer,
)
from app.objects.primtive_with_id.volunteer_skills import SkillsDict, ListOfVolunteerSkills
from app.objects.primtive_with_id.volunteer_at_event import ListOfVolunteersAtEventWithId, VolunteerAtEventWithId
from app.objects.primtive_with_id.patrol_boats import ListOfVolunteersWithIdAtEventWithPatrolBoatsId
from app.objects.patrol_boats import ListOfVolunteersAtEventWithPatrolBoatAndRole, VolunteerAtEventWithPatrolBoatAndRoleOnDay
from app.objects.volunteers_at_event import VolunteerEventData

class PatrolBoatData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api
        self.cache = AdHocCache(data_api)

    def get_list_of_volunteers_at_event_with_patrol_boat_and_role(self, event: Event) -> ListOfVolunteersAtEventWithPatrolBoatAndRole:
        all_volunteers_at_event = self.get_list_of_volunteers_at_event(event)

        list_of_volunteers_at_event_with_skills_patrol_boat_and_role = [

        ]

        return ListOfVolunteersAtEventWithPatrolBoatAndRole(list_of_volunteers_at_event_with_skills_patrol_boat_and_role)

    def get_volunteers_at_event_with_skills_patrol_boat_and_role_on_day_for_specific_volunteer(self, event: Event, volunteer_at_event_with_id: VolunteerAtEventWithId) -> ListOfVolunteersAtEventWithPatrolBoatAndRole:
        volunteer = self.get_list_of_volunteers().volunteer_with_id(volunteer_at_event_with_id.volunteer_id)
        volunteer_skills = self.get_list_of_volunteer_skills().dict_of_skills_for_volunteer_id(volunteer_at_event_with_id.volunteer_id)
        availability = volunteer_at_event_with_id.availablity
        available_on_days = availability.intersect(event.day_selector_with_covered_days())



    def get_volunteers_at_event_with_skills_patrol_boat_and_role_on_day_for_specific_volunteer_on_day(self, event: Event,
                                                                                                      volunteer: Volunteer,
                                                                                                      skills_dict: SkillsDict,
                                                                                                      volunteer_event_data: VolunteerEventData,
                                                                                                      day: Day) ->  VolunteerAtEventWithPatrolBoatAndRoleOnDay:
        return VolunteerAtEventWithPatrolBoatAndRoleOnDay(
            volunteer=volunteer,
            skills_dict=skills_dict,
            volunteer_event_data=volunteer_event_data,
            day=day,
            patrol_boat="",
            role_and_group=""
        )


    def get_list_of_volunteers(self) -> ListOfVolunteers:
        list_of_volunteers = self.data_api.get_list_of_volunteers()
        return list_of_volunteers

    def get_list_of_volunteer_skills(self) -> ListOfVolunteerSkills:
        return self.data_api.get_list_of_volunteer_skills()

    def get_list_of_volunteers_at_event(self, event: Event) -> ListOfVolunteersAtEventWithId:
        return self.data_api.get_list_of_volunteers_at_event(event)

    def get_list_of_patrol_boats(self) -> ListOfPatrolBoats:
        return self.data_api.get_list_of_patrol_boats()

    def get_list_of_voluteers_at_event_with_patrol_boats(self, event: Event) ->  ListOfVolunteersWithIdAtEventWithPatrolBoatsId:
        return self.data_api.get_list_of_voluteers_at_event_with_patrol_boats(event=event)