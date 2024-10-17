from copy import copy
from typing import List, Callable, Dict

import app.objects.volunteer_roles_and_groups_with_id
from app.OLD_backend.wa_import.update_cadets_at_event import get_all_rows_in_mapped_event_for_cadet

from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache

from app.data_access.store.data_access import DataLayer

from app.OLD_backend.data.patrol_boats import PatrolBoatsData
from app.objects.patrol_boats import PatrolBoat

from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.OLD_backend.group_allocations.cadet_event_allocations import (
    get_list_of_active_cadets_at_event,
)
from app.backend.groups.cadets_with_groups_at_event import get_dict_of_all_event_allocations_for_single_cadet

from app.OLD_backend.rota.volunteer_rota import (
    list_of_cadet_groups_associated_with_volunteer,
    lake_in_list_of_groups,
    volunteer_is_on_lake,
    groups_for_volunteer_at_event, load_list_of_volunteers_at_event, get_list_of_volunteer_roles_for_event_across_days,
)
from app.OLD_backend.volunteers.volunteers import get_dict_of_existing_skills
from app.frontend.shared.events_state import get_event_from_state
from app.OLD_backend.volunteers.volunteer_allocation import \
    get_list_of_volunteer_names_associated_with_cadet_at_event, \
    get_list_of_active_connected_cadets_at_event_for_volunteer

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import ListOfCadets, Cadet, cadet_is_too_young_to_be_without_parent
from app.objects.day_selectors import EMPTY_DAY_SELECTOR, Day, DaySelector
from app.objects.events import Event
from app.objects.registration_data import get_status_from_row
from app.objects_OLD.volunteers_at_event import DEPRECATE_VolunteerAtEvent


def warn_on_all_volunteers_availability(cache: AdHocCache, event: Event) -> List[str]:
    return warn_on_all_volunteers_generic(
        cache=cache,
        event=event,
        warning_function=warn_about_single_volunteer_availablity_at_event,
    )


def warn_on_all_volunteers_group(cache: AdHocCache, event: Event) -> List[str]:
    return warn_on_all_volunteers_generic(
        cache=cache,
        event=event,
        warning_function=warn_about_single_volunteer_groups_at_event,
    )


def warn_on_all_volunteers_unconnected(cache: AdHocCache, event: Event) -> List[str]:
    return warn_on_all_volunteers_generic(
        cache=cache,
        event=event,
        warning_function=warn_about_single_volunteer_with_no_cadet_at_event,
    )

def warn_on_volunteer_qualifications(cache: AdHocCache, event: Event) -> List[str]:
    return warn_on_all_volunteers_generic(
        cache=cache,
        event=event,
        warning_function=warn_about_single_volunteer_with_qualifications,
    )


def warn_on_all_volunteers_generic(
    cache: AdHocCache, event: Event, warning_function: Callable
) -> List[str]:

    list_of_volunteers_at_event = cache.get_from_cache(load_list_of_volunteers_at_event,
        event=event
    )

    list_of_warnings = []
    for volunteer_at_event in list_of_volunteers_at_event:
        warnings_for_volunteer = warning_function(
            cache=cache, volunteer_at_event=volunteer_at_event, event=event
        )
        list_of_warnings.append(warnings_for_volunteer)

    list_of_warnings = process_warning_list(list_of_warnings)

    return list_of_warnings


def process_warning_list(list_of_warnings: List[str]) -> List[str]:
    list_of_warnings = [warning for warning in list_of_warnings if len(warning) > 0]

    if len(list_of_warnings) > 0:
        list_of_warnings = [" "] + list_of_warnings

    return list_of_warnings


