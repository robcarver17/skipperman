from dataclasses import dataclass
from typing import List, Dict, Union

from app.objects.utilities.utils import flatten, most_common

from app.objects.events import ListOfEvents, Event

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.club_dinghies import ClubDinghy, ListOfClubDinghies, no_club_dinghy
from app.objects.day_selectors import Day
from app.objects.volunteers import ListOfVolunteers, Volunteer
from app.objects.volunteers_and_cades_at_event_with_club_boat_with_ids import (
    ListOfCadetAtEventWithIdAndClubDinghies,
    CadetAtEventWithClubDinghyWithId,
    VolunteerAtEventWithClubDinghyWithId,
)
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.volunteers_and_cades_at_event_with_club_boat_with_ids import (
    ListOfVolunteerAtEventWithIdAndClubDinghies,
)


@dataclass
class ClubDinghyAtEventOnDayForPerson:
    person: Union[Cadet, Volunteer]
    day: Day
    club_dinghy: ClubDinghy

    @classmethod
    def from_cadet_at_event_with_club_dinghy_and_id(
        cls,
        cadet_at_event_with_club_dinghy_and_id: CadetAtEventWithClubDinghyWithId,
        list_of_cadets: ListOfCadets,
        list_of_club_dinghies: ListOfClubDinghies,
    ):
        return cls(
            person=list_of_cadets.cadet_with_id(
                cadet_at_event_with_club_dinghy_and_id.cadet_id
            ),
            day=cadet_at_event_with_club_dinghy_and_id.day,
            club_dinghy=list_of_club_dinghies.club_dinghy_with_id(
                cadet_at_event_with_club_dinghy_and_id.club_dinghy_id
            ),
        )

    @classmethod
    def from_volunteer_at_event_with_club_dinghy_and_id(
        cls,
        volunteer_at_event_with_club_dinghy_and_id: VolunteerAtEventWithClubDinghyWithId,
        list_of_volunteers: ListOfVolunteers,
        list_of_club_dinghies: ListOfClubDinghies,
    ):
        return cls(
            person=list_of_volunteers.volunteer_with_id(
                volunteer_at_event_with_club_dinghy_and_id.volunteer_id
            ),
            day=volunteer_at_event_with_club_dinghy_and_id.day,
            club_dinghy=list_of_club_dinghies.club_dinghy_with_id(
                volunteer_at_event_with_club_dinghy_and_id.club_dinghy_id
            ),
        )


class DictOfDaysAndClubDinghiesAtEventForPerson(Dict[Day, ClubDinghy]):
    def allocate_club_boat_on_day(self, day: Day, club_boat: ClubDinghy):
        if club_boat is no_club_dinghy:
            try:
                self.pop(day)
            except:
                pass

        self[day] = club_boat

    def most_common(self) -> ClubDinghy:
        return most_common(self.list_of_dinghies(), default=no_club_dinghy)

    def has_any_dinghy_on_any_day(self):
        unique_list_of_dinghies = self.unique_list_of_dinghies()
        if len(unique_list_of_dinghies) > 0:
            return True
        if len(unique_list_of_dinghies) == 0:
            return False
        single_dinghy = unique_list_of_dinghies[0]
        if single_dinghy is no_club_dinghy:
            return False

    def has_any_dinghy_on_specific_day(self, day: Day) -> bool:
        dinghy_on_day = self.dinghy_on_day(day, default=no_club_dinghy)
        no_dinghy_on_day = dinghy_on_day is no_club_dinghy

        return not no_dinghy_on_day

    def has_specific_dinghy_on_day(self, day: Day, dinghy: ClubDinghy):
        dinghy_on_day = self.dinghy_on_day(day, default=no_club_dinghy)
        if dinghy_on_day == no_club_dinghy:
            return False

        return dinghy_on_day == dinghy

    def dinghy_on_day(self, day, default=arg_not_passed) -> ClubDinghy:
        if default is arg_not_passed:
            default = no_club_dinghy

        return self.get(day, default)

    def unique_list_of_dinghies(self) -> ListOfClubDinghies:
        return ListOfClubDinghies(list(set(self.values())))

    def list_of_dinghies(self) -> ListOfClubDinghies:
        return ListOfClubDinghies(list(self.values()))

    def remove_club_boat_for_person_from_event_on_day(self, day):
        try:
            self.pop(day)
        except:
            pass


