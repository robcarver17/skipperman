from typing import List

from app.backend.groups.previous_groups import (
    get_group_allocations_for_event_active_cadets_only,
)
from app.objects.exceptions import arg_not_passed

from app.objects.day_selectors import Day
from app.objects.cadet_attendance import DictOfDaySelectors

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_attendance_matrix_for_list_of_cadets_at_event,
    get_dict_of_all_event_info_for_cadets,
)
from app.backend.registration_data.cadet_registration_data import (
    is_cadet_unavailable_on_day,
)
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.composed.cadets_at_event_with_groups import (
    DictOfCadetsWithDaysAndGroupsAtEvent,
)

from app.objects.events import Event

from app.data_access.store.object_definitions import (
    object_definition_for_cadets_with_ids_and_groups_at_event,
    object_definition_for_dict_of_cadets_with_groups_at_event,
)
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups

from app.data_access.store.object_store import ObjectStore
from app.objects.groups import Group



def get_joint_attendance_matrix_for_cadets_in_group_at_event(
    object_store: ObjectStore,
    event: Event,
    group: Group,
    list_of_cadets: ListOfCadets = arg_not_passed,
):
    if list_of_cadets is arg_not_passed:
        all_cadet_event_data = get_dict_of_all_event_info_for_cadets(
            object_store=object_store, event=event, active_only=True
        )
        list_of_cadets = all_cadet_event_data.dict_of_cadets_with_days_and_groups.cadets_in_group_during_event(
            group
        )

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
    all_cadet_event_data = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event, active_only=True
    )
    cadets_in_group_during_event = all_cadet_event_data.dict_of_cadets_with_days_and_groups.cadets_in_group_during_event(
        group
    )

    all_selectors = {}
    for cadet in cadets_in_group_during_event:
        days_and_groups = all_cadet_event_data.dict_of_cadets_with_days_and_groups.get_days_and_groups_for_cadet(
            cadet
        )
        all_selectors[cadet] = days_and_groups.day_selector_when_cadet_in_group(group)

    return DictOfDaySelectors(all_selectors)


### FOLLOWING NEW CODE MIGHT NOT BE NEEDED
def get_dict_of_cadets_with_groups_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsWithDaysAndGroupsAtEvent:
    return object_store.get(
        object_definition=object_definition_for_dict_of_cadets_with_groups_at_event,
        event_id=event.id,
    )


def update_dict_of_cadets_with_groups_at_event(
    object_store: ObjectStore,
    event: Event,
    dict_of_cadets_with_groups_at_event: DictOfCadetsWithDaysAndGroupsAtEvent,
):
    object_store.update(
        new_object=dict_of_cadets_with_groups_at_event,
        object_definition=object_definition_for_dict_of_cadets_with_groups_at_event,
        event_id=event.id,
    )


def get_list_of_cadets_with_ids_with_groups_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfCadetIdsWithGroups:
    return object_store.get(
        object_definition=object_definition_for_cadets_with_ids_and_groups_at_event,
        event_id=event.id,
    )


def update_list_of_cadets_with_ids_with_groups_at_event(
    object_store: ObjectStore,
    event: Event,
    list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups,
):
    object_store.update(
        new_object=list_of_cadet_ids_with_groups,
        object_definition=object_definition_for_cadets_with_ids_and_groups_at_event,
        event_id=event.id,
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
