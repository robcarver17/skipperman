from typing import List

from app.data_access.configuration.configuration import UNABLE_TO_VOLUNTEER_KEYWORD
from app.objects.day_selectors import DaySelector, Day, union_across_day_selectors
from app.objects.relevant_information_for_volunteers import (
    ListOfRelevantInformationForVolunteer,
)
from app.objects.utils import we_are_not_the_same
from app.objects.volunteers import Volunteer


def relevant_information_requires_clarification(
    volunteer: Volunteer,
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> str:
    issues = NO_ISSUES_WITH_VOLUNTEER
    volunteer_name = volunteer.name

    issues = add_status_conflict_to_issues_list(
        list_of_relevant_information=list_of_relevant_information,
        volunteer_name=volunteer_name,
        issues=issues,
    )
    issues = add_availablity_conflict_to_issues_list(
        list_of_relevant_information=list_of_relevant_information,
        volunteer_name=volunteer_name,
        issues=issues,
    )
    issues = add_same_or_different_conflict_to_list_of_issues(
        list_of_relevant_information=list_of_relevant_information,
        volunteer_name=volunteer_name,
        issues=issues,
    )
    issues = add_preferred_conflict_to_list_of_isses(
        list_of_relevant_information=list_of_relevant_information,
        volunteer_name=volunteer_name,
        issues=issues,
    )

    return issues


def add_status_conflict_to_issues_list(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer_name: str,
    issues: str,
):

    list_of_status = [
        relevant_information.identify.self_declared_status
        for relevant_information in list_of_relevant_information
    ]

    any_status_is_unable = any(
        [
            status
            for status in list_of_status
            if UNABLE_TO_VOLUNTEER_KEYWORD in status.lower()
        ]
    )
    if any_status_is_unable:
        issues += (
            "Volunteer %s says they are unable to volunteer, according to at least one registration. "
            % volunteer_name
        )
    else:
        print("No issues with status conflict")

    return issues


def add_availablity_conflict_to_issues_list(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer_name: str,
    issues: str,
):

    list_of_availability = [
        relevant_information.availability.volunteer_availablity
        for relevant_information in list_of_relevant_information
    ]
    print("volunteer availability %s" % str(list_of_availability))

    conflict_with_availability_declared_by_volunteer = we_are_not_the_same(
        list_of_availability
    )
    if conflict_with_availability_declared_by_volunteer:
        issues += (
            "Inconsistency between availability for %s across registrations for different sailors. "
            % volunteer_name
        )
    else:
        ## Volunteer consistent let's check cadets
        issues = add_cadet_vs_volunteer_availablity_conflict_to_issues_list(
            list_of_relevant_information=list_of_relevant_information,
            volunteer_name=volunteer_name,
            issues=issues,
        )

    return issues


def add_cadet_vs_volunteer_availablity_conflict_to_issues_list(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer_name: str,
    issues: str,
):

    volunteer_availability = list_of_relevant_information[
        0
    ].availability.volunteer_availablity  ## all the same if we get here
    list_of_cadet_availability = [
        relevant_information.availability.cadet_availability
        for relevant_information in list_of_relevant_information
    ]

    print(
        "volunteer availability (alll same) %s cadet availability %s"
        % (str(volunteer_availability), str(list_of_cadet_availability))
    )
    cadet_vs_volunteer_availability_conflict_on_days = (
        list_of_days_when_volunteer_available_when_cadet_not_attending(
            volunteer_availability=volunteer_availability,
            list_of_cadet_availability=list_of_cadet_availability,
        )
    )
    if len(cadet_vs_volunteer_availability_conflict_on_days) > 0:
        cadet_vs_volunteer_availability_conflict_on_days_as_str = ", ".join(
            [day.name for day in cadet_vs_volunteer_availability_conflict_on_days]
        )
        issues += (
            "Volunteer %s is available on the following days when cadet is not: %s. "
            % (volunteer_name, cadet_vs_volunteer_availability_conflict_on_days_as_str)
        )
    else:
        print("No issues with availability")

    return issues


def list_of_days_when_volunteer_available_when_cadet_not_attending(
    volunteer_availability: DaySelector, list_of_cadet_availability: List[DaySelector]
) -> List[Day]:
    all_cadets_availability = union_across_day_selectors(list_of_cadet_availability)
    print("All cadets availability as single union %s" % str(all_cadets_availability))
    bad_days = [
        day
        for day in volunteer_availability.days_available()
        if not all_cadets_availability.available_on_day(day)
    ]

    print("bad days %s" % str(bad_days))

    return bad_days


def add_preferred_conflict_to_list_of_isses(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer_name: str,
    issues: str,
):
    list_of_preferred = [
        relevant_information.availability.preferred_duties
        for relevant_information in list_of_relevant_information
    ]
    preferred_conflict = we_are_not_the_same(list_of_preferred)
    if preferred_conflict:
        issues += (
            "Inconsistency on preferred duties across registrations for volunter %s . "
            % volunteer_name
        )
    else:
        print("No issues with preferred duties")

    return issues


def add_same_or_different_conflict_to_list_of_issues(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer_name: str,
    issues: str,
):
    list_of_same_or_different = [
        relevant_information.availability.same_or_different
        for relevant_information in list_of_relevant_information
    ]
    same_or_different_conflict = we_are_not_the_same(list_of_same_or_different)
    if same_or_different_conflict:
        issues += (
            "Inconsistency on same/different duties across registrations for volunteer %s . "
            % volunteer_name
        )
    else:
        print("No issues with same/different duties")

    return issues


NO_ISSUES_WITH_VOLUNTEER = ""
