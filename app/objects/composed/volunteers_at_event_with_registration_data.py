from dataclasses import dataclass
from typing import Dict


from app.objects.utilities.exceptions import MissingData, arg_not_passed

from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.volunteer_at_event_with_id import (
    VolunteerAtEventWithId,
)
from app.objects.cadets import ListOfCadets

from app.objects.day_selectors import DaySelector, Day


@dataclass
class RegistrationDataForVolunteerAtEvent:
    availablity: DaySelector
    list_of_associated_cadets: ListOfCadets  ## backward compatability not used
    self_declared_status: str = ""  ## info only
    preferred_duties: str = ""  ## information only
    same_or_different: str = ""  ## information only
    any_other_information: str = (
        ""  ## information only - double counted as required twice
    )
    notes: str = ""

    @classmethod
    def from_volunteer_at_event_with_id(
        cls,
        volunteer_at_event_with_id: VolunteerAtEventWithId,
    ):
        return cls(
            availablity=volunteer_at_event_with_id.availablity,
            list_of_associated_cadets=ListOfCadets([]),
            preferred_duties=volunteer_at_event_with_id.preferred_duties,
            same_or_different=volunteer_at_event_with_id.same_or_different,
            any_other_information=volunteer_at_event_with_id.any_other_information,
            notes=volunteer_at_event_with_id.notes,
            self_declared_status=volunteer_at_event_with_id.self_declared_status,
        )


class DictOfRegistrationDataForVolunteerAtEvent(
    Dict[Volunteer, RegistrationDataForVolunteerAtEvent]
):
    def get_data_for_volunteer(
        self, volunteer: Volunteer, default=arg_not_passed
    ) -> RegistrationDataForVolunteerAtEvent:
        data = self.get(volunteer, default)
        if data is arg_not_passed:
            raise MissingData("Volunteer %s not found" % str(volunteer))

        return data

    def list_of_volunteers_at_event(self):
        return ListOfVolunteers(list(self.keys()))
