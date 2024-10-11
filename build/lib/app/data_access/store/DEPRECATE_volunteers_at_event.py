from typing import List

from app.objects.events import Event

from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache

from app.data_access.store.data_layer import DataLayer
from app.data_access.store.DEPRECATE_cadets_with_groups_at_event import CadetsWithGroupsAtEventData

from app.objects.volunteers import (
    ListOfVolunteers,

)
from app.objects.composed.volunteers_with_skills import ListOfVolunteersWithSkills
from app.objects_OLD.primtive_with_id.volunteer_at_event import ListOfVolunteersAtEventWithId, VolunteerAtEventWithId

from app.objects_OLD.volunteers_at_event import VolunteerAtEventWithSkills, ListOfVolunteersAtEventWithSkills
from app.objects_OLD.cadets_with_groups import ListOfCadetsAtEventWithGroupsByDay, CadetAtEventWithGroupsByDay


class VolunteersAtEventData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api
        self.cache = AdHocCache(data_api)

    def get_list_of_volunteers_at_event_with_skills(self, event: Event) -> ListOfVolunteersAtEventWithSkills:
        all_volunteers_with_id_at_event = self.get_list_of_volunteers_with_id_at_event(event)

        list_of_volunteers_at_event = [
            self.get_volunteer_at_event_with_skills(
                event=event,
                volunteer_at_event_with_id=volunteer_at_event_with_id
            ) for volunteer_at_event_with_id in all_volunteers_with_id_at_event
        ]

        return ListOfVolunteersAtEventWithSkills(list_of_volunteers_at_event)

    def get_volunteer_at_event_with_skills(self, event: Event, volunteer_at_event_with_id: VolunteerAtEventWithId) -> VolunteerAtEventWithSkills:
        volunteer = self.get_list_of_volunteers().volunteer_with_id(volunteer_at_event_with_id.volunteer_id)
        volunteer_skills = self.get_list_of_volunteer_skills().dict_of_skills_for_volunteer_id(volunteer_at_event_with_id.volunteer_id)
        list_of_associated_cadets=self.get_list_of_associated_cadets_at_event(event=event, list_of_associated_cadet_id=volunteer_at_event_with_id.list_of_associated_cadet_id)

        return VolunteerAtEventWithSkills.from_volunteer_at_event_with_id(
            event=event,
            volunteer=volunteer,
            volunteer_at_event_with_id=volunteer_at_event_with_id,
            list_of_associated_cadets=list_of_associated_cadets,
            skills_dict=volunteer_skills
        )

    def get_list_of_associated_cadets_at_event(self, event: Event, list_of_associated_cadet_id: List[str]) -> ListOfCadetsAtEventWithGroupsByDay:
        list_of_cadets = [
            self.get_associated_cadet_at_event(event=event, cadet_id=cadet_id)
            for cadet_id in list_of_associated_cadet_id
        ]

        return ListOfCadetsAtEventWithGroupsByDay(list_of_cadets)


    def get_associated_cadet_at_event(self, event: Event, cadet_id: str) -> CadetAtEventWithGroupsByDay:
        list_of_cadets_at_event_with_groups_by_day = self.get_list_of_cadets_at_event_with_groups_by_day(event)
        return list_of_cadets_at_event_with_groups_by_day.cadet_at_event_with_groups_by_day_given_id(cadet_id=cadet_id)

    def get_list_of_cadets_at_event_with_groups_by_day(self, event: Event) -> ListOfCadetsAtEventWithGroupsByDay:
        return self.cache.get_from_cache(
            get_list_of_cadets_at_event_with_groups_by_day,
            event=event
        )

    def get_list_of_volunteers(self) -> ListOfVolunteers:
        list_of_volunteers = self.data_api.get_list_of_volunteers()
        return list_of_volunteers

    def get_list_of_volunteer_skills(self) -> ListOfVolunteersWithSkills:
        return self.data_api.get_list_of_volunteer_skills()

    def get_list_of_volunteers_with_id_at_event(self, event: Event) -> ListOfVolunteersAtEventWithId:
        return self.data_api.get_list_of_volunteers_at_event(event)


def get_list_of_cadets_at_event_with_groups_by_day(data_layer: DataLayer, event: Event) -> ListOfCadetsAtEventWithGroupsByDay:
    cadets_with_groups_at_event_data = CadetsWithGroupsAtEventData(data_layer)
    return cadets_with_groups_at_event_data.get_list_of_cadets_at_event_with_groups_by_day(event)
