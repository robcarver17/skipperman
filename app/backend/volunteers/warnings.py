from copy import copy
from typing import List, Callable

from app.objects.volunteer_roles_and_groups_with_id import is_qualified_for_role

from app.objects.composed.volunteers_with_all_event_data import AllEventDataForVolunteer
from app.objects.volunteers import Volunteer

from app.data_access.store.object_store import ObjectStore

from app.backend.registration_data.identified_cadets_at_event import \
    get_all_rows_in_registration_data_which_have_been_identified_for_a_specific_cadet

from app.backend.groups.previous_groups import get_dict_of_all_event_allocations_for_single_cadet
from app.backend.volunteers.volunteers_at_event import get_dict_of_all_event_data_for_volunteers
from app.backend.rota.volunteers_and_cadets import list_of_cadet_groups_associated_with_volunteer
from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import get_availability_dict_for_active_cadets_at_event, get_list_of_active_cadets_at_event
from app.backend.registration_data.cadet_and_volunteer_connections_at_event import \
    get_list_of_volunteers_associated_with_cadet_at_event, get_list_of_cadets_associated_with_volunteer_at_event

from app.objects.cadets import (
    ListOfCadets,
    Cadet,
    cadet_is_too_young_to_be_without_parent,
)
from app.objects.day_selectors import EMPTY_DAY_SELECTOR
from app.objects.events import Event
from app.objects.registration_data import get_status_from_row


def warn_on_all_volunteers_availability(object_store: ObjectStore, event: Event) -> List[str]:
    return warn_on_all_volunteers_generic(
        object_store=object_store,
        event=event,
        warning_function=warn_about_single_volunteer_availablity_at_event,
    )


def warn_on_all_volunteers_group(object_store: ObjectStore, event: Event) -> List[str]:
    return warn_on_all_volunteers_generic(
        object_store=object_store,
        event=event,
        warning_function=warn_about_single_volunteer_groups_at_event,
    )


def warn_on_all_volunteers_unconnected(object_store: ObjectStore, event: Event) -> List[str]:
    return warn_on_all_volunteers_generic(
        object_store=object_store,
        event=event,
        warning_function=warn_about_single_volunteer_with_no_cadet_at_event,
    )


def warn_on_volunteer_qualifications(object_store: ObjectStore, event: Event) -> List[str]:
    return warn_on_all_volunteers_generic(
        object_store=object_store,
        event=event,
        warning_function=warn_about_single_volunteer_with_qualifications,
    )


def warn_on_all_volunteers_generic(
    object_store: ObjectStore, event: Event, warning_function: Callable
) -> List[str]:
    list_of_volunteers_at_event = get_dict_of_all_event_data_for_volunteers(object_store=object_store, event=event)

    list_of_warnings = []
    for volunteer, volunteer_event_data in list_of_volunteers_at_event.items():
        warnings_for_volunteer = warning_function(
            volunteer=volunteer, volunteer_event_data=volunteer_event_data,
            object_store=object_store, event=event
        )
        list_of_warnings.append(warnings_for_volunteer)

    list_of_warnings = process_warning_list(list_of_warnings)

    return list_of_warnings




def warn_about_single_volunteer_with_qualifications(
        volunteer: Volunteer,
        event: Event,
        volunteer_event_data: AllEventDataForVolunteer,
        object_store: ObjectStore ## not used
) -> str:


    dict_of_skills = volunteer_event_data.volunteer_skills
    list_of_volunteer_roles = volunteer_event_data.roles_and_groups.list_of_roles()

    roles_with_warning = []
    for volunteer_role in list_of_volunteer_roles:
        if not is_qualified_for_role(
            role=volunteer_role, dict_of_skills=dict_of_skills
        ):
            roles_with_warning.append(volunteer_role.name)

    if len(roles_with_warning) == 0:
        return ""

    roles_with_warning = list(set(roles_with_warning))
    warnings_as_str = ", ".join(roles_with_warning)

    return "%s is not qualified for role(s): %s" % (volunteer.name, warnings_as_str)


def warn_about_single_volunteer_groups_at_event(
        volunteer: Volunteer,
        event: Event,
        volunteer_event_data: AllEventDataForVolunteer,
        object_store: ObjectStore
) -> str:
    group_warnings_for_volunteer = []

    list_of_cadet_groups =         list_of_cadet_groups_associated_with_volunteer(
        event=event,
        volunteer=volunteer,
    object_store=object_store)

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

    list_of_groups_for_volunteer = volunteer_event_data.roles_and_groups.list_of_groups()

    for group in list_of_groups_for_volunteer:
        if group in list_of_cadet_groups:
            if group.is_unallocated:
                continue
            group_warnings_for_volunteer.append(
                "Volunteer %s and cadet are both in group %s %s"
                % (volunteer.name, group.name, notes)
            )

    return ", ".join(group_warnings_for_volunteer)


