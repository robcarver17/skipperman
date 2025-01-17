from dataclasses import dataclass
from typing import List

from app.data_access.configuration.configuration import UNABLE_TO_VOLUNTEER_KEYWORD

from app.objects.cadets import Cadet

from app.objects.day_selectors import (
    DaySelector,
    union_across_day_selectors,
    create_day_selector_from_short_form_text,
)
from app.objects.exceptions import missing_data
from app.objects.registration_status import RegistrationStatus
from app.objects.utils import we_are_not_the_same
from app.objects.volunteers import Volunteer


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
    day_availability: str
    weekend_availability: str
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


def relevant_information_requires_clarification(
    volunteer: Volunteer,
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> str:
    issues = NO_ISSUES_WITH_VOLUNTEER

    list_of_status = [
        relevant_information.identify.self_declared_status
        for relevant_information in list_of_relevant_information
    ]
    list_of_preferred = [
        relevant_information.availability.preferred_duties
        for relevant_information in list_of_relevant_information
    ]
    list_of_availability = [
        suggested_volunteer_availability(relevant_information.availability)
        for relevant_information in list_of_relevant_information
    ]
    list_of_cadet_availability = [
        relevant_information.availability.cadet_availability
        for relevant_information in list_of_relevant_information
    ]

    list_of_same_or_different = [
        relevant_information.availability.same_or_different
        for relevant_information in list_of_relevant_information
    ]

    any_status_is_unable = any(
        [
            status
            for status in list_of_status
            if UNABLE_TO_VOLUNTEER_KEYWORD in status.lower()
        ]
    )
    availability_conflict = we_are_not_the_same(list_of_availability)
    if availability_conflict:
        ## cannot check so say false
        cadet_vs_volunteer_availability_conflict = False
    else:
        volunteer_availability = list_of_availability[0]  ## all the same
        cadet_vs_volunteer_availability_conflict = (
            is_volunteer_available_on_days_when_cadet_not_attending(
                volunteer_availability=volunteer_availability,
                list_of_cadet_availability=list_of_cadet_availability,
            )
        )

    preferred_conflict = we_are_not_the_same(list_of_preferred)
    same_or_different_conflict = we_are_not_the_same(list_of_same_or_different)

    volunteer_name = volunteer.name
    if any_status_is_unable:
        issues += (
            "Volunteer %s says they are unable to volunteer, according to at least one registration. "
            % volunteer_name
        )
    if availability_conflict:
        issues += (
            "Inconsistency between availability for %s across registrations. "
            % volunteer_name
        )
    if cadet_vs_volunteer_availability_conflict:
        issues += (
            "Volunteer %s is available on days when cadet is not. " % volunteer_name
        )
    if preferred_conflict:
        issues += (
            "Inconsistency on preferred duties across registrations for volunter %s . "
            % volunteer_name
        )
    if same_or_different_conflict:
        issues += (
            "Inconsistency on same/different duties across registrations for volunteer %s . "
            % volunteer_name
        )

    return issues


def is_volunteer_available_on_days_when_cadet_not_attending(
    volunteer_availability: DaySelector, list_of_cadet_availability: List[DaySelector]
) -> bool:
    all_cadets_availability = union_across_day_selectors(list_of_cadet_availability)
    for day in volunteer_availability.days_available():
        if not all_cadets_availability.available_on_day(day):
            return True

    return False


NO_ISSUES_WITH_VOLUNTEER = ""


def suggested_volunteer_availability(
    relevant_information: RelevantInformationForVolunteerAvailability,
) -> DaySelector:
    day_availability = relevant_information.day_availability
    weekend_availability = relevant_information.weekend_availability
    cadet_availability = relevant_information.cadet_availability

    if day_availability is not missing_data:
        return create_day_selector_from_short_form_text(day_availability)
    elif weekend_availability is not missing_data:
        return create_day_selector_from_short_form_text(weekend_availability)
    elif cadet_availability is not missing_data:
        return cadet_availability
    else:
        ## assume all
        raise Exception("No availability information")
