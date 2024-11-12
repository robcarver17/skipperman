from typing import List

from app.backend.events.cadets_at_event import get_dict_of_all_event_info_for_cadets, update_dict_of_all_event_info_for_cadets

from app.backend.registration_data.cadet_registration_data import \
    get_list_of_cadets_with_id_and_registration_data_at_event, \
    update_list_of_cadets_with_id_and_registration_data_at_event
from app.data_access.store.object_store import ObjectStore
from app.objects.cadets import Cadet
from app.objects.day_selectors import Day, DaySelector
from app.objects.events import Event
from app.objects.registration_status import RegistrationStatus


def update_status_of_existing_cadet_at_event_to_cancelled_or_deleted_and_return_messages(
        object_store: ObjectStore, event: Event, cadet: Cadet,    new_status: RegistrationStatus,
) -> List[str]:

    dict_of_all_event_info_for_cadets = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event, active_only=True
    )

    messages = dict_of_all_event_info_for_cadets.update_status_of_existing_cadet_in_event_info_to_cancelled_or_deleted_and_return_messages(
         cadet=cadet, new_status=new_status)
    update_dict_of_all_event_info_for_cadets(
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        object_store=object_store,
    )

    return messages


def make_cadet_available_on_day(
        object_store: ObjectStore, event: Event, cadet: Cadet,
         day: Day
):

    registration_data = get_list_of_cadets_with_id_and_registration_data_at_event(object_store=object_store, event=event)
    cadet_at_event =registration_data.cadet_at_event(cadet)
    cadet_at_event.availability.make_available_on_day(day)
    update_list_of_cadets_with_id_and_registration_data_at_event(object_store=object_store,
                                                                 event=event,
                                                                 list_of_cadets_with_id_at_event=registration_data)


def update_availability_of_existing_cadet_at_event_and_return_messages(
        object_store: ObjectStore, event: Event, cadet: Cadet,
    new_availabilty: DaySelector,
):

    dict_of_all_event_info_for_cadets = get_dict_of_all_event_info_for_cadets(
        object_store=object_store, event=event, active_only=True
    )

    messages = dict_of_all_event_info_for_cadets.update_availability_of_existing_cadet_at_event_and_return_messages(
         cadet=cadet, new_availabilty=new_availabilty)
    update_dict_of_all_event_info_for_cadets(
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        object_store=object_store,
    )

    return messages


def update_status_of_existing_cadet_at_event_when_not_cancelling_or_deleting(
        object_store: ObjectStore, event: Event, cadet: Cadet,    new_status: RegistrationStatus,
):

    registration_data = get_list_of_cadets_with_id_and_registration_data_at_event(object_store=object_store, event=event)
    registration_data.update_status_of_existing_cadet_at_event(
        cadet_id=cadet.id, new_status=new_status
    )
    update_list_of_cadets_with_id_and_registration_data_at_event(object_store=object_store,
                                                                 event=event,
                                                                 list_of_cadets_with_id_at_event=registration_data)
