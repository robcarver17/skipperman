from copy import copy
from typing import List, Callable

from app.objects.constants import missing_data

from app.backend.data.volunteers import VolunteerData

from app.backend.data.volunteer_rota import VolunteerRotaData

from app.backend.data.patrol_boats import PatrolBoatsData
from app.objects.patrol_boats import PatrolBoat

from app.backend.cadets import cadet_from_id
from app.backend.data.cadets_at_event import CadetsAtEventData
from app.backend.group_allocations.cadet_event_allocations import get_list_of_active_cadets_at_event
from app.backend.group_allocations.previous_allocations import get_dict_of_all_event_allocations_for_single_cadet

from app.backend.volunteers.volunteer_rota import load_list_of_volunteers_at_event, \
    list_of_cadet_groups_associated_with_volunteer, lake_in_list_of_groups, volunteer_is_on_lake, groups_for_volunteer
from app.backend.volunteers.volunteers import get_volunteer_from_id
from app.data_access.configuration.field_list import VOLUNTEER_STATUS
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.registration_details.parse_registration_details_form import \
    list_of_volunteer_names_associated_with_cadet_at_event

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.day_selectors import EMPTY_DAY_SELECTOR, Day
from app.objects.events import Event
from app.objects.mapped_wa_event import RowInMappedWAEvent
from app.objects.volunteers_at_event import VolunteerAtEvent


def warn_on_all_volunteers_availability(interface: abstractInterface) -> List[str]:
    return warn_on_all_volunteers_generic(interface=interface,
                                          warning_function=warn_about_single_volunteer_availablity_at_event)


def warn_on_all_volunteers_group(interface: abstractInterface) -> List[str]:

    return warn_on_all_volunteers_generic(interface=interface,
                                          warning_function=warn_about_single_volunteer_groups_at_event)


def warn_on_all_volunteers_unconnected(interface: abstractInterface) -> List[str]:
    return warn_on_all_volunteers_generic(interface=interface,
                                          warning_function=warn_about_single_volunteer_with_no_cadet_at_event)


def warn_on_all_volunteers_generic(interface: abstractInterface, warning_function: Callable) -> List[str]:
    event = get_event_from_state(interface)
    list_of_volunteers_at_event = load_list_of_volunteers_at_event(event=event, interface=interface)

    list_of_warnings = []
    for volunteer_at_event in list_of_volunteers_at_event:
        warnings_for_volunteer = warning_function(interface=interface, volunteer_at_event=volunteer_at_event, event=event)
        list_of_warnings.append(warnings_for_volunteer)

    list_of_warnings = process_warning_list(list_of_warnings)

    return list_of_warnings


def process_warning_list(list_of_warnings: List[str]) -> List[str]:
    list_of_warnings = [warning for warning in list_of_warnings if len(warning)>0]

    if len(list_of_warnings)>0:
        list_of_warnings = [" "]+list_of_warnings

    return list_of_warnings


def warn_about_single_volunteer_groups_at_event(interface: abstractInterface,
                                                event: Event,
                                                volunteer_at_event: VolunteerAtEvent) -> str:

    group_warnings_for_volunteer = []

    list_of_cadet_groups = list_of_cadet_groups_associated_with_volunteer(interface=interface,event=event, volunteer_at_event=volunteer_at_event)
    has_lake_cadet = lake_in_list_of_groups(list_of_cadet_groups)
    is_lake_volunteer = volunteer_is_on_lake(interface=interface, volunteer_id = volunteer_at_event.volunteer_id, event=event)
    volunteer = get_volunteer_from_id(interface, volunteer_at_event.volunteer_id)
    notes = copy(volunteer_at_event.notes)
    if len(notes)>0:
        notes = "(%s)" % notes

    if has_lake_cadet and is_lake_volunteer:
        group_warnings_for_volunteer.append("Volunteer %s is in lake role, but has cadet at lake %s" % (volunteer.name, notes))

    list_of_groups_for_volunteer = groups_for_volunteer(interface=interface, event=event, volunteer_id=volunteer_at_event.volunteer_id)
    for group in list_of_groups_for_volunteer:
        if group in list_of_cadet_groups:
            if group.is_unallocated:
                continue
            group_warnings_for_volunteer.append("Volunteer %s and cadet are both in group %s %s" % (volunteer.name, group.group_name, notes))

    return ", ".join(group_warnings_for_volunteer)


