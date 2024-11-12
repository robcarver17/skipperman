from dataclasses import dataclass
from typing import List

from app.objects.events import Event
from app.objects.volunteer_at_event_with_id import VolunteerAtEventWithId

from app.objects.volunteers import Volunteer

from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject
from app.objects.day_selectors import (
    DaySelector,
    Day,
)
from app.objects.exceptions import missing_data, MissingData


@dataclass
class DEPRECATE_VolunteerAtEvent(GenericSkipperManObject):
    volunteer: Volunteer
    event: Event
    availablity: DaySelector
    list_of_associated_cadet_id: list
    preferred_duties: str = ""  ## information only
    same_or_different: str = ""  ## information only
    any_other_information: str = (
        ""  ## information only - double counted as required twice
    )
    notes: str = ""

    def available_on_day(self, day: Day):
        return self.availablity.available_on_day(day)

    @property
    def name(self):
        return self.volunteer.name

    @property
    def volunteer_id(self):
        return self.volunteer.id

    @classmethod
    def from_volunteer_and_voluteer_at_event_with_id(
        cls,
        volunteer: Volunteer,
        event: Event,
        volunteer_at_event_with_id=VolunteerAtEventWithId,
    ):
        return cls(
            volunteer=volunteer,
            event=event,
            availablity=volunteer_at_event_with_id.availablity,
            list_of_associated_cadet_id=volunteer_at_event_with_id.list_of_associated_cadet_id,
            preferred_duties=volunteer_at_event_with_id.preferred_duties,
            same_or_different=volunteer_at_event_with_id.same_or_different,
            any_other_information=volunteer_at_event_with_id.any_other_information,
            notes=volunteer_at_event_with_id.notes,
        )


class ListOfVolunteersAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return DEPRECATE_VolunteerAtEvent

    def volunteer_at_event_with_id(
        self, volunteer_id: str, return_missing_data: bool = False
    ):
        try:
            idx = self.list_of_volunteer_ids().index(volunteer_id)
        except:
            if return_missing_data:
                return missing_data
            else:
                raise MissingData

        return self[idx]

    def list_of_volunteer_ids(self) -> List[str]:
        return [volunteer_at_event.volunteer_id for volunteer_at_event in self]

    def sort_by_list_of_volunteer_ids(self, list_of_ids) -> "ListOfVolunteersAtEvent":
        new_list_of_volunteers_at_event = [
            self.volunteer_at_event_with_id(id, return_missing_data=True)
            for id in list_of_ids
        ]
        new_list_of_volunteers_at_event = [
            volunteer_at_event
            for volunteer_at_event in new_list_of_volunteers_at_event
            if volunteer_at_event is not missing_data
        ]

        return ListOfVolunteersAtEvent(new_list_of_volunteers_at_event)
