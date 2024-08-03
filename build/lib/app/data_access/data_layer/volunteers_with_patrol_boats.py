
from app.objects.day_selectors import Day

from app.objects.events import Event

from app.data_access.data_layer.ad_hoc_cache import AdHocCache
from app.data_access.data_layer.data_layer import DataLayer
from app.data_access.data_layer.volunteers_at_event_with_roles import VolunteersAtEventWithRolesData

from app.objects.exceptions import  MissingData
from app.objects.primtive_with_id.patrol_boats import ListOfPatrolBoats, PatrolBoat
from app.objects.primtive_with_id.patrol_boats import ListOfVolunteersWithIdAtEventWithPatrolBoatsId
from app.objects.patrol_boats import ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats, VolunteerAtEventWithSkillsAndRolesAndPatrolBoats, PatrolBoatByDayDict
from app.objects.volunteers_in_roles import ListOfVolunteersAtEventWithSkillsAndRoles, VolunteerAtEventWithSkillsAndRoles

class PatrolBoatData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api
        self.cache = AdHocCache(data_api)

    def list_of_unique_boats_at_event_including_unallocated(self, event: Event) -> ListOfPatrolBoats:
        list_of_patrol_boats = self.get_list_of_patrol_boats()
        list_of_voluteers_at_event_with_patrol_boats = (
            self.get_list_of_voluteers_at_event_with_patrol_boats(event)
        )
        list_of_boats_at_event = list_of_voluteers_at_event_with_patrol_boats.list_of_unique_boats_at_event_including_unallocated(
            list_of_patrol_boats
        )

        return list_of_boats_at_event

    def get_list_of_volunteers_at_event_with_patrol_boat_and_role(self, event: Event) -> ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats:
        all_volunteers_at_event = self.get_list_of_volunteers_at_event_with_skills_and_roles(event)

        list_of_volunteers_at_event_with_skills_patrol_boat_and_role = [
            self.get_volunteers_at_event_with_skills_patrol_boat_and_role_on_day_for_specific_volunteer(
                volunteer_at_event_with_skills_and_roles) for volunteer_at_event_with_skills_and_roles in all_volunteers_at_event

        ]

        return ListOfVolunteersAtEventWithSkillsAndRolesAndPatrolBoats(list_of_volunteers_at_event_with_skills_patrol_boat_and_role)

    def get_volunteers_at_event_with_skills_patrol_boat_and_role_on_day_for_specific_volunteer(self,  volunteer_at_event_with_skills_and_roles: VolunteerAtEventWithSkillsAndRoles) -> VolunteerAtEventWithSkillsAndRolesAndPatrolBoats:
        patrol_boat_by_day = self.get_patrol_boat_by_day_dict_for_volunteer_at_event(
            volunteer_at_event_with_skills_and_roles=volunteer_at_event_with_skills_and_roles
        )
        return VolunteerAtEventWithSkillsAndRolesAndPatrolBoats.from_volunteer_at_event_with_skills_and_roles(
            volunteer_at_event_with_skills_and_roles=volunteer_at_event_with_skills_and_roles,
            patrol_boat_by_day=patrol_boat_by_day
        )

    def get_patrol_boat_by_day_dict_for_volunteer_at_event(self, volunteer_at_event_with_skills_and_roles: VolunteerAtEventWithSkillsAndRoles
                                                                                                      ) ->  PatrolBoatByDayDict:

        days_attending = volunteer_at_event_with_skills_and_roles.volunteer_event_data.availablity
        dict_of_boats_by_day = dict([
            (day,self.get_patrol_boat_on_day_for_volunteer_at_event(
                volunteer_at_event_with_skills_and_roles=volunteer_at_event_with_skills_and_roles,
                day=day
            ))
            for day in days_attending
        ])

        dict_of_boats_by_day_as_list = [(day, patrol_boat) for day, patrol_boat in dict_of_boats_by_day.items() if not patrol_boat.is_empty]

        return PatrolBoatByDayDict(dict_of_boats_by_day_as_list)

    def get_patrol_boat_on_day_for_volunteer_at_event(self, volunteer_at_event_with_skills_and_roles: VolunteerAtEventWithSkillsAndRoles,
                                                      day: Day
                                                                                                      ) ->  PatrolBoat:

        list_of_voluteers_at_event_with_patrol_boats = self.get_list_of_voluteers_at_event_with_patrol_boats(event=volunteer_at_event_with_skills_and_roles.volunteer_event_data.event)
        try:
            boat_id = list_of_voluteers_at_event_with_patrol_boats.which_boat_id_is_volunteer_on_today(volunteer_id=volunteer_at_event_with_skills_and_roles.volunteer.id,
                                                                                                                   day=day)
        except MissingData:
            return PatrolBoat.create_empty()

        patrol_boats = self.get_list_of_patrol_boats()
        return patrol_boats.object_with_id(boat_id)

    def get_list_of_volunteers_at_event_with_skills_and_roles(self, event: Event) -> ListOfVolunteersAtEventWithSkillsAndRoles:
        return self.cache.get_from_cache(get_list_of_volunteers_at_event_with_skills_and_roles,
                                         event=event)

    def get_list_of_patrol_boats(self) -> ListOfPatrolBoats:
        return self.data_api.get_list_of_patrol_boats()

    def get_list_of_voluteers_at_event_with_patrol_boats(self, event: Event) ->  ListOfVolunteersWithIdAtEventWithPatrolBoatsId:
        return self.data_api.get_list_of_voluteers_at_event_with_patrol_boats(event=event)

def get_list_of_volunteers_at_event_with_skills_and_roles(data_layer: DataLayer, event: Event) -> ListOfVolunteersAtEventWithSkillsAndRoles:
    volunteers_with_roles_at_event_data = VolunteersAtEventWithRolesData(data_layer)
    return volunteers_with_roles_at_event_data.get_list_of_volunteers_at_event_with_skills_and_roles(event)