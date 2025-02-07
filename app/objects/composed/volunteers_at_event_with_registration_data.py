from dataclasses import dataclass
from typing import Dict

from app.objects.events import Event, ListOfEvents
from app.objects.exceptions import MissingData, arg_not_passed

from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.volunteer_at_event_with_id import (
    ListOfVolunteersAtEventWithId,
    VolunteerAtEventWithId,
)
from app.objects.cadets import ListOfCadets

from app.objects.day_selectors import DaySelector, Day


@dataclass
class RegistrationDataForVolunteerAtEvent:
    availablity: DaySelector
    list_of_associated_cadets: ListOfCadets
    preferred_duties: str = ""  ## information only
    same_or_different: str = ""  ## information only
    any_other_information: str = (
        ""  ## information only - double counted as required twice
    )
    notes: str = ""

    def clear_user_data(self):
        self.any_other_information = ""
        self.notes = ""


    @classmethod
    def from_volunteer_at_event_with_id(
        cls,
        volunteer_at_event_with_id: VolunteerAtEventWithId,
        list_of_cadets: ListOfCadets,
    ):
        return cls(
            availablity=volunteer_at_event_with_id.availablity,
            list_of_associated_cadets=list_of_cadets.subset_from_list_of_ids_retaining_order(
                list_of_ids=volunteer_at_event_with_id.list_of_associated_cadet_id,
            ),
            preferred_duties=volunteer_at_event_with_id.preferred_duties,
            same_or_different=volunteer_at_event_with_id.same_or_different,
            any_other_information=volunteer_at_event_with_id.any_other_information,
            notes=volunteer_at_event_with_id.notes,
        )


class DictOfRegistrationDataForVolunteerAtEvent(
    Dict[Volunteer, RegistrationDataForVolunteerAtEvent]
):
    def __init__(
        self,
        raw_dict: Dict[Volunteer, RegistrationDataForVolunteerAtEvent],
        event: Event,
        list_of_volunteers_at_event_with_id: ListOfVolunteersAtEventWithId,
    ):
        super().__init__(raw_dict)
        self._event = event
        self._list_of_volunteers_at_event_with_id = list_of_volunteers_at_event_with_id

    def update_volunteer_notes_at_event(
            self, volunteer: Volunteer, new_notes: str
    ):
        volunteer_data = self.get_data_for_volunteer(volunteer)
        volunteer_data.notes = new_notes
        self.list_of_volunteers_at_event_with_id.update_notes(volunteer=volunteer, new_notes=new_notes)

    def clear_user_data(self):
        for registration_data_for_volunteer in self.values():
            registration_data_for_volunteer.clear_user_data()

        self.list_of_volunteers_at_event_with_id.clear_user_data()

    def sort_by_list_of_volunteers(self, list_of_volunteers: ListOfVolunteers):
        new_raw_dict = dict(
            [(volunteer, self[volunteer]) for volunteer in list_of_volunteers]
        )

        return DictOfRegistrationDataForVolunteerAtEvent(
            raw_dict=new_raw_dict,
            list_of_volunteers_at_event_with_id=self.list_of_volunteers_at_event_with_id.sort_by_list_of_volunteer_ids(
                list_of_volunteers.list_of_ids
            ),
            event=self.event,
        )

    def drop_volunteer(self, volunteer: Volunteer):
        self.pop(volunteer)
        self.list_of_volunteers_at_event_with_id.remove_volunteer_with_id(volunteer.id)

    def make_volunteer_available_on_day(self, volunteer: Volunteer, day: Day):
        registration_for_volunteer = self.get_data_for_volunteer(volunteer)
        registration_for_volunteer.availablity.make_available_on_day(day)
        self.list_of_volunteers_at_event_with_id.make_volunteer_available_on_day(
            volunteer=volunteer, day=day
        )

    def make_volunteer_unavailable_on_day(self, volunteer: Volunteer, day: Day):
        registration_for_volunteer = self.get(volunteer)
        registration_for_volunteer.availablity.make_unavailable_on_day(day)
        self.list_of_volunteers_at_event_with_id.make_volunteer_unavailable_on_day(
            volunteer=volunteer, day=day
        )

    def get_data_for_volunteer(self, volunteer: Volunteer, default = arg_not_passed):
        try:
            return self.get(volunteer)
        except:
            if default is arg_not_passed:
                raise MissingData("Volunteer %s not found" % str(volunteer))
            else:
                return default

    @property
    def event(self) -> Event:
        return self._event

    @property
    def list_of_volunteers_at_event_with_id(self) -> ListOfVolunteersAtEventWithId:
        return self._list_of_volunteers_at_event_with_id

    def list_of_volunteers_at_event(self):
        return ListOfVolunteers(list(self.keys()))


def compose_dict_of_registration_data_for_volunteer_at_event(
    event_id: str,
    list_of_volunteers: ListOfVolunteers,
    list_of_cadets: ListOfCadets,
    list_of_volunteers_at_event_with_id: ListOfVolunteersAtEventWithId,
    list_of_events: ListOfEvents,
) -> DictOfRegistrationDataForVolunteerAtEvent:
    event = list_of_events.object_with_id(event_id)

    raw_dict = compose_raw_dict_of_registration_data_for_volunteer_at_event(
        list_of_volunteers=list_of_volunteers,
        list_of_cadets=list_of_cadets,
        list_of_volunteers_at_event_with_id=list_of_volunteers_at_event_with_id,
    )

    return DictOfRegistrationDataForVolunteerAtEvent(
        raw_dict=raw_dict,
        event=event,
        list_of_volunteers_at_event_with_id=list_of_volunteers_at_event_with_id,
    )


def compose_raw_dict_of_registration_data_for_volunteer_at_event(
    list_of_volunteers: ListOfVolunteers,
    list_of_cadets: ListOfCadets,
    list_of_volunteers_at_event_with_id: ListOfVolunteersAtEventWithId,
) -> Dict[Volunteer, RegistrationDataForVolunteerAtEvent]:
    return dict(
        [
            (
                list_of_volunteers.volunteer_with_id(
                    volunteer_at_event_with_id.volunteer_id
                ),
                RegistrationDataForVolunteerAtEvent.from_volunteer_at_event_with_id(
                    volunteer_at_event_with_id=volunteer_at_event_with_id,
                    list_of_cadets=list_of_cadets,
                ),
            )
            for volunteer_at_event_with_id in list_of_volunteers_at_event_with_id
        ]
    )
