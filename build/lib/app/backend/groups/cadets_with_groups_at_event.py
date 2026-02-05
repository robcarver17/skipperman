from typing import List

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.day_selectors import Day
from app.objects.utilities.exceptions import arg_not_passed

from app.objects.cadet_attendance import DictOfDaySelectors

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_attendance_matrix_for_list_of_cadets_at_event,
    get_dict_of_all_event_info_for_cadets,
)
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.composed.cadets_at_event_with_groups import (
    DEPRECATE_DictOfCadetsWithDaysAndGroupsAtEvent, DictOfCadetsWithDaysAndGroupsAtEvent, DaysAndGroups,
)

from app.objects.events import Event

from app.data_access.store.object_definitions import (
    object_definition_for_cadets_with_ids_and_groups_at_event,
    object_definition_for_dict_of_cadets_with_groups_at_event,
)
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups

from app.data_access.store.object_store import ObjectStore
from app.objects.groups import Group, ListOfGroups


def get_joint_attendance_matrix_for_cadets_in_group_at_event(
    object_store: ObjectStore,
    event: Event,
    group: Group,
    list_of_cadets: ListOfCadets
) -> DictOfDaySelectors:
    attendance_data = get_attendance_matrix_for_list_of_cadets_at_event(
        object_store=object_store, event=event, list_of_cadets=list_of_cadets
    )
    attendance_in_group = get_attendance_matrix_for_group_at_event(
        object_store=object_store, event=event, group=group
    )

    joint_attendance = attendance_data.intersect(attendance_in_group)
    joint_attendance = joint_attendance.align_with_list_of_days(event.days_in_event())

    return joint_attendance


def get_attendance_matrix_for_group_at_event(
    object_store: ObjectStore, event: Event, group: Group
) -> DictOfDaySelectors:
    dict_of_cadets_with_days_and_groups = get_dict_of_cadets_with_groups_at_event(object_store=object_store, event=event)
    cadets_in_group_during_event = dict_of_cadets_with_days_and_groups.cadets_in_group_during_event(
        group
    )

    all_selectors = {}
    for cadet in cadets_in_group_during_event:
        days_and_groups = dict_of_cadets_with_days_and_groups.get_days_and_groups_for_cadet(
            cadet
        )
        all_selectors[cadet] = days_and_groups.day_selector_when_cadet_in_group(group)

    return DictOfDaySelectors(all_selectors)



def get_dict_of_cadets_with_groups_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsWithDaysAndGroupsAtEvent:
    return object_store.get(
            object_store.data_api.data_list_of_cadets_with_groups.get_dict_of_cadets_with_groups_at_event,
        event_id=event.id,
    )

def get_days_and_groups_for_cadet_at_event(object_store: ObjectStore, event: Event, cadet: Cadet)  -> DaysAndGroups:
    return object_store.get(
        object_store.data_api.data_list_of_cadets_with_groups.days_and_group_at_event_for_cadet,
        event_id=event.id,
        cadet_id=cadet.id
    )

def add_cadet_to_group_on_day(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
        day: Day,
        group: Group
):
    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_groups.add_cadet_to_group_on_day,
        event_id=event.id,
        cadet_id=cadet.id,
        day=day,
        group_id=group.id
    )





def get_list_of_groups_at_event_given_list_of_cadets(
    object_store: ObjectStore, event: Event, list_of_cadets: ListOfCadets
) -> List[Group]:
    group_allocation_data = get_group_allocations_for_event_active_cadets_only(
        object_store=object_store, event=event
    )
    list_of_groups = []
    for cadet in list_of_cadets:
        groups_for_cadet = group_allocation_data.get_days_and_groups_for_cadet(
            cadet
        ).list_of_groups
        list_of_groups += groups_for_cadet

    return list(set(list_of_groups))


def get_list_of_all_groups_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfGroups:
    return object_store.get(object_store.data_api.data_list_of_cadets_with_groups.get_list_of_all_groups_at_event, event=event)


def get_list_of_cadets_in_group(object_store: ObjectStore, event: Event, group: Group):
    return object_store.get(
        object_store.data_api.data_list_of_cadets_with_groups.get_list_of_cadets_in_group,
        group=group,
        event=event)

def get_group_allocations_for_event_active_cadets_only(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsWithDaysAndGroupsAtEvent:
    return object_store.get(object_store.data_api.data_list_of_cadets_with_groups.get_group_allocations_for_event_active_cadets_only, event=event)
