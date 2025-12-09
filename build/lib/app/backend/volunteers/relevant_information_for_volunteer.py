from app.objects.registration_data import (
    check_any_status_is_unable_given_list_of_status,
)
from app.objects.relevant_information_for_volunteers import (
    ListOfRelevantInformationForVolunteer,
)
from app.objects.utilities.utils import we_are_not_the_same, simplify_and_display
from app.objects.volunteers import Volunteer
from app.objects.event_warnings import (
    EventWarningLog,
    ListOfEventWarnings,
    VOLUNTEER_AVAILABILITY,
    VOLUNTEER_PREFERENCE,
)
from app.data_access.configuration.fixed import LOW_PRIORITY, HIGH_PRIORITY


def relevant_information_requires_clarification(
    volunteer: Volunteer,
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
) -> ListOfEventWarnings:
    issues = []
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

    return ListOfEventWarnings(issues)


def check_any_status_is_unable(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
):
    list_of_status = [
        relevant_information.identify.self_declared_status
        for relevant_information in list_of_relevant_information
    ]

    any_status_is_unable = check_any_status_is_unable_given_list_of_status(
        list_of_status
    )
    return any_status_is_unable


def add_status_conflict_to_issues_list(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer_name: str,
    issues: list,
):
    list_of_status = [
        relevant_information.identify.self_declared_status
        for relevant_information in list_of_relevant_information
    ]

    if check_any_status_is_unable(list_of_relevant_information):
        issues.append(
            EventWarningLog(
                priority=HIGH_PRIORITY,
                category=VOLUNTEER_AVAILABILITY,
                warning="Volunteer %s says they are unable to volunteer, according to at least one registration: status in registration %s "
                % (volunteer_name, simplify_and_display(list_of_status)),
                auto_refreshed=False,
            )
        )
    else:
        print("No issues with status conflict")

    return issues


def add_availablity_conflict_to_issues_list(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer_name: str,
    issues: list,
):
    list_of_availability = [
        relevant_information.availability.volunteer_availablity
        for relevant_information in list_of_relevant_information
    ]

    conflict_with_availability_declared_by_volunteer = we_are_not_the_same(
        list_of_availability
    )
    if conflict_with_availability_declared_by_volunteer:
        issues.append(
            EventWarningLog(
                priority=HIGH_PRIORITY,
                category=VOLUNTEER_AVAILABILITY,
                auto_refreshed=False,
                warning="Inconsistency between availability for %s across registrations for different sailors: %s "
                % (
                    volunteer_name,
                    simplify_and_display(
                        [
                            available.days_available_as_str()
                            for available in list_of_availability
                        ],
                        linker="; "
                    ),
                ),
            )
        )

    return issues


def add_preferred_conflict_to_list_of_isses(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer_name: str,
    issues: list,
):
    list_of_preferred = [
        relevant_information.availability.preferred_duties
        for relevant_information in list_of_relevant_information
    ]
    preferred_conflict = we_are_not_the_same(list_of_preferred)
    if preferred_conflict:
        issues.append(
            EventWarningLog(
                priority=LOW_PRIORITY,
                category=VOLUNTEER_PREFERENCE,
                auto_refreshed=False,
                warning="Inconsistency on preferred duties across registrations for volunteer %s: %s "
                % (volunteer_name, simplify_and_display(list_of_preferred, linker="; ")),
            )
        )

    else:
        print("No issues with preferred duties")

    return issues


def add_same_or_different_conflict_to_list_of_issues(
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer_name: str,
    issues: list,
):
    list_of_same_or_different = [
        relevant_information.availability.same_or_different
        for relevant_information in list_of_relevant_information
    ]
    same_or_different_conflict = we_are_not_the_same(list_of_same_or_different)
    if same_or_different_conflict:
        issues.append(
            EventWarningLog(
                priority=LOW_PRIORITY,
                category=VOLUNTEER_PREFERENCE,
                auto_refreshed=False,
                warning="Inconsistency on same/different duties across registrations for volunteer %s: %s "
                % (volunteer_name, simplify_and_display(list_of_same_or_different, linker="; ")),
            )
        )

    else:
        print("No issues with same/different duties")

    return issues
