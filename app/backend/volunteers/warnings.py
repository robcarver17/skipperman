from copy import copy
from typing import List, Callable, Dict

from app.backend.registration_data.volunter_relevant_information import get_volunteer_from_relevant_information
from app.objects.composed.volunteer_roles import (
    empty_if_qualified_for_role_else_warnings,
)
from app.objects.composed.volunteers_at_event_with_registration_data import RegistrationDataForVolunteerAtEvent

from app.objects.composed.volunteers_with_all_event_data import AllEventDataForVolunteer
from app.objects.identified_volunteer_at_event import RowIDAndIndex
from app.objects.volunteers import Volunteer

from app.data_access.store.object_store import ObjectStore

from app.backend.registration_data.identified_cadets_at_event import (
    get_all_rows_in_registration_data_which_have_been_identified_for_a_specific_cadet,
)

from app.backend.groups.previous_groups import (
    get_dict_of_all_event_allocations_for_single_cadet,
)
from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_all_event_data_for_volunteers,
)
from app.backend.rota.volunteers_and_cadets import (
    list_of_cadet_groups_associated_with_volunteer,
)
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_availability_dict_for_active_cadets_at_event,
    get_list_of_active_cadets_at_event,
)
from app.backend.registration_data.cadet_and_volunteer_connections_at_event import (
    get_list_of_volunteers_associated_with_cadet_at_event,
    get_list_of_cadets_associated_with_volunteer_at_event,
)

from app.objects.cadets import (
    ListOfCadets,
    Cadet,
    cadet_is_too_young_to_be_without_parent,
)
from app.objects.day_selectors import empty_day_selector, Day, DaySelector
from app.objects.events import Event
from app.objects.registration_data import get_volunteer_status_from_row
from app.objects.event_warnings import ListOfEventWarnings, MEDIUM_PRIORITY, CADET_WITHOUT_ADULT, \
    VOLUNTEER_AVAILABILITY, VOLUNTEER_GROUP, LOW_PRIORITY, LOWEST_PRIORITY, VOLUNTEER_UNCONNECTED, \
    VOLUNTEER_QUALIFICATION, HIGH_PRIORITY, VOLUNTEER_IDENTITY, VOLUNTEER_PREFERENCE
from app.backend.events.event_warnings import \
    get_list_of_warnings_at_event_for_categories_sorted_by_category_and_priority, process_warnings_into_warning_list


def process_all_warnings_for_rota(object_store: ObjectStore, event: Event):
    warn_on_volunteers_with_skipped_registration(
        object_store=object_store, event=event
    )
    warn_on_all_volunteers_availability_volunteers_missing(
        object_store=object_store, event=event
    )
    warn_on_all_volunteers_availability_sailors_missing(
        object_store=object_store, event=event
    )
    warn_on_all_volunteers_group(
        object_store=object_store, event=event
    )
    warn_on_all_volunteers_unconnected(
        object_store=object_store, event=event
    )
    warn_on_volunteer_qualifications(
        object_store=object_store, event=event
    )
    warn_on_cadets_which_should_have_volunteers(
        object_store=object_store, event=event
    )




def warn_on_all_volunteers_availability_volunteers_missing(
    object_store: ObjectStore, event: Event
):
    warnings = warn_on_all_volunteers_generic(
        object_store=object_store,
        event=event,
        warning_function=warn_about_single_volunteer_availablity_at_event_missing_volunteer,
    )

    process_warnings_into_warning_list(object_store=object_store, event=event,
                                       list_of_warnings=warnings, category=VOLUNTEER_AVAILABILITY,
                                       priority=LOW_PRIORITY)

def warn_on_all_volunteers_availability_sailors_missing(
    object_store: ObjectStore, event: Event
):
    warnings = warn_on_all_volunteers_generic(
        object_store=object_store,
        event=event,
        warning_function=warn_about_single_volunteer_availablity_at_event_missing_sailor,
    )

    process_warnings_into_warning_list(object_store=object_store, event=event,
                                       list_of_warnings=warnings, category=VOLUNTEER_AVAILABILITY,
                                       priority=MEDIUM_PRIORITY)

