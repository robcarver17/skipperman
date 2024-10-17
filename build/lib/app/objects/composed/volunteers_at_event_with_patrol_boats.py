from dataclasses import dataclass
from typing import Dict, List

from app.objects.events import Event, ListOfEvents

from app.objects.volunteers import Volunteer, ListOfVolunteers

from app.objects.patrol_boats import PatrolBoat, ListOfPatrolBoats

from app.objects.day_selectors import Day

from app.objects.patrol_boats_with_volunteers_with_id import ListOfVolunteersWithIdAtEventWithPatrolBoatsId, VolunteerWithIdAtEventWithPatrolBoatId

empty_place_holder_for_new_boat = Volunteer(
    first_name="****placeholder",
    surname="****newboat"
)

@dataclass
class VolunteerPatrolBoatDay:
    volunteer:Volunteer
    day: Day
    patrol_boat: PatrolBoat

    @classmethod
    def from_volunteer_id_and_patrol_boat_id_at_event(cls, volunteer_id_and_patrol_boat_id_at_event: VolunteerWithIdAtEventWithPatrolBoatId,
                                                      list_of_patrol_boats: ListOfPatrolBoats,
                                                      list_of_volunteers: ListOfVolunteers
                                                      ):

        if volunteer_id_and_patrol_boat_id_at_event.is_empty:
            volunteer= empty_place_holder_for_new_boat
        else:
            volunteer_id = volunteer_id_and_patrol_boat_id_at_event.volunteer_id
            volunteer = list_of_volunteers.volunteer_with_id(volunteer_id)

        return cls(
            volunteer=volunteer,
            patrol_boat=list_of_patrol_boats.object_with_id(volunteer_id_and_patrol_boat_id_at_event.patrol_boat_id),
            day=volunteer_id_and_patrol_boat_id_at_event.day
        )


class PatrolBoatByDayDict(Dict[Day, PatrolBoat]):
    def first_patrol_boat(self) -> PatrolBoat:
        return list(set(self.values()))[0]

class ListOfVolunteerPatrolBoatDays(List[VolunteerPatrolBoatDay]):
    def unique_list_of_volunteers(self) -> ListOfVolunteers:
        list_of_volunteers =  [
            volunteer_patrol_boat.volunteer
            for volunteer_patrol_boat in self
        ]
        list_of_volunteers = list(set(list_of_volunteers))
        list_of_volunteers = [volunteer for volunteer in list_of_volunteers if volunteer is not empty_place_holder_for_new_boat]

        return ListOfVolunteers(list_of_volunteers)

    def unique_list_of_patrol_boats(self) -> ListOfPatrolBoats:
        list_of_boats =  [
            volunteer_patrol_boat.patrol_boat
            for volunteer_patrol_boat in self
        ]

        list_of_boats = list(set(list_of_boats))

        return ListOfPatrolBoats(list_of_boats)

    @classmethod
    def from_list_of_volunteer_id_and_patrol_boat_id_at_event(cls,
                                                    list_of_volunteer_ids_and_patrol_boat_id_at_event: ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
                                                      list_of_patrol_boats: ListOfPatrolBoats,
                                                      list_of_volunteers: ListOfVolunteers
                                                      ):

        return cls(
            [
                VolunteerPatrolBoatDay.from_volunteer_id_and_patrol_boat_id_at_event(volunteer_id_and_patrol_boat_id_at_event=volunteer_id_and_patrol_boat_id_at_event,
                                                                                     list_of_volunteers=list_of_volunteers,
                                                                                     list_of_patrol_boats=list_of_patrol_boats)
                for volunteer_id_and_patrol_boat_id_at_event in list_of_volunteer_ids_and_patrol_boat_id_at_event
            ]
        )

    def patrol_boat_dict_for_volunteer(self, volunteer: Volunteer) -> PatrolBoatByDayDict:
        subset_for_volunteer = self.subset_for_volunteer(volunteer)
        return PatrolBoatByDayDict(
            dict(
                [
                    (patrol_boat_volunteer.day,
                     patrol_boat_volunteer.patrol_boat)
                    for patrol_boat_volunteer in subset_for_volunteer
                ]
            )
        )

    def subset_for_volunteer(self, volunteer: Volunteer) -> 'ListOfVolunteerPatrolBoatDays':
        subset_for_volunteer = [patrol_boat_volunteer for patrol_boat_volunteer in self if
                                patrol_boat_volunteer.volunteer == volunteer]

        return ListOfVolunteerPatrolBoatDays(subset_for_volunteer)

class DictOfVolunteersAtEventWithPatrolBoatsByDay(Dict[Volunteer, PatrolBoatByDayDict]):
    def __init__(self, raw_dict: Dict[Volunteer, PatrolBoatByDayDict], event: Event,
                list_of_all_patrol_boats_at_event: ListOfPatrolBoats,
                 list_of_volunteers_with_id_at_event_with_patrol_boat_id: ListOfVolunteersWithIdAtEventWithPatrolBoatsId):
        super().__init__(raw_dict)
        self._event = event
        self._list_of_volunteers_with_id_at_event_with_patrol_boat_id = list_of_volunteers_with_id_at_event_with_patrol_boat_id
        self._list_of_all_patrol_boats_at_event = list_of_all_patrol_boats_at_event

    @property
    def list_of_volunteers_with_id_at_event_with_patrol_boat_id(self) -> ListOfVolunteersWithIdAtEventWithPatrolBoatsId:
        return self._list_of_volunteers_with_id_at_event_with_patrol_boat_id

    @property
    def event(self) -> Event:
        return self._event

    @property
    def list_of_all_patrol_boats_at_event(self) -> ListOfPatrolBoats:
        return self._list_of_all_patrol_boats_at_event

def compose_dict_of_patrol_boats_by_day_for_volunteer_at_event(event_id: str,
                                                               list_of_events: ListOfEvents,
                                                               list_of_volunteers: ListOfVolunteers,
                                                               list_of_patrol_boats: ListOfPatrolBoats,
                                                               list_of_volunteers_with_id_at_event_with_patrol_boat_id: ListOfVolunteersWithIdAtEventWithPatrolBoatsId)-> DictOfVolunteersAtEventWithPatrolBoatsByDay:

    event = list_of_events.object_with_id(event_id)

    list_of_volunteer_patrol_boat_days = ListOfVolunteerPatrolBoatDays.from_list_of_volunteer_id_and_patrol_boat_id_at_event(
        list_of_volunteer_ids_and_patrol_boat_id_at_event=list_of_volunteers_with_id_at_event_with_patrol_boat_id,
        list_of_volunteers=list_of_volunteers,
        list_of_patrol_boats=list_of_patrol_boats
    )

    unique_list_of_volunteers = list_of_volunteer_patrol_boat_days.unique_list_of_volunteers()
    unique_list_of_patrol_boats_at_event = list_of_volunteer_patrol_boat_days.unique_list_of_patrol_boats()

    raw_dict = dict(
        [
            (volunteer, list_of_volunteer_patrol_boat_days.patrol_boat_dict_for_volunteer(volunteer))
            for volunteer in unique_list_of_volunteers
        ]
    )

    return DictOfVolunteersAtEventWithPatrolBoatsByDay(
        raw_dict=raw_dict,
        event=event,
        list_of_volunteers_with_id_at_event_with_patrol_boat_id=list_of_volunteers_with_id_at_event_with_patrol_boat_id,
        list_of_all_patrol_boats_at_event=unique_list_of_patrol_boats_at_event
    )
