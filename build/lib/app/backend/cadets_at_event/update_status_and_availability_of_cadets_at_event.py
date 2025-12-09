from typing import List

from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
    update_dict_of_all_event_info_for_cadets,
)
from app.backend.clothing.dict_of_clothing_for_event import (
    remove_clothing_for_cadet_at_event,
)
from app.backend.food.modify_food_data import (
    remove_food_requirements_for_cadet_at_event,
)

from app.data_access.store.object_store import ObjectStore
from app.objects.cadet_with_id_at_event import (
    CadetWithIdAtEvent,
    get_health_from_event_row,
)
from app.objects.cadets import Cadet
from app.objects.day_selectors import Day, DaySelector
from app.objects.events import Event
from app.objects.registration_data import RowInRegistrationData
from app.objects.registration_status import RegistrationStatus


def update_status_of_existing_cadet_at_event_to_cancelled_or_deleted_and_return_messages(
    object_store: ObjectStore,
    event: Event,
    cadet: Cadet,
    new_status: RegistrationStatus,
) -> List[str]:
    dict_of_all_event_info_for_cadets = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)

    messages = dict_of_all_event_info_for_cadets.update_status_of_existing_cadet_in_event_info_to_cancelled_or_deleted_and_return_messages(
        cadet=cadet, new_status=new_status
    )
    update_dict_of_all_event_info_for_cadets(
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        object_store=object_store,
    )

    return messages


from app.backend.registration_data.cadet_registration_data import (
    get_dict_of_cadets_with_registration_data,
    update_dict_of_cadets_with_registration_data,
)


def make_cadet_available_on_day(
    object_store: ObjectStore, event: Event, cadet: Cadet, day: Day
):
    dict_of_all_event_info_for_cadets = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)
    dict_of_all_event_info_for_cadets.make_cadet_available_on_day(cadet=cadet, day=day)
    update_dict_of_all_event_info_for_cadets(
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        object_store=object_store,
    )


def update_availability_of_existing_cadet_at_event_and_return_messages(
    object_store: ObjectStore,
    event: Event,
    cadet: Cadet,
    new_availabilty: DaySelector,
) -> List[str]:
    days_now_available = new_availabilty.days_that_intersect_with(
        event.day_selector_for_days_in_event()
    )
    if len(days_now_available) == 0:
        return [
            "Error: You have set availability for %s so they have no days of attendance. If they are not coming cancel then registration instead."
            % cadet.name
        ]

    dict_of_all_event_info_for_cadets = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)

    messages = dict_of_all_event_info_for_cadets.update_availability_of_existing_cadet_at_event_and_return_messages(
        cadet=cadet, new_availabilty=new_availabilty
    )

    update_dict_of_all_event_info_for_cadets(
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        object_store=object_store,
    )

    return messages


def update_status_of_existing_cadet_at_event_when_not_cancelling_or_deleting(
    object_store: ObjectStore,
    event: Event,
    cadet: Cadet,
    new_status: RegistrationStatus,
):
    dict_of_all_event_info_for_cadets = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)
    dict_of_all_event_info_for_cadets.update_status_of_existing_cadet_at_event_when_not_cancelling_or_deleting(
        cadet=cadet, new_status=new_status
    )
    update_dict_of_all_event_info_for_cadets(
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        object_store=object_store,
    )


def update_registration_details_for_existing_cadet_at_event_who_was_manual(
    object_store: ObjectStore,
    event: Event,
    cadet: Cadet,
    row_in_registration_data: RowInRegistrationData,
):
    dict_of_all_event_info_for_cadets = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)
    dict_of_all_event_info_for_cadets.update_registration_data_for_existing_cadet(
        cadet=cadet, row_in_registration_data=row_in_registration_data
    )
    dict_of_all_event_info_for_cadets.update_health_for_existing_cadet_at_event(
        cadet=cadet, new_health=get_health_from_event_row(row_in_registration_data)
    )
    update_dict_of_all_event_info_for_cadets(
        dict_of_all_event_info_for_cadets=dict_of_all_event_info_for_cadets,
        object_store=object_store,
    )

    remove_clothing_for_cadet_at_event(
        object_store=object_store, event=event, cadet=cadet
    )

    remove_food_requirements_for_cadet_at_event(
        object_store=object_store, event=event, cadet=cadet
    )