def warn_on_all_volunteers_group(object_store: ObjectStore, event: Event):
    warnings =  warn_on_all_volunteers_generic(
        object_store=object_store,
        event=event,
        warning_function=warn_about_single_volunteer_groups_at_event,
    )

    process_warnings_into_warning_list(object_store=object_store, event=event,
                                       list_of_warnings=warnings,
                                       category=VOLUNTEER_GROUP,
                                       priority=LOW_PRIORITY)


def warn_on_all_volunteers_unconnected(
    object_store: ObjectStore, event: Event
):
    warnings = warn_on_all_volunteers_generic(
        object_store=object_store,
        event=event,
        warning_function=warn_about_single_volunteer_with_no_cadet_at_event,
    )

    process_warnings_into_warning_list(object_store=object_store, event=event,
                                       list_of_warnings=warnings,
                                       category = VOLUNTEER_UNCONNECTED,
                                       priority=LOWEST_PRIORITY,
                                       )


def warn_on_volunteer_qualifications(
    object_store: ObjectStore, event: Event
):
    warnings= warn_on_all_volunteers_generic(
        object_store=object_store,
        event=event,
        warning_function=warn_about_single_volunteer_with_qualifications,
    )

    process_warnings_into_warning_list(object_store=object_store, event=event,
                                       list_of_warnings=warnings,
                                       category=VOLUNTEER_QUALIFICATION,
                                       priority=HIGH_PRIORITY)


def warn_on_all_volunteers_generic(
    object_store: ObjectStore, event: Event, warning_function: Callable
) -> List[str]:
    list_of_volunteers_at_event = get_dict_of_all_event_data_for_volunteers(
        object_store=object_store, event=event
    )

    list_of_warnings = []
    for volunteer, volunteer_event_data in list_of_volunteers_at_event.items():
        warnings_for_volunteer = warning_function(
            volunteer=volunteer,
            volunteer_event_data=volunteer_event_data,
            object_store=object_store,
            event=event,
        )
        list_of_warnings.append(warnings_for_volunteer)

    list_of_warnings = remove_empty_values_in_warning_list(list_of_warnings)

    return list_of_warnings


def warn_about_single_volunteer_with_qualifications(
    volunteer: Volunteer,
    event: Event,  ## not used but called by generic function so keep
    volunteer_event_data: AllEventDataForVolunteer,
    object_store: ObjectStore,  ## not used, ditto
) -> str:

    dict_of_skills = volunteer_event_data.volunteer_skills
    list_of_volunteer_roles = volunteer_event_data.roles_and_groups.list_of_roles()

    roles_with_warning = []
    for volunteer_role in list_of_volunteer_roles:
        warnings = empty_if_qualified_for_role_else_warnings(
            role=volunteer_role, dict_of_skills=dict_of_skills
        )
        if len(warnings) == 0:
            continue

        warning_text = "for %s needs: %s" % (volunteer_role.name, warnings)
        roles_with_warning.append(warning_text)

    if len(roles_with_warning) == 0:
        return ""

    roles_with_warning = list(set(roles_with_warning))
    warnings_as_str = ", ".join(roles_with_warning)

    return "%s is not qualified for role(s): %s" % (volunteer.name, warnings_as_str)


def warn_about_single_volunteer_groups_at_event(
    volunteer: Volunteer,
    event: Event,
    volunteer_event_data: AllEventDataForVolunteer,
    object_store: ObjectStore,
) -> str:
    group_warnings_for_volunteer = []

    list_of_cadet_groups = list_of_cadet_groups_associated_with_volunteer(
        event=event, volunteer=volunteer, object_store=object_store
    )

    has_lake_cadet = list_of_cadet_groups.has_lake_group()
    is_lake_volunteer = volunteer_event_data.roles_and_groups.is_on_lake_during_event()

    notes = copy(volunteer_event_data.registration_data.notes)
    if len(notes) > 0:
        notes = "(%s)" % notes

    if has_lake_cadet and is_lake_volunteer:
        group_warnings_for_volunteer.append(
            "Volunteer %s is in lake role, but has cadet at lake %s"
            % (volunteer.name, notes)
        )

    list_of_groups_for_volunteer = (
        volunteer_event_data.roles_and_groups.list_of_groups()
    )

    for group in list_of_groups_for_volunteer:
        if group in list_of_cadet_groups:
            if group.is_unallocated:
                continue
            group_warnings_for_volunteer.append(
                "Volunteer %s and cadet are both in group %s %s"
                % (volunteer.name, group.name, notes)
            )

    return ", ".join(group_warnings_for_volunteer)


