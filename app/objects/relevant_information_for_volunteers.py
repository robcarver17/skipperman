from dataclasses import dataclass
from typing import List

from app.objects.cadets import Cadet

from app.objects.day_selectors import (
    DaySelector,
)
from app.objects.registration_status import RegistrationStatus


@dataclass
class RelevantInformationForVolunteerIdentification:
    passed_name: str
    cadet: Cadet
    registered_by_firstname: str
    self_declared_status: str
    any_other_information: str  ## information only - double counted as required twice

    @property
    def cadet_surname(self):
        return self.cadet.surname


@dataclass
class RelevantInformationForVolunteerDetails:  ##copied across
    food_preference: str
    any_other_information: str  ## information only - double counted as required twice


@dataclass
class RelevantInformationForVolunteerAvailability:
    volunteer_availablity: DaySelector
    cadet_availability: DaySelector
    preferred_duties: str  ## information only
    same_or_different: str  ## information only
    any_other_information: str  ## information only - double counted as required twice
    row_status: RegistrationStatus


@dataclass
class RelevantInformationForVolunteer:
    identify: RelevantInformationForVolunteerIdentification
    availability: RelevantInformationForVolunteerAvailability
    details: RelevantInformationForVolunteerDetails


missing_relevant_information = object()


class ListOfRelevantInformationForVolunteer(List[RelevantInformationForVolunteer]):
    def __init__(
        self, list_of_relevant_information: List[RelevantInformationForVolunteer]
    ):
        super().__init__(list_of_relevant_information)

    def all_cancelled_or_deleted(self) -> bool:
        cancelled_or_deleted = [
            get_row_status_cancelled_or_deleted_from_relevant_information(
                relevant_information
            )
            for relevant_information in self
        ]

        return all(cancelled_or_deleted)


def get_row_status_cancelled_or_deleted_from_relevant_information(
    relevant_information: RelevantInformationForVolunteer,
) -> bool:
    if relevant_information is missing_relevant_information:
        return True

    row_status = relevant_information.availability.row_status
    cancelled_or_deleted = row_status.is_cancelled_or_deleted

    return cancelled_or_deleted