class ListOfClubDinghysAtEventOnDayForPeople(List[ClubDinghyAtEventOnDayForPerson]):
    @classmethod
    def from_list_of_cadets_at_event_with_id_and_club_dinghy(
        cls,
        list_of_cadets_at_event_with_id_and_club_dinghy: ListOfCadetAtEventWithIdAndClubDinghies,
        list_of_cadets: ListOfCadets,
        list_of_club_dinghies: ListOfClubDinghies,
    ):
        return cls(
            [
                ClubDinghyAtEventOnDayForPerson.from_cadet_at_event_with_club_dinghy_and_id(
                    cadet_at_event_with_club_dinghy_and_id=cadet_at_event_with_club_dinghy_and_id,
                    list_of_cadets=list_of_cadets,
                    list_of_club_dinghies=list_of_club_dinghies,
                )
                for cadet_at_event_with_club_dinghy_and_id in list_of_cadets_at_event_with_id_and_club_dinghy
            ]
        )

    @classmethod
    def from_list_of_volunteers_at_event_with_id_and_club_dinghy(
        cls,
        list_of_volunteers_at_event_with_id_and_club_dinghy: ListOfVolunteerAtEventWithIdAndClubDinghies,
        list_of_volunteers: ListOfVolunteers,
        list_of_club_dinghies: ListOfClubDinghies,
    ):
        return cls(
            [
                ClubDinghyAtEventOnDayForPerson.from_volunteer_at_event_with_club_dinghy_and_id(
                    volunteer_at_event_with_club_dinghy_and_id=volunteer_at_event_with_club_dinghy_and_id,
                    list_of_volunteers=list_of_volunteers,
                    list_of_club_dinghies=list_of_club_dinghies,
                )
                for volunteer_at_event_with_club_dinghy_and_id in list_of_volunteers_at_event_with_id_and_club_dinghy
            ]
        )

    def unique_list_of_people(self):
        list_of_people = [cadet_and_boat.person for cadet_and_boat in self]
        return list(set(list_of_people))

    def dict_of_days_and_club_dinghies_for_people(
        self, person: Union[Cadet, Volunteer]
    ) -> DictOfDaysAndClubDinghiesAtEventForPerson:
        subset_for_person = self.subset_for_person(person)

        return DictOfDaysAndClubDinghiesAtEventForPerson(
            dict(
                [
                    (cadet_and_boat.day, cadet_and_boat.club_dinghy)
                    for cadet_and_boat in subset_for_person
                ]
            )
        )

    def subset_for_person(self, person: Union[Cadet, Volunteer]):
        return ListOfClubDinghysAtEventOnDayForPeople(
            [
                cadet_and_boat
                for cadet_and_boat in self
                if cadet_and_boat.person == person
            ]
        )

class DictOfPeopleAndClubDinghiesAtEvent(
    Dict[Union[Cadet, Volunteer], DictOfDaysAndClubDinghiesAtEventForPerson]
):
    pass


