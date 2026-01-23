from typing import Dict

from app.backend.events.list_of_events import get_list_of_events
from app.backend.groups.cadets_with_groups_at_event import get_list_of_cadets_in_group
from app.backend.registration_data.cadet_registration_data import (
    get_availability_dict_for_cadets_at_event,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.attendance import (
    registration_not_taken,
 not_attending, unknown, Attendance,
)
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.composed.attendance import (
    AttendanceOnDay, AttendanceAtEventAcrossCadets,
)
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.groups import Group


def clean_attendance_data_for_event(interface: abstractInterface, event: Event):
    interface.update(
        interface.object_store.data_api.data_attendance_at_events_for_specific_cadet.delete_attendance_data_at_event,
        event=event
    )


def delete_raw_attendance_for_cadet_and_return_list_of_events(
    interface: abstractInterface, cadet: Cadet
):
    list_of_event_ids = interface.object_store.get(
        interface.object_store.data_api.data_attendance_at_events_for_specific_cadet.get_events_cadet_attended,
        cadet=cadet
    )
    interface.update(
        interface.object_store.data_api.data_attendance_at_events_for_specific_cadet.delete_attendance_data_for_cadet,
        cadet=cadet
    )
    list_of_events = get_list_of_events(interface.object_store)

    return list_of_events.subset_from_list_of_ids_retaining_order(list_of_event_ids)

def get_attendance_at_event_for_list_of_cadets(
    object_store: ObjectStore, list_of_cadets: ListOfCadets, event: Event
) -> AttendanceAtEventAcrossCadets:
    return object_store.get(
        object_store.data_api.data_attendance_at_events_for_specific_cadet.get_attendance_at_event_for_list_of_cadets,
                            list_of_cadets=list_of_cadets, event=event)


def clear_cache_attendance_at_event_for_list_of_cadets(
    object_store: ObjectStore, list_of_cadets: ListOfCadets, event: Event
) -> AttendanceAtEventAcrossCadets:
    return object_store.clear_item(
        object_store.data_api.data_attendance_at_events_for_specific_cadet.get_attendance_at_event_for_list_of_cadets,
                            list_of_cadets=list_of_cadets, event=event)




def get_attendance_at_event_for_cadets_in_group_at_event(
    object_store: ObjectStore, event: Event, group: Group
) -> AttendanceAtEventAcrossCadets:

    cadets_in_group = get_list_of_cadets_in_group(object_store=object_store,
                                                  event=event,
                                                  group=group)

    return get_attendance_at_event_for_list_of_cadets(
        object_store=object_store,
        event=event,
        list_of_cadets=cadets_in_group
    )


def mark_unknown_cadets_as_not_attending_or_unregistered(interface: abstractInterface, event: Event, group: Group, day: Day):
    availability_dict = get_availability_dict_for_cadets_at_event(
        object_store=interface.object_store, event=event
    )
    attendance_dict =get_attendance_on_day_for_cadets_in_group(
        object_store=interface.object_store, event=event, day=day,
        group=group
    )
    list_of_cadets = ListOfCadets(list(attendance_dict.keys()))
    for cadet in list_of_cadets:
        attending = availability_dict.get(cadet).available_on_day(day)
        attendance = registration_not_taken if attending else not_attending
        current_attendance = attendance_dict.get(cadet).current_attendance

        if current_attendance == unknown:
            ## set attedance
            update_attendance_for_cadet_on_day_at_event(
                interface=interface,
                event=event,
                cadet=cadet,
                day=day,
                attendance=attendance
            )

    #### NEEDS TO WRITE TO SQL, CLEAR THAT PART OF CACHE SO RELOADED
    clear_cache_attendance_at_event_for_list_of_cadets(object_store=interface.object_store,
                                                       event=event,
                                                       list_of_cadets=list_of_cadets)


def update_attendance_for_cadet_on_day_at_event(interface: abstractInterface, event: Event,
                                                cadet: Cadet, day: Day,
                                                attendance: Attendance):
    interface.update(interface.object_store.data_api.data_attendance_at_events_for_specific_cadet.update_attendance_for_cadet_on_day_at_event,
                     event=event,
                     cadet=cadet,
                     day=day,
                     attendance=attendance)


def get_attendance_on_day_for_cadets_in_group(
    object_store: ObjectStore, event: Event, group: Group, day: Day
) -> Dict[Cadet, AttendanceOnDay]:
    dict_of_attendance_at_event_for_list_of_cadets = get_attendance_at_event_for_cadets_in_group_at_event(
        object_store=object_store, event=event, group=group
    )

    return get_attendance_history_at_event_on_day(
        day=day,
        dict_of_attendance_at_event_for_list_of_cadets=dict_of_attendance_at_event_for_list_of_cadets
    )



def get_attendance_history_at_event_on_day(
    dict_of_attendance_at_event_for_list_of_cadets:  AttendanceAtEventAcrossCadets,
    day: Day,
) -> Dict[Cadet, AttendanceOnDay]:
    return dict(
        [
            (
                cadet,
                attendance_at_event.attendance_on_day(day),
            )
            for cadet, attendance_at_event in dict_of_attendance_at_event_for_list_of_cadets.items()
        ]
    )


def are_all_cadets_in_group_marked_in_registration_as_present_absent_or_late(
    object_store: ObjectStore, event: Event, group: Group, day: Day
) -> bool:
    attendance = get_attendance_on_day_for_cadets_in_group(
        object_store, event, group, day
    )
    attendance_for_all_cadets = list(attendance.values())
    requires_save = [
        attendance.current_attendance == registration_not_taken or attendance.current_attendance==unknown
        for attendance in attendance_for_all_cadets
    ]

    return not any(requires_save)