def warn_about_single_volunteer_availablity_at_event(interface: abstractInterface,
                                                     event: Event,
                                                     volunteer_at_event: VolunteerAtEvent) -> str:

    cadet_ids = volunteer_at_event.list_of_associated_cadet_id
    connected_cadets = ListOfCadets([cadet_from_id(interface=interface, cadet_id=cadet_id) for cadet_id in cadet_ids])
    cadets_at_event_data = CadetsAtEventData(interface.data)
    active_connected_cadets = ListOfCadets([cadet for cadet in connected_cadets if cadet.id in cadets_at_event_data.list_of_active_cadet_ids_at_event(event)])

    if len(active_connected_cadets)==0:
        return ''

    return warn_about_volunteer_availablity_at_event_with_connected_cadets(
        interface=interface,
        event=event,
        volunteer_at_event=volunteer_at_event,
        active_connected_cadets=active_connected_cadets
    )


def warn_about_volunteer_availablity_at_event_with_connected_cadets(interface: abstractInterface,
                                         event: Event,
                                  volunteer_at_event: VolunteerAtEvent,
                                                                    active_connected_cadets: ListOfCadets) -> str:
    warnings = []
    cadets_at_event_data = CadetsAtEventData(interface.data)
    volunteer = get_volunteer_from_id(interface, volunteer_at_event.volunteer_id)
    cadet_at_event_availability = cadets_at_event_data.get_availability_dict_for_active_cadet_ids_at_event(event)
    for day in event.weekdays_in_event():
        volunteer_available_on_day = volunteer_at_event.availablity.available_on_day(day)
        list_of_cadets_available_on_day = [cadet for cadet in active_connected_cadets
                                           if cadet_at_event_availability.get(cadet.id, EMPTY_DAY_SELECTOR).available_on_day(day)]

        any_cadet_available_on_day = len(list_of_cadets_available_on_day)>0

        if volunteer_available_on_day==any_cadet_available_on_day:
            continue

        if not any_cadet_available_on_day:
            missing_cadet_names = ", ".join([cadet.name for cadet in active_connected_cadets if cadet not in list_of_cadets_available_on_day])
            warnings.append('On %s volunteer attending but associated cadets %s are not attending' % (day.name.lower(),
                                                                                                                 missing_cadet_names))

    notes = copy(volunteer_at_event.notes)
    if len(notes) > 0:
        notes = "(%s)" % notes

    if len(warnings)>0:
        prefix = "%s:" % volunteer.name
        warnings_str = ", ".join(warnings)
        return "%s %s %s" % (prefix, warnings_str, notes)
    else:
        return ''


def warn_about_single_volunteer_with_no_cadet_at_event(interface: abstractInterface,
                                         event: Event,
                                  volunteer_at_event: VolunteerAtEvent) -> str:

    cadet_ids = volunteer_at_event.list_of_associated_cadet_id
    connected_cadets = ListOfCadets([cadet_from_id(interface=interface, cadet_id=cadet_id) for cadet_id in cadet_ids])
    volunteer = get_volunteer_from_id(interface, volunteer_at_event.volunteer_id)
    cadets_at_event_data = CadetsAtEventData(interface.data)
    active_connected_cadets = ListOfCadets([cadet for cadet in connected_cadets if cadet.id in cadets_at_event_data.list_of_active_cadet_ids_at_event(event)])

    if len(active_connected_cadets)==0:
        return '%s is not connected to any active (not cancelled) cadets at this event' % volunteer.name
    else:
        return ''


def warn_on_cadets_which_should_have_volunteers(interface: abstractInterface) -> List[str]:
    event = get_event_from_state(interface)
    active_cadets = get_list_of_active_cadets_at_event(interface=interface, event=event)
    list_of_warnings = [warning_for_specific_cadet_at_event(interface=interface,
                                                        event=event,
                                                        cadet=cadet)
                    for cadet in active_cadets]


    return process_warning_list(list_of_warnings)


def warning_for_specific_cadet_at_event(interface: abstractInterface, event: Event, cadet: Cadet) -> str:
    no_volunteer =  has_no_active_volunteer(interface=interface, event=event, cadet=cadet)
    warning = ''
    if no_volunteer:
        first_event = is_first_event(interface=interface, event=event, cadet=cadet)
        too_young = is_too_young(cadet)
        status_text = get_volunteer_status_and_possible_names(interface=interface, event=event, cadet=cadet)
        if first_event:
            warning+="It's the first event for %s and must not be at the event by themselves but they have no connected volunteer %s" % (cadet.name, status_text)

        if too_young:
            warning+="%s is too young to be at the event by themselves but has no connected volunteer %s" % (cadet.name, status_text)

    return warning