class DEPRECATE_DictOfPeopleAndClubDinghiesAtEvent(
    Dict[Union[Cadet, Volunteer], DictOfDaysAndClubDinghiesAtEventForPerson]
):
    def __init__(
        self,
        raw_dict,
        event: Event,
        list_of_cadets_at_event_with_id_and_club_dinghy: ListOfCadetAtEventWithIdAndClubDinghies,
        list_of_club_dinghies: ListOfClubDinghies,
        list_of_volunteers_with_ids_and_club_dinghies_at_event: ListOfVolunteerAtEventWithIdAndClubDinghies,
    ):
        super().__init__(raw_dict)

        self._list_of_cadets_at_event_with_id_and_club_dinghy = (
            list_of_cadets_at_event_with_id_and_club_dinghy
        )
        self._list_of_club_dinghies = list_of_club_dinghies
        self._event = event
        self._list_of_volunteers_with_ids_and_club_dinghies_at_event = (
            list_of_volunteers_with_ids_and_club_dinghies_at_event
        )

    def copy_club_dinghy_for_instructor_across_all_days(
        self, days_available: List[Day], volunteer: Volunteer, club_dinghy: ClubDinghy
    ):
        for day in days_available:
            self.allocate_club_boat_on_day(volunteer, day, club_dinghy)

    def list_of_volunteers_on_day_currently_allocated_to_club_dinghy(
        self, day: Day, club_dinghy: ClubDinghy
    ) -> ListOfVolunteers:
        list_of_volunteers = self.list_of_volunteers
        list_of_volunteers = [
            volunteer
            for volunteer in list_of_volunteers
            if self.club_dinghys_for_person(volunteer).has_specific_dinghy_on_day(
                day=day, dinghy=club_dinghy
            )
        ]

        return ListOfVolunteers(list_of_volunteers)

    def allocate_club_boat_on_day(
        self, person: Union[Cadet, Volunteer], day: Day, club_boat: ClubDinghy
    ):
        boats_for_person = self.club_dinghys_for_person(person)
        boats_for_person.allocate_club_boat_on_day(day=day, club_boat=club_boat)
        self[person] = boats_for_person

        if type(person) is Cadet:
            self.list_of_cadets_at_event_with_id_and_club_dinghy.update_allocation_for_cadet_on_day(
                cadet_id=person.id, day=day, club_dinghy_id=club_boat.id
            )
        elif type(person) is Volunteer:
            self.list_of_volunteers_with_ids_and_club_dinghies_at_event.update_allocation_for_volunteer_on_day(
                volunteer_id=person.id, day=day, club_dinghy_id=club_boat.id
            )
        else:
            raise "Unknown type %s" % type(person)

    def unique_sorted_list_of_allocated_club_dinghys_allocated_at_event(
        self,
    ) -> ListOfClubDinghies:
        dinghies_for_peoeple = [
            dict_of_dinghies.unique_list_of_dinghies()
            for dict_of_dinghies in self.values()
        ]
        all_dinghies_as_single_list = flatten(dinghies_for_peoeple)
        sorted_list = [
            dinghy
            for dinghy in self.list_of_club_dinghies
            if dinghy in all_dinghies_as_single_list
        ]

        return ListOfClubDinghies(sorted_list)

    def remove_person_from_event(self, person: Union[Cadet, Volunteer]):
        current_allocation = self.club_dinghys_for_person(person)
        if len(current_allocation) == 0:
            return []
        for day in self.event.days_in_event():
            self.remove_persons_club_boat_allocation_on_day(person=person, day=day)

        try:
            self.pop(person)
        except:
            return []

        return [" - removed club boat allocation %s" % str(current_allocation)]

    def remove_persons_club_boat_allocation_on_day(
        self, person: Union[Cadet, Volunteer], day: Day
    ):
        current_allocation = self.club_dinghys_for_person(person)
        current_allocation.remove_club_boat_for_person_from_event_on_day(day)
        self[person] = current_allocation

        if type(person) is Cadet:
            self.list_of_cadets_at_event_with_id_and_club_dinghy.delete_allocation_for_cadet_on_day(
                cadet_id=person.id, day=day
            )
        elif type(person) is Volunteer:
            self._list_of_volunteers_with_ids_and_club_dinghies_at_event.delete_allocation_for_volunteer_on_day(
                volunteer_id=person.id, day=day
            )
        else:
            raise "Unknown type %s" % type(person)

    def club_dinghys_for_person(
        self,
        person: Union[Cadet, Volunteer],
    ) -> DictOfDaysAndClubDinghiesAtEventForPerson:
        return self.get(person, DictOfDaysAndClubDinghiesAtEventForPerson())

    @property
    def list_of_club_dinghies(self) -> ListOfClubDinghies:
        return self._list_of_club_dinghies

    @property
    def list_of_cadets_at_event_with_id_and_club_dinghy(
        self,
    ) -> ListOfCadetAtEventWithIdAndClubDinghies:
        return self._list_of_cadets_at_event_with_id_and_club_dinghy

    @property
    def event(self) -> Event:
        return self._event

    @property
    def list_of_cadets(self) -> ListOfCadets:
        list_of_people = [
            person for person in list(self.keys()) if type(person) is Cadet
        ]
        return ListOfCadets(list_of_people)

    @property
    def list_of_volunteers(self) -> ListOfVolunteers:
        list_of_people = [
            person for person in list(self.keys()) if type(person) is Volunteer
        ]
        return ListOfVolunteers(list_of_people)

    @property
    def list_of_volunteers_with_ids_and_club_dinghies_at_event(
        self,
    ) -> ListOfVolunteerAtEventWithIdAndClubDinghies:
        return self._list_of_volunteers_with_ids_and_club_dinghies_at_event