def warn_about_single_volunteer_availablity_at_event_missing_volunteer(
    volunteer: Volunteer,
    event: Event,
    volunteer_event_data: AllEventDataForVolunteer,
    object_store: ObjectStore,
) -> str:

    active_connected_cadets = get_list_of_cadets_associated_with_volunteer_at_event(
        object_store=object_store, event=event, volunteer=volunteer
    )

    if len(active_connected_cadets) == 0:
        return ""
    return warn_about_volunteer_availablity_at_event_with_connected_cadets(
        event=event,
        volunteer=volunteer,
        object_store=object_store,
        volunteer_event_data=volunteer_event_data,
        active_connected_cadets=active_connected_cadets,
        missing_volunteers_if_true_otherwise_missing_cadets = True
    )


def warn_about_single_volunteer_availablity_at_event_missing_sailor(
    volunteer: Volunteer,
    event: Event,
    volunteer_event_data: AllEventDataForVolunteer,
    object_store: ObjectStore,
) -> str:

    active_connected_cadets = get_list_of_cadets_associated_with_volunteer_at_event(
        object_store=object_store, event=event, volunteer=volunteer
    )

    if len(active_connected_cadets) == 0:
        return ""
    return warn_about_volunteer_availablity_at_event_with_connected_cadets(
        event=event,
        volunteer=volunteer,
        object_store=object_store,
        volunteer_event_data=volunteer_event_data,
        active_connected_cadets=active_connected_cadets,
        missing_volunteers_if_true_otherwise_missing_cadets=False

    )


def warn_about_volunteer_availablity_at_event_with_connected_cadets(
    object_store: ObjectStore,
    event: Event,
    volunteer: Volunteer,
    volunteer_event_data: AllEventDataForVolunteer,
    active_connected_cadets: ListOfCadets,
        missing_volunteers_if_true_otherwise_missing_cadets: bool
) -> str:
    cadet_at_event_availability = get_availability_dict_for_active_cadets_at_event(
        object_store=object_store, event=event
    )
    volunteer_registration_data = volunteer_event_data.registration_data
    warnings = []
    for day in event.days_in_event():
        warnings = warning_about_volunteer_availability_on_specific_day(
            volunteer_registration_data=volunteer_registration_data,
            active_connected_cadets=active_connected_cadets,
            cadet_at_event_availability=cadet_at_event_availability,
            day=day,
            warnings=warnings,
            missing_volunteers_if_true_otherwise_missing_cadets=missing_volunteers_if_true_otherwise_missing_cadets
        )

    warnings = add_notes_to_warnings_on_availability(volunteer=volunteer, volunteer_registration_data=volunteer_registration_data, warnings=warnings)

    return warnings

def warning_about_volunteer_availability_on_specific_day(
                                                        volunteer_registration_data: RegistrationDataForVolunteerAtEvent,
                                                         active_connected_cadets: ListOfCadets,
                                                         cadet_at_event_availability: Dict[Cadet, DaySelector],
                                                         day: Day,
                                                         warnings: List[str],
                                                         missing_volunteers_if_true_otherwise_missing_cadets: bool):
    volunteer_available_on_day = (
        volunteer_registration_data.availablity.available_on_day(day)
    )
    list_of_cadets_available_on_day = get_list_of_cadets_available_on_day(
        cadet_at_event_availability=cadet_at_event_availability,
        active_connected_cadets=active_connected_cadets,
        day=day
    )
    any_cadet_available_on_day = len(list_of_cadets_available_on_day) > 0

    if missing_volunteers_if_true_otherwise_missing_cadets:
        if not volunteer_available_on_day and any_cadet_available_on_day:
            new_warning = warning_if_cadet_present_and_no_volunteers(list_of_cadets_available_on_day=list_of_cadets_available_on_day,
                                                                     day=day)
            warnings.append(new_warning)
    else:
        if volunteer_available_on_day and not any_cadet_available_on_day:
            new_warning = warning_if_volunteer_present_and_not_cadet(active_connected_cadets=active_connected_cadets,
                                                                     list_of_cadets_available_on_day=list_of_cadets_available_on_day,
                                                                     day=day)
            warnings.append(new_warning)


    return warnings