def warn_about_single_volunteer_with_qualifications(
    cache: AdHocCache,
    event: Event,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
) -> str:
    volunteer = volunteer_at_event.volunteer

    dict_of_skills = cache.get_from_cache(get_dict_of_existing_skills, volunteer=volunteer)
    list_of_volunteer_roles = cache.get_from_cache(get_list_of_volunteer_roles_for_event_across_days,
                                                   event=event,
                                                   volunteer_at_event=volunteer_at_event)

    roles_with_warning = []
    for volunteer_role in list_of_volunteer_roles:
        if not app.objects.primtive_with_id.volunteer_roles_and_groups.is_qualified_for_role(dict_of_skills):
            roles_with_warning.append(volunteer_role.role)

    if len(roles_with_warning) == 0:
        return ""

    roles_with_warning = list(set(roles_with_warning))
    warnings_as_str = ", ".join(roles_with_warning)

    return "%s is not qualified for role(s): %s" % (volunteer.name, warnings_as_str)



def warn_about_single_volunteer_groups_at_event(
        cache: AdHocCache,    event: Event,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
) -> str:
    group_warnings_for_volunteer = []

    list_of_cadet_groups = cache.get_from_cache(list_of_cadet_groups_associated_with_volunteer, event=event, volunteer_at_event=volunteer_at_event)
    has_lake_cadet = lake_in_list_of_groups(list_of_cadet_groups)
    is_lake_volunteer = cache.get_from_cache(volunteer_is_on_lake,
         volunteer_id=volunteer_at_event.volunteer_id, event=event
    )
    volunteer = volunteer_at_event.volunteer
    notes = copy(volunteer_at_event.notes)
    if len(notes) > 0:
        notes = "(%s)" % notes

    if has_lake_cadet and is_lake_volunteer:
        group_warnings_for_volunteer.append(
            "Volunteer %s is in lake role, but has cadet at lake %s"
            % (volunteer.name, notes)
        )

    list_of_groups_for_volunteer = cache.get_from_cache(groups_for_volunteer_at_event,
         event=event, volunteer=volunteer
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


def warn_about_single_volunteer_availablity_at_event(
        cache: AdHocCache,    event: Event,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
) -> str:
    active_connected_cadets = cache.get_from_cache(get_list_of_active_connected_cadets_at_event_for_volunteer,
        event=event,
        volunteer_at_event=volunteer_at_event
    )

    if len(active_connected_cadets) == 0:
        return ""

    return warn_about_volunteer_availablity_at_event_with_connected_cadets(
        cache=cache,
        event=event,
        volunteer_at_event=volunteer_at_event,
        active_connected_cadets=active_connected_cadets,
    )


def get_availability_dict_for_active_cadet_ids_at_event(data_layer: DataLayer, event: Event)-> Dict[str, DaySelector]:
    cadets_at_event_data = CadetsAtEventIdLevelData(data_layer)
    cadet_at_event_availability = (
        cadets_at_event_data.get_availability_dict_for_active_cadet_ids_at_event(event)
    )

    return cadet_at_event_availability

def warn_about_volunteer_availablity_at_event_with_connected_cadets(
        cache: AdHocCache,    event: Event,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
    active_connected_cadets: ListOfCadets,
) -> str:
    cadet_at_event_availability = cache.get_from_cache(
        get_availability_dict_for_active_cadet_ids_at_event,
        event=event
    )

    warnings = []
    for day in event.weekdays_in_event():
        volunteer_available_on_day = volunteer_at_event.availablity.available_on_day(
            day
        )
        list_of_cadets_available_on_day = [
            cadet
            for cadet in active_connected_cadets
            if cadet_at_event_availability.get(
                cadet.id, EMPTY_DAY_SELECTOR
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

    notes = copy(volunteer_at_event.notes)
    if len(notes) > 0:
        notes = "(%s)" % notes

    if len(warnings) > 0:
        prefix = "%s:" % volunteer_at_event.name
        warnings_str = ", ".join(warnings)
        return "%s %s %s" % (prefix, warnings_str, notes)
    else:
        return ""


def warn_about_single_volunteer_with_no_cadet_at_event(
        cache: AdHocCache,    event: Event,
    volunteer_at_event: DEPRECATE_VolunteerAtEvent,
) -> str:
    volunteer = volunteer_at_event.volunteer
    active_connected_cadets = cache.get_from_cache(
        get_list_of_active_connected_cadets_at_event_for_volunteer,
        event=event,
        volunteer_at_event=volunteer_at_event
    )

    if len(active_connected_cadets) == 0:
        return (
            "%s is not connected to any active (not cancelled) cadets at this event"
            % volunteer.name
        )
    else:
        return ""


def warn_on_cadets_which_should_have_volunteers(
    cache: AdHocCache,
        event: Event
) -> List[str]:
    active_cadets = cache.get_from_cache(get_list_of_active_cadets_at_event, event=event)
    list_of_warnings = [
        warning_for_specific_cadet_at_event(
           cache=cache, event=event, cadet=cadet
        )
        for cadet in active_cadets
    ]

    return process_warning_list(list_of_warnings)


def warning_for_specific_cadet_at_event(
    cache: AdHocCache, event: Event, cadet: Cadet
) -> str:
    no_volunteer = cadet_has_no_active_volunteer(cache=cache,
         event=event, cadet=cadet
    )
    warning = ""
    if no_volunteer:
        first_event = is_first_event_for_cadet(cache=cache, event=event, cadet=cadet)
        too_young = cadet_is_too_young_to_be_without_parent(cadet)
        status_text = get_volunteer_status_and_possible_names(
            cache=cache, event=event, cadet=cadet
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
    cache: AdHocCache, event: Event, cadet: Cadet
) -> bool:
    volunteer_names = cache.get_from_cache(get_list_of_volunteer_names_associated_with_cadet_at_event,
         cadet_id=cadet.id, event=event
    )
    return len(volunteer_names) == 0


def is_first_event_for_cadet(cache: AdHocCache, event: Event, cadet: Cadet) -> bool:
    previous_allocation = copy(cache.get_from_cache(get_dict_of_all_event_allocations_for_single_cadet,
         cadet=cadet
    ))
    previous_allocation.pop(event)

    return len(previous_allocation) == 0


def get_volunteer_status_and_possible_names(
    cache: AdHocCache, event: Event, cadet: Cadet
) -> str:

    relevant_rows = cache.get_from_cache(get_all_rows_in_mapped_event_for_cadet, event=event, cadet=cadet)
    relevant_rows = relevant_rows.active_registrations_only()

    status_in_rows = [get_status_from_row(row) for row in relevant_rows]
    status_in_rows = [status for status in status_in_rows if len(status) > 0]

    if len(status_in_rows) == 0:
        return ""

    return "(Declared volunteer status: %s)" % ", ".join(status_in_rows)



def warn_on_pb2_drivers(interface: abstractInterface) -> List[str]:
    event = get_event_from_state(interface)
    patrol_boats = PatrolBoatsData(interface.data)
    boats_at_event = patrol_boats.list_of_unique_boats_at_event_including_unallocated(
        event
    )
    list_of_warnings = []
    for patrol_boat in boats_at_event:
        list_of_warnings += warn_on_pb2_drivers_for_boat(
            interface=interface, event=event, patrol_boat=patrol_boat
        )

    list_of_warnings = process_warning_list(list_of_warnings)

    return list_of_warnings


def warn_on_pb2_drivers_for_boat(
    interface: abstractInterface, event: Event, patrol_boat: PatrolBoat
) -> List[str]:
    list_of_warnings = [
        warn_on_pb2_drivers_for_boat_on_day(
            interface=interface, event=event, patrol_boat=patrol_boat, day=day
        )
        for day in event.weekdays_in_event()
    ]

    return list_of_warnings


def warn_on_pb2_drivers_for_boat_on_day(
    interface: abstractInterface, event: Event, patrol_boat: PatrolBoat, day: Day
) -> str:
    patrol_boat_data = PatrolBoatsData(interface.data)
    at_least_one_volunteer_on_boat_on_day_has_boat_skill = (
        patrol_boat_data.at_least_one_volunteer_on_boat_on_day_has_boat_skill(
            event=event, patrol_boat=patrol_boat, day=day
        )
    )
    if not at_least_one_volunteer_on_boat_on_day_has_boat_skill:
        return "%s on %s has no PB2 qualified person on board" % (
            patrol_boat.name,
            day.name,
        )
    else:
        return ""