def compose_dict_of_people_and_club_dinghies_at_event(
    event_id: str,
    list_of_events: ListOfEvents,
    list_of_cadets: ListOfCadets,
    list_of_club_dinghies: ListOfClubDinghies,
    list_of_cadets_at_event_with_id_and_club_dinghy: ListOfCadetAtEventWithIdAndClubDinghies,
    list_of_volunteers_with_ids_and_club_dinghies_at_event: ListOfVolunteerAtEventWithIdAndClubDinghies,
    list_of_volunteers: ListOfVolunteers,
) -> DEPRECATE_DictOfPeopleAndClubDinghiesAtEvent:
    event = list_of_events.event_with_id(event_id)
    raw_dict_cadets = compose_raw_dict_of_cadets_and_club_dinghies_at_event(
        list_of_cadets=list_of_cadets,
        list_of_club_dinghies=list_of_club_dinghies,
        list_of_cadets_at_event_with_id_and_club_dinghy=list_of_cadets_at_event_with_id_and_club_dinghy,
    )
    raw_dict_volunteers = compose_raw_dict_of_volunteers_and_club_dinghies_at_event(
        list_of_volunteers=list_of_volunteers,
        list_of_club_dinghies=list_of_club_dinghies,
        list_of_volunteers_with_ids_and_club_dinghies_at_event=list_of_volunteers_with_ids_and_club_dinghies_at_event,
    )
    raw_dict = {}
    raw_dict.update(raw_dict_cadets)
    raw_dict.update(raw_dict_volunteers)

    return DEPRECATE_DictOfPeopleAndClubDinghiesAtEvent(
        raw_dict=raw_dict,
        event=event,
        list_of_cadets_at_event_with_id_and_club_dinghy=list_of_cadets_at_event_with_id_and_club_dinghy,
        list_of_club_dinghies=list_of_club_dinghies,
        list_of_volunteers_with_ids_and_club_dinghies_at_event=list_of_volunteers_with_ids_and_club_dinghies_at_event,
    )


def compose_raw_dict_of_cadets_and_club_dinghies_at_event(
    list_of_cadets: ListOfCadets,
    list_of_club_dinghies: ListOfClubDinghies,
    list_of_cadets_at_event_with_id_and_club_dinghy: ListOfCadetAtEventWithIdAndClubDinghies,
) -> Dict[Cadet, DictOfDaysAndClubDinghiesAtEventForPerson]:
    list_of_club_dinghies_at_event_on_day_for_cadet = ListOfClubDinghysAtEventOnDayForPeople.from_list_of_cadets_at_event_with_id_and_club_dinghy(
        list_of_club_dinghies=list_of_club_dinghies,
        list_of_cadets=list_of_cadets,
        list_of_cadets_at_event_with_id_and_club_dinghy=list_of_cadets_at_event_with_id_and_club_dinghy,
    )

    cadets_at_event = (
        list_of_club_dinghies_at_event_on_day_for_cadet.unique_list_of_people()
    )

    return dict(
        [
            (
                cadet,
                list_of_club_dinghies_at_event_on_day_for_cadet.dict_of_days_and_club_dinghies_for_people(
                    cadet
                ),
            )
            for cadet in cadets_at_event
        ]
    )


def compose_raw_dict_of_volunteers_and_club_dinghies_at_event(
    list_of_volunteers: ListOfVolunteers,
    list_of_club_dinghies: ListOfClubDinghies,
    list_of_volunteers_with_ids_and_club_dinghies_at_event: ListOfVolunteerAtEventWithIdAndClubDinghies,
) -> Dict[Volunteer, DictOfDaysAndClubDinghiesAtEventForPerson]:
    list_of_club_dinghies_at_event_on_day_for_volunteer = ListOfClubDinghysAtEventOnDayForPeople.from_list_of_volunteers_at_event_with_id_and_club_dinghy(
        list_of_club_dinghies=list_of_club_dinghies,
        list_of_volunteers=list_of_volunteers,
        list_of_volunteers_at_event_with_id_and_club_dinghy=list_of_volunteers_with_ids_and_club_dinghies_at_event,
    )

    volunteers_at_event = (
        list_of_club_dinghies_at_event_on_day_for_volunteer.unique_list_of_people()
    )

    return dict(
        [
            (
                volunteer,
                list_of_club_dinghies_at_event_on_day_for_volunteer.dict_of_days_and_club_dinghies_for_people(
                    volunteer
                ),
            )
            for volunteer in volunteers_at_event
        ]
    )