def get_list_of_cadets_available_on_day(cadet_at_event_availability: Dict[Cadet, DaySelector],
                                                active_connected_cadets: ListOfCadets,
                                                         day: Day,) -> ListOfCadets:
    list_of_cadets_available_on_day = [
        cadet
        for cadet in active_connected_cadets
        if is_cadet_available_on_day(cadet=cadet, cadet_at_event_availability=cadet_at_event_availability, day=day)
    ]

    return ListOfCadets(list_of_cadets_available_on_day)


def is_cadet_available_on_day(cadet_at_event_availability: Dict[Cadet, DaySelector],
                              cadet: Cadet,
                                                         day: Day,) -> bool:
    availability_for_cadet = cadet_at_event_availability.get(cadet, empty_day_selector)

    return availability_for_cadet.available_on_day(day)

def warning_if_volunteer_present_and_not_cadet(active_connected_cadets: ListOfCadets, list_of_cadets_available_on_day: ListOfCadets, day: Day)-> str:
    missing_cadet_names = ", ".join(
        get_cadet_names_who_are_connected_but_not_available_on_day(active_connected_cadets=active_connected_cadets,
                                                                   list_of_cadets_available_on_day=list_of_cadets_available_on_day)
    )
    return (
        "On %s volunteer attending; but associated sailors %s are not attending"
        % (day.name.upper(), missing_cadet_names)
    )

def get_cadet_names_who_are_connected_but_not_available_on_day(active_connected_cadets: ListOfCadets, list_of_cadets_available_on_day: ListOfCadets, ):
    missing_cadet_names = \
        [
            cadet.name
            for cadet in active_connected_cadets
            if cadet not in list_of_cadets_available_on_day
        ]

    return missing_cadet_names


def warning_if_cadet_present_and_no_volunteers(list_of_cadets_available_on_day: ListOfCadets, day: Day) -> str:
    names_of_attending_cadets = [cadet.name for cadet in list_of_cadets_available_on_day]
    joined_names = ", ".join(names_of_attending_cadets)

    return "On %s, sailors are attending but volunteer is not: %s" % (day.name.upper(), joined_names)


def add_notes_to_warnings_on_availability(volunteer: Volunteer, volunteer_registration_data: RegistrationDataForVolunteerAtEvent, warnings: List[str]) -> str:

    notes = copy(volunteer_registration_data.notes)
    if len(notes) > 0:
        notes = "(Notes: %s)" % notes

    if len(warnings) > 0:
        prefix = "%s:" % volunteer.name
        warnings_str = ", ".join(warnings)
        return "%s %s %s" % (prefix, warnings_str, notes)
    else:
        return ""

def warn_about_single_volunteer_with_no_cadet_at_event(
    volunteer: Volunteer,
    event: Event,
    volunteer_event_data: AllEventDataForVolunteer,
    object_store: ObjectStore,  ## not used
) -> str:
    active_connected_cadets = get_list_of_cadets_associated_with_volunteer_at_event(
        object_store=object_store, event=event, volunteer=volunteer
    )

    if len(active_connected_cadets) == 0:
        return (
            "%s is not connected to any active (not cancelled) cadets at this event"
            % volunteer.name
        )
    else:
        return ""


def warn_on_cadets_which_should_have_volunteers(
    object_store: ObjectStore, event: Event
) :
    ## NOT GENERIC!
    active_cadets = get_list_of_active_cadets_at_event(
        object_store=object_store, event=event
    )
    list_of_warnings = [
        warning_for_specific_cadet_at_event(
            object_store=object_store, event=event, cadet=cadet
        )
        for cadet in active_cadets
    ]

    list_of_warnings = remove_empty_values_in_warning_list(list_of_warnings)
    process_warnings_into_warning_list(object_store=object_store, event=event,
                                       list_of_warnings=list_of_warnings,
                                       priority=HIGH_PRIORITY, category=CADET_WITHOUT_ADULT)


