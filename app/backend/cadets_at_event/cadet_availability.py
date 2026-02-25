from typing import Dict

from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadet_attendance import DictOfDaySelectors
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets
from app.objects.day_selectors import DaySelector, Day
from app.backend.registration_data.cadet_registration_data import  get_dict_of_cadets_with_registration_data
from app.objects.events import Event
from app.objects.utilities.exceptions import arg_not_passed


def cadet_availability_at_event_from_dict_of_all_event_data(

    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet
) -> DaySelector:
    data_for_cadet = dict_of_all_event_data.event_data_for_cadet(cadet)
    is_active = data_for_cadet.is_active_registration()

    if not is_active:
        return DaySelector()

    return data_for_cadet.registration_data.availability


def cadet_is_unavailable_on_day_from_dict_of_event_data(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> bool:
    return not cadet_is_available_on_day_from_dict_of_event_data(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet, day=day
    )


def cadet_is_available_on_day_from_dict_of_event_data(
    dict_of_all_event_data: DictOfAllEventInfoForCadets, cadet: Cadet, day: Day
) -> bool:
    return cadet_availability_at_event_from_dict_of_all_event_data(
        dict_of_all_event_data=dict_of_all_event_data, cadet=cadet
    ).available_on_day(day)


def get_attendance_matrix_for_cadets_at_event(
    object_store: ObjectStore, event: Event
) -> Dict[Cadet, DaySelector]:
    registration_data = get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )
    return registration_data.availability_dict()


def get_attendance_matrix_for_list_of_cadets_at_event(
    object_store: ObjectStore,
    event: Event,
    list_of_cadets: ListOfCadets = arg_not_passed,
) -> DictOfDaySelectors:

    all_event_info = get_dict_of_cadets_with_registration_data(object_store=object_store, event=event)
    if list_of_cadets is arg_not_passed:
        list_of_cadets = all_event_info.list_of_cadets

    dict_of_availability = dict(
        [
            (cadet, all_event_info.get(cadet).availability_empty_if_inactive()) for cadet in list_of_cadets
        ]
    )

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



## NOTE: we don't have a counterpart for make unavailable, that is in update_status_and_availability
def make_cadet_available_on_day(
    interface: abstractInterface, event: Event, cadet: Cadet, day: Day
):
    interface.update(
        interface.object_store.data_api.data_cadets_at_event.make_cadet_available_on_day,
        event_id=event.id,
    cadet_id=cadet.id,
    day=day)