def has_no_active_volunteer(interface: abstractInterface, event: Event, cadet: Cadet) -> bool:
    volunteer_names = list_of_volunteer_names_associated_with_cadet_at_event(
        interface=interface,
        cadet_id=cadet.id,
        event=event
    )
    return len(volunteer_names)==0


def is_first_event(interface: abstractInterface, event: Event, cadet: Cadet) -> bool:
    previous_allocation = get_dict_of_all_event_allocations_for_single_cadet(interface=interface,
                                                                             cadet=cadet)
    previous_allocation.pop(event)

    return len(previous_allocation)==0


def is_too_young(cadet: Cadet) -> bool:
    return cadet.approx_age_years()<11


def get_volunteer_status_and_possible_names(interface: abstractInterface, event: Event, cadet: Cadet) -> str:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    relevant_rows = cadets_at_event_data.get_all_rows_in_mapped_event_for_cadet_id(event=event, cadet_id=cadet.id)
    relevant_rows = relevant_rows.active_registrations_only()

    status_in_rows = [get_status_from_row(row) for row in relevant_rows]
    status_in_rows = [status for status in status_in_rows if len(status)>0]

    if len(status_in_rows)==0:
        return ""

    return "(Declared volunteer status: %s)" % ", ".join(status_in_rows)


def get_status_from_row(row: RowInMappedWAEvent):
    return row.get_item(VOLUNTEER_STATUS, '')


def warn_on_volunteer_qualifications(interface: abstractInterface) -> List[str]:
    return warn_on_all_volunteers_generic(interface=interface,
                                          warning_function=warn_about_single_volunteer_with_qualifications)


def warn_about_single_volunteer_with_qualifications(interface: abstractInterface,
                                         event: Event,
                                  volunteer_at_event: VolunteerAtEvent) -> str:

    volunteer_rota_data = VolunteerRotaData(interface.data)
    volunteer_data = VolunteerData(interface.data)
    volunteer = volunteer_data.volunteer_with_id(volunteer_at_event.volunteer_id) ## FIXME SHOULD BE ABLE TO GET THIS FROM VolunteerAtEvent

    dict_of_skills = volunteer_data.get_dict_of_existing_skills_for_volunteer(volunteer)

    list_of_volunteer_roles = [volunteer_rota_data.get_volunteer_with_role_at_event_on_day_for_volunteer_at_event(event=event,
                                                                                                        volunteer_at_event=volunteer_at_event,
                                                                                                        day=day) for day in event.weekdays_in_event()]

    roles_with_warning =[]
    for volunteer_role in list_of_volunteer_roles:
        if not volunteer_role.is_qualified_for_role(dict_of_skills):
            roles_with_warning.append(volunteer_role.role)

    if len(roles_with_warning)==0:
        return ''

    roles_with_warning = list(set(roles_with_warning))
    warnings_as_str = ", ".join(roles_with_warning)

    return "%s is not qualified for role(s): %s" % (volunteer.name, warnings_as_str)

def warn_on_pb2_drivers(interface: abstractInterface) -> List[str]:
    event = get_event_from_state(interface)
    patrol_boats = PatrolBoatsData(interface.data)
    boats_at_event = patrol_boats.list_of_unique_boats_at_event_including_unallocated(event)
    list_of_warnings = []
    for patrol_boat in boats_at_event:
        list_of_warnings+=warn_on_pb2_drivers_for_boat(interface=interface, event=event, patrol_boat=patrol_boat)

    list_of_warnings = process_warning_list(list_of_warnings)

    return list_of_warnings

def warn_on_pb2_drivers_for_boat(interface: abstractInterface, event: Event, patrol_boat: PatrolBoat) -> List[str]:
    list_of_warnings = [warn_on_pb2_drivers_for_boat_on_day(interface=interface, event=event, patrol_boat=patrol_boat, day=day)
    for day in event.weekdays_in_event()]

    return list_of_warnings

def warn_on_pb2_drivers_for_boat_on_day(interface: abstractInterface, event: Event, patrol_boat: PatrolBoat, day: Day) -> str:
    patrol_boat_data = PatrolBoatsData(interface.data)
    at_least_one_volunteer_on_boat_on_day_has_boat_skill = patrol_boat_data.at_least_one_volunteer_on_boat_on_day_has_boat_skill(
        event=event,
        patrol_boat=patrol_boat,
        day=day
    )
    if not at_least_one_volunteer_on_boat_on_day_has_boat_skill:
        return '%s on %s has no PB2 qualified person on board' % (patrol_boat.name, day.name)
    else:
        return ''