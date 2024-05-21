from typing import Union

from app.objects.day_selectors import NO_DAYS_SELECTED, EMPTY_DAY_SELECTOR

from app.backend.cadets import cadet_from_id
from app.backend.data.cadets_at_event import CadetsAtEventData

from app.objects.cadets import ListOfCadets

from app.objects.abstract_objects.abstract_lines import ListOfLines, DetailListOfLines

from app.objects.events import Event

from app.backend.volunteers.volunteer_rota import list_of_cadet_groups_associated_with_volunteer, \
    lake_in_list_of_groups, volunteer_is_on_lake, groups_for_volunteer
from app.backend.volunteers.volunteers import get_volunteer_from_id
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_rota.parse_volunteer_table import get_filtered_list_of_volunteers_at_event
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.volunteers_at_event import VolunteerAtEvent


def warn_on_all_volunteers(interface: abstractInterface) -> Union[DetailListOfLines, str]:
    list_of_volunteers_at_event = get_filtered_list_of_volunteers_at_event(interface)

    list_of_warnings = []
    for volunteer_at_event in list_of_volunteers_at_event:
        warnings_for_volunteer = warn_about_volunteer_at_event(interface=interface, volunteer_at_event=volunteer_at_event)

        list_of_warnings+=warnings_for_volunteer

    if len(list_of_warnings)==0:
        return ''

    return DetailListOfLines(ListOfLines(list_of_warnings).add_Lines(), name="Warnings")

def warn_about_volunteer_at_event(interface: abstractInterface,
                                  volunteer_at_event: VolunteerAtEvent) -> list:
    event = get_event_from_state(interface)
    warnings_for_volunteer = []
    group_warning = warn_about_volunteer_groups_at_event(interface=interface, event=event, volunteer_at_event=volunteer_at_event)
    if len(group_warning)>0:
        warnings_for_volunteer.append(group_warning)
    availability_warning = warn_about_volunteer_availablity_at_event(interface=interface, event=event, volunteer_at_event=volunteer_at_event)
    if len(availability_warning)>0:
        warnings_for_volunteer.append(availability_warning)

    return warnings_for_volunteer

def warn_about_volunteer_groups_at_event(interface: abstractInterface,
                                         event: Event,
                                  volunteer_at_event: VolunteerAtEvent) -> str:

    group_warnings_for_volunteer = []

    list_of_cadet_groups = list_of_cadet_groups_associated_with_volunteer(interface=interface,event=event, volunteer_at_event=volunteer_at_event)
    has_lake_cadet = lake_in_list_of_groups(list_of_cadet_groups)
    is_lake_volunteer = volunteer_is_on_lake(interface=interface, volunteer_id = volunteer_at_event.volunteer_id, event=event)
    volunteer = get_volunteer_from_id(interface, volunteer_at_event.volunteer_id)

    if has_lake_cadet and is_lake_volunteer:
        group_warnings_for_volunteer.append("Volunteer %s is in lake role, but has cadet at lake" % volunteer.name)

    list_of_groups_for_volunteer = groups_for_volunteer(interface=interface, event=event, volunteer_id=volunteer_at_event.volunteer_id)
    for group in list_of_groups_for_volunteer:
        if group in list_of_cadet_groups:
            if group.is_unallocated:
                continue
            group_warnings_for_volunteer.append("Volunteer %s and cadet are both in group %s" % (volunteer.name, group.group_name))

    return ", ".join(group_warnings_for_volunteer)

def warn_about_volunteer_availablity_at_event(interface: abstractInterface,
                                         event: Event,
                                  volunteer_at_event: VolunteerAtEvent) -> str:

    cadet_ids = volunteer_at_event.list_of_associated_cadet_id
    connected_cadets = ListOfCadets([cadet_from_id(interface=interface, cadet_id=cadet_id) for cadet_id in cadet_ids])
    volunteer = get_volunteer_from_id(interface, volunteer_at_event.volunteer_id)
    cadets_at_event_data = CadetsAtEventData(interface.data)
    active_connected_cadets = ListOfCadets([cadet for cadet in connected_cadets if cadet.id in cadets_at_event_data.list_of_active_cadet_ids_at_event(event)])

    if len(active_connected_cadets)==0:
        return '%s is not connected to any active (not cancelled) cadets at this event' % volunteer.name



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

    if len(warnings)>0:
        prefix = "%s: " % volunteer.name
        return prefix+", ".join(warnings)
    else:
        return ''