def warn_about_single_volunteer_availablity_at_event(
        volunteer: Volunteer,
        event: Event,
        volunteer_event_data: AllEventDataForVolunteer,
        object_store: ObjectStore
) -> str:

    active_connected_cadets =\
        get_list_of_cadets_associated_with_volunteer_at_event(
        object_store=object_store,
        event=event,
        volunteer=volunteer)

    if len(active_connected_cadets) == 0:
        return ""

    return warn_about_volunteer_availablity_at_event_with_connected_cadets(
        event=event,
        volunteer=volunteer,
        object_store=object_store,
        volunteer_event_data=volunteer_event_data,
        active_connected_cadets=active_connected_cadets,
    )




def warn_about_volunteer_availablity_at_event_with_connected_cadets(
    object_store: ObjectStore,
    event: Event,
        volunteer: Volunteer,
        volunteer_event_data: AllEventDataForVolunteer,
        active_connected_cadets: ListOfCadets,
) -> str:
    cadet_at_event_availability = \
        get_availability_dict_for_active_cadets_at_event(object_store=object_store, event=event
                                                         )
    volunteer_registration_data = volunteer_event_data.registration_data
    warnings = []
    for day in event.weekdays_in_event():
        volunteer_available_on_day = volunteer_registration_data.availablity.available_on_day(
            day
        )
        list_of_cadets_available_on_day = [
            cadet
            for cadet in active_connected_cadets
            if cadet_at_event_availability.get(
                cadet, EMPTY_DAY_SELECTOR
            ).available_on_day(day)
        ]

        any_cadet_available_on_day = len(list_of_cadets_available_on_day) > 0

        if volunteer_available_on_day == any_cadet_available_on_day:
            continue

        if not any_cadet_available_on_day:
            missing_cadet_names = ", ".join(
                [
                    cadet.name
                    for cadet in active_connected_cadets
                    if cadet not in list_of_cadets_available_on_day
                ]
            )
            warnings.append(
                "On %s volunteer attending but associated cadets %s are not attending"
                % (day.name.lower(), missing_cadet_names)
            )

    notes = copy(volunteer_registration_data.notes)
    if len(notes) > 0:
        notes = "(%s)" % notes

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
        object_store: ObjectStore ## not used
) -> str:
    active_connected_cadets =\
        get_list_of_cadets_associated_with_volunteer_at_event(
        object_store=object_store,
        event=event,
        volunteer=volunteer)

    if len(active_connected_cadets) == 0:
        return (
            "%s is not connected to any active (not cancelled) cadets at this event"
            % volunteer.name
        )
    else:
        return ""


def warn_on_cadets_which_should_have_volunteers(
    object_store: ObjectStore, event: Event
) -> List[str]:
    active_cadets = \
        get_list_of_active_cadets_at_event(object_store=object_store, event=event
    )
    list_of_warnings = [
        warning_for_specific_cadet_at_event(object_store=object_store, event=event, cadet=cadet)
        for cadet in active_cadets
    ]

    return process_warning_list(list_of_warnings)


def warning_for_specific_cadet_at_event(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> str:
    no_volunteer = cadet_has_no_active_volunteer(object_store=object_store, event=event, cadet=cadet)
    warning = ""
    if no_volunteer:
        first_event = is_first_event_for_cadet(object_store=object_store, event=event, cadet=cadet)
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
    volunteers = \
        get_list_of_volunteers_associated_with_cadet_at_event(
        object_store=object_store,
        event=event,
        cadet=cadet
    )
    return len(volunteers) == 0


def is_first_event_for_cadet(object_store: ObjectStore, event: Event, cadet: Cadet) -> bool:
    previous_allocation = copy(

            get_dict_of_all_event_allocations_for_single_cadet(object_store=object_store, cadet=cadet)
    )
    previous_allocation.pop(event)

    return len(previous_allocation) == 0


def get_volunteer_status_and_possible_names(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> str:
    relevant_rows =\
        get_all_rows_in_registration_data_which_have_been_identified_for_a_specific_cadet(object_store=object_store, event=event, cadet=cadet)

    relevant_rows = relevant_rows.active_registrations_only()

    status_in_rows = [get_status_from_row(row) for row in relevant_rows]
    status_in_rows = [status for status in status_in_rows if len(status) > 0]

    if len(status_in_rows) == 0:
        return ""

    status_in_rows = list(set(status_in_rows))

    if len(status_in_rows)>1:
        status_in_rows.append(("[for different registered cadets]"))

    return "(Declared volunteer status: %s)" % ", ".join(status_in_rows)


def process_warning_list(list_of_warnings: List[str]) -> List[str]:
    list_of_warnings = [warning for warning in list_of_warnings if len(warning) > 0]

    if len(list_of_warnings) > 0:
        list_of_warnings = [" "] + list_of_warnings

    return list_of_warnings
