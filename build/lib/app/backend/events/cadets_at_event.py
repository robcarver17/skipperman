from typing import List

from app.objects.exceptions import arg_not_passed

from app.objects.cadets import ListOfCadets

from app.objects.day_selectors import DictOfDaySelectors, DaySelector

from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_all_event_info_for_cadet,
)
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadet
from app.objects.groups import ListOfGroups


def get_health_notes_for_list_of_cadets_at_event(
    object_store: ObjectStore, list_of_cadets: ListOfCadets, event: Event
) -> List[str]:
    all_event_info = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event, active_only=True
    )

    health_notes = []
    for cadet_at_event in list_of_cadets:
        registration_data = all_event_info.dict_of_cadets_with_registration_data.registration_data_for_cadet(
            cadet_at_event
        )
        health_for_cadet = registration_data.health
        if len(health_for_cadet) == 0:
            health_for_cadet = "none"
        health_notes.append(health_for_cadet)

    return health_notes


def get_attendance_matrix_for_list_of_cadets_at_event(
    object_store: ObjectStore,
    event: Event,
    list_of_cadets: ListOfCadets = arg_not_passed,
) -> DictOfDaySelectors:
    all_event_info = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event, active_only=True
    )
    dict_of_availability = {}
    if arg_not_passed:
        list_of_cadets = all_event_info.list_of_cadets
    for cadet in list_of_cadets:
        cadet_at_event_data = all_event_info.dict_of_cadets_with_registration_data.get(
            cadet, None
        )
        if cadet_at_event_data is None:
            dict_of_availability[cadet] = DaySelector()
        else:
            dict_of_availability[cadet] = cadet_at_event_data.availability

    return DictOfDaySelectors(dict_of_availability)


def get_dict_of_all_event_info_for_cadets(
    object_store: ObjectStore, event: Event, active_only: bool = True
) -> DictOfAllEventInfoForCadet:
    return object_store.get(
        object_definition=object_definition_for_dict_of_all_event_info_for_cadet,
        event_id=event.id,
        active_only=active_only,
    )


def update_dict_of_all_event_info_for_cadets(
    object_store: ObjectStore,
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadet,
):
    object_store.update(
        new_object=dict_of_all_event_info_for_cadets,
        object_definition=object_definition_for_dict_of_all_event_info_for_cadet,
        event_id=dict_of_all_event_info_for_cadets.event.id,
    )


def get_list_of_all_groups_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfGroups:
    event_info = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event, active_only=True
    )
    return event_info.dict_of_cadets_with_days_and_groups.all_groups_at_event()
