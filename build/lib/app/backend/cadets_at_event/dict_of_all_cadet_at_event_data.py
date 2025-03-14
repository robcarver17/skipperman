from typing import List, Dict

from app.backend.registration_data.cadet_registration_data import add_empty_row_to_raw_registration_data_and_return_row, \
    add_new_cadet_to_event_from_row_in_registration_data
from app.backend.registration_data.identified_cadets_at_event import add_identified_cadet_and_row

from app.objects.exceptions import arg_not_passed

from app.objects.cadets import ListOfCadets, Cadet

from app.objects.day_selectors import DaySelector, Day
from app.objects.cadet_attendance import DictOfDaySelectors

from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_all_event_info_for_cadet,
)
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets
from app.objects.groups import ListOfGroups


def cadet_is_active(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
) -> bool:
    return dict_of_all_event_data.event_data_for_cadet(cadet).is_active_registration()


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
    if list_of_cadets is arg_not_passed:
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


def get_attendance_matrix_for_list_of_cadets_at_event_with_passed_event_info(
    all_event_info: DictOfAllEventInfoForCadets,
    list_of_cadets: ListOfCadets = arg_not_passed,
) -> DictOfDaySelectors:
    dict_of_availability = {}
    event_days = all_event_info.event.days_in_event()
    if list_of_cadets is arg_not_passed:
        list_of_cadets = all_event_info.list_of_cadets
    for cadet in list_of_cadets:
        cadet_at_event_data = all_event_info.dict_of_cadets_with_registration_data.get(
            cadet, None
        )
        if cadet_at_event_data is None:
            availability_for_cadet = DaySelector()
        else:
            availability_for_cadet = cadet_at_event_data.availability

        dict_of_availability[cadet] = availability_for_cadet.align_with_list_of_days(
            event_days
        )

    return DictOfDaySelectors(dict_of_availability)


def get_dict_of_all_event_info_for_cadets(
    object_store: ObjectStore, event: Event, active_only: bool = True
) -> DictOfAllEventInfoForCadets:
    return object_store.get(
        object_definition=object_definition_for_dict_of_all_event_info_for_cadet,
        event_id=event.id,
        active_only=active_only,
    )


def update_dict_of_all_event_info_for_cadets(
    object_store: ObjectStore,
    dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadets,
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


def get_availability_dict_for_active_cadets_at_event(
    object_store: ObjectStore, event: Event
) -> Dict[Cadet, DaySelector]:
    cadets_at_event_data = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event
    )

    active_cadets_at_event = get_list_of_active_cadets_at_event(
        object_store=object_store, event=event
    )
    registration_data = cadets_at_event_data.dict_of_cadets_with_registration_data

    return dict(
        [
            (cadet, registration_data.registration_data_for_cadet(cadet).availability)
            for cadet in active_cadets_at_event
        ]
    )


def get_list_of_active_cadets_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfCadets:
    cadets_at_event_data = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event, active_only=True
    )

    active_cadets_at_event = cadets_at_event_data.list_of_cadets

    return active_cadets_at_event


def cadet_is_unavailable_on_day(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> bool:
    return not cadet_is_available_on_day(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )


def cadet_is_available_on_day(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> bool:
    return cadet_availability_at_event(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    ).available_on_day(day)


def cadet_availability_at_event(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
) -> DaySelector:
    is_active = cadet_is_active(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    )
    if not is_active:
        return DaySelector()

    return dict_of_all_event_data.event_data_for_cadet(
        cadet
    ).registration_data.availability


def add_new_cadet_manually_to_event(
    object_store: ObjectStore,
    new_cadet: Cadet,
    event: Event,
):
    new_row = add_empty_row_to_raw_registration_data_and_return_row(
        object_store=object_store,
        event=event,
    )

    add_identified_cadet_and_row(
        object_store=object_store, event=event, row_id=new_row.row_id, cadet=new_cadet
    )

    add_new_cadet_to_event_from_row_in_registration_data(
        object_store=object_store,
        event=event,
        row_in_registration_data=new_row,
        cadet=new_cadet,
    )
