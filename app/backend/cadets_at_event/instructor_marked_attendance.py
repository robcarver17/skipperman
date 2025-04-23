from typing import Dict

from app.backend.groups.previous_groups import get_group_allocations_for_event_active_cadets_only
from app.backend.registration_data.cadet_registration_data import get_availability_dict_for_cadets_at_event
from app.data_access.store.object_definitions import object_definition_for_dict_of_cadets_with_attendance, object_definition_for_attendance_of_cadets_for_cadet_id
from app.data_access.store.object_store import ObjectStore
from app.objects.attendance import unknown, registration_not_taken, ListOfRawAttendanceItemsForSpecificCadet
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.composed.attendance import DictOfAttendanceAcrossEvents, AttendanceOnDay
from app.objects.attendance import Attendance
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import Group


def delete_raw_attendance_for_cadet_and_return_list_of_events(object_store: ObjectStore, cadet: Cadet):
    attendance = get_attendance_across_events_for_list_of_cadets(object_store, ListOfCadets([cadet]))
    events = attendance.attendance_for_cadet_across_days_and_events(cadet).list_of_events

    object_store.update(
        ListOfRawAttendanceItemsForSpecificCadet([]),
        object_definition=object_definition_for_attendance_of_cadets_for_cadet_id,
        cadet_id = cadet.id
    )

    return events

def get_attendance_across_events_for_list_of_cadets(object_store: ObjectStore, list_of_cadets: ListOfCadets) -> DictOfAttendanceAcrossEvents:
    return object_store.get(
        object_definition=object_definition_for_dict_of_cadets_with_attendance,
        list_of_cadet_ids = list_of_cadets.list_of_ids

    )

def update_attendance_across_events_for_list_of_cadets(object_store: ObjectStore, list_of_cadets: ListOfCadets,
                                                       dict_of_attendance_across_events_for_list_of_cadets: DictOfAttendanceAcrossEvents):
    object_store.update(
        object_definition=object_definition_for_dict_of_cadets_with_attendance,
        new_object=dict_of_attendance_across_events_for_list_of_cadets,
            list_of_cadet_ids = list_of_cadets.list_of_ids

    )

def get_attendance_across_events_for_cadets_in_group_at_event(object_store: ObjectStore, event: Event, group: Group) -> DictOfAttendanceAcrossEvents:
    all_group_allocations_at_event = get_group_allocations_for_event_active_cadets_only(
        object_store=object_store, event=event
    )
    cadets_in_group = all_group_allocations_at_event.cadets_in_group_during_event(group)
    cadets_in_group = cadets_in_group.sort_by_firstname()

    return get_attendance_across_events_for_list_of_cadets(object_store=object_store,
                                                           list_of_cadets=cadets_in_group)


def get_current_attendance_on_day_for_cadets_in_group(object_store: ObjectStore, event: Event, group: Group, day: Day) -> Dict[Cadet, AttendanceOnDay]:
    attendance = get_attendance_across_events_for_cadets_in_group_at_event(object_store=object_store,
                                                                           event=event,
                                                                           group=group)
    availability_dict = get_availability_dict_for_cadets_at_event(
        object_store=object_store,
        event=event
    )


    attendance.mark_unknown_cadets_as_not_attending_or_unregistered(
        event=event,
        day=day,
        availability_dict=availability_dict
    )

    current_attendance = get_current_attendance_at_event_on_day(day=day,
                                                                event=event,
                                                                dict_of_attendance_across_events_for_list_of_cadets=attendance)


    return current_attendance

def get_current_attendance_at_event_on_day(dict_of_attendance_across_events_for_list_of_cadets: DictOfAttendanceAcrossEvents,
                                    event: Event, day: Day) -> Dict[Cadet, AttendanceOnDay]:

    return dict(
        [
            (
                cadet,
             attendance_across_events.attendance_for_cadet_at_event(event).attendance_on_day(day)
             )
            for cadet, attendance_across_events in dict_of_attendance_across_events_for_list_of_cadets.items()
            ]
    )


def are_all_cadets_in_group_marked_in_registration_as_present_absent_or_late(object_store: ObjectStore,
                                            event: Event,
                                            group: Group,
                                            day: Day) -> bool:

    attendance = get_current_attendance_on_day_for_cadets_in_group(object_store, event, group, day)
    attendance_for_all_cadets = list(attendance.values())
    list_of_current_attendance = [attendance_for_cadet.current_attendance for attendance_for_cadet in attendance_for_all_cadets]
    requires_save = [current_attendance ==registration_not_taken
                     for current_attendance in list_of_current_attendance]

    return not any(requires_save)