def warning_for_specific_cadet_at_event(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> str:
    no_volunteer = cadet_has_no_active_volunteer(
        object_store=object_store, event=event, cadet=cadet
    )
    warning = ""
    if no_volunteer:
        first_event = is_first_event_for_cadet(
            object_store=object_store, event=event, cadet=cadet
        )
        too_young = cadet_is_too_young_to_be_without_parent(cadet)
        status_text = get_volunteer_status_and_possible_names(
            object_store=object_store, event=event, cadet=cadet
        )
        if first_event:
            warning += (
                "It's the first event for %s and must not be at the event by themselves but they have no connected volunteer %s"
                % (cadet.name, status_text)
            )

        if too_young:
            warning += (
                "%s is too young to be at the event by themselves but has no connected volunteer %s"
                % (cadet.name, status_text)
            )

    return warning


def cadet_has_no_active_volunteer(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> bool:
    volunteers = get_list_of_volunteers_associated_with_cadet_at_event(
        object_store=object_store, event=event, cadet=cadet
    )
    return len(volunteers) == 0


def is_first_event_for_cadet(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> bool:
    previous_allocation = copy(
        get_dict_of_all_event_allocations_for_single_cadet(
            object_store=object_store,
            cadet=cadet,
            excluding_event=event,
            only_events_before_excluded_event=True,
        )
    )

    return len(previous_allocation) == 0


def get_volunteer_status_and_possible_names(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> str:
    relevant_rows = get_all_rows_in_registration_data_which_have_been_identified_for_a_specific_cadet(
        object_store=object_store, event=event, cadet=cadet
    )

    relevant_rows = relevant_rows.active_registrations_only()

    status_in_rows = [get_volunteer_status_from_row(row) for row in relevant_rows]
    status_in_rows = [status for status in status_in_rows if len(status) > 0]

    if len(status_in_rows) == 0:
        return ""

    status_in_rows = list(set(status_in_rows))

    if len(status_in_rows) > 1:
        status_in_rows.append("[for different registered cadets]")

    return "(Declared volunteer status: %s)" % ", ".join(status_in_rows)

from app.backend.registration_data.identified_volunteers_at_event import get_list_of_identified_volunteers_at_event, \
    get_relevant_information_for_volunteer_in_event_at_row_and_index


def warn_on_volunteers_with_skipped_registration(object_store: ObjectStore, event: Event):
    identified_volunteers_at_event = get_list_of_identified_volunteers_at_event(object_store=object_store, event=event)
    list_of_temporary_row_ids_and_volunteer_index = identified_volunteers_at_event.list_of_row_and_index_temporary_skip()
    warnings = [warning_for_specific_temporary_skip_volunteer_id_at_event(
        object_store=object_store,
        event=event,
        row_id_and_index=row_id_and_index

    ) for row_id_and_index in list_of_temporary_row_ids_and_volunteer_index]

    process_warnings_into_warning_list(object_store=object_store, event=event,
                                       list_of_warnings=warnings, category=VOLUNTEER_IDENTITY,
                                       priority=MEDIUM_PRIORITY)

def warning_for_specific_temporary_skip_volunteer_id_at_event(object_store: ObjectStore, event: Event, row_id_and_index: RowIDAndIndex) -> str:
    relevant_information = (
        get_relevant_information_for_volunteer_in_event_at_row_and_index(
            object_store=object_store,
            row_id=row_id_and_index.row_id,
            volunteer_index=row_id_and_index.volunteer_index,
            event=event,
        )
    )
    volunteer = get_volunteer_from_relevant_information(relevant_information)
    warning = \
        "Temporarily skipping volunteer probably called %s in row %s id %d"    % (volunteer.name, str(row_id_and_index.row_id), row_id_and_index.volunteer_index)

    return warning


def remove_empty_values_in_warning_list(list_of_warnings: List[str]) -> List[str]:
    list_of_warnings = [warning for warning in list_of_warnings if len(warning) > 0]

    return list_of_warnings


def get_all_saved_warnings_for_volunteer_rota(object_store: ObjectStore, event: Event) -> ListOfEventWarnings:
    all_warnings = get_list_of_warnings_at_event_for_categories_sorted_by_category_and_priority(
        object_store=object_store,
        event=event,
        list_of_categories=[
            VOLUNTEER_IDENTITY,
    VOLUNTEER_QUALIFICATION,
    CADET_WITHOUT_ADULT,
    VOLUNTEER_AVAILABILITY,
    VOLUNTEER_GROUP,
    VOLUNTEER_UNCONNECTED,
        VOLUNTEER_PREFERENCE])

    return all_warnings

