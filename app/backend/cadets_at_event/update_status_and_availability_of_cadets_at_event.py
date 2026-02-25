from copy import copy
from typing import List

from app.backend.boat_classes.cadets_with_boat_classes_at_event import \
    remove_cadet_from_boats_data_across_days_and_return_messages, \
    remove_cadet_from_boats_data_on_day_and_return_messages
from app.backend.clothing.dict_of_clothing_for_event import (
    remove_requirements_for_clothing_for_cadet_at_event,
)
from app.backend.food.modify_food_data import (
    remove_food_requirements_for_cadet_at_event,
)
from app.backend.cadets_at_event.cadet_availability import get_attendance_matrix_for_cadets_at_event, \
    make_cadet_available_on_day
from app.backend.registration_data.update_cadets_at_event import update_health_for_existing_cadet_at_event

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet
from app.objects.day_selectors import Day, DaySelector
from app.objects.events import Event
from app.objects.registration_data import RowInRegistrationData
from app.objects.registration_status import RegistrationStatus


def update_status_of_existing_cadet_at_event_to_cancelled_or_deleted_and_return_messages(
        interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    new_status: RegistrationStatus,
) -> List[str]:
    assert new_status.is_cancelled_or_deleted

    interface.update(
        interface.object_store.data_api.data_cadets_at_event.update_status_of_existing_cadet_at_event,
        event_id=event.id,
        cadet_id=cadet.id,
        new_status=new_status
    )

    interface.update(
        interface.object_store.data_api.data_list_of_cadets_at_event_with_club_dinghies.delete_cadet_from_event_and_return_messages,
        event_id=event.id,
        cadet_id=cadet.id
    )

    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_groups.delete_cadet_from_event_and_return_messages,
        event_id=event.id,
        cadet_id=cadet.id
    )

    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_clothing_at_event.delete_cadet_from_event_and_return_messages,
        event_id=event.id,
        cadet_id=cadet.id
    )

    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_food_requirement_at_event.delete_cadet_from_event_and_return_messages,
        event_id=event.id,
        cadet_id=cadet.id
    )

    msgs= remove_cadet_from_boats_data_across_days_and_return_messages(
        interface=interface,
        event=event,
        cadet=cadet,
    )

    return msgs


def update_availability_of_existing_cadet_at_event_and_return_messages(
        interface: abstractInterface,
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

    availability_dict = get_attendance_matrix_for_cadets_at_event(object_store=interface.object_store, event=event)
    existing_availablity = copy(
        availability_dict.get(cadet, DaySelector.create_empty())
    )

    messages = []
    for day in event.days_in_event():
        if existing_availablity.available_on_day(
                day
        ) == new_availabilty.available_on_day(day):
            continue

        if new_availabilty.available_on_day(day):
            make_cadet_available_on_day(interface=interface, event=event, day=day, cadet=cadet)
        else:
            message_for_day = remove_availability_of_existing_cadet_on_day_and_return_messages(
                interface=interface,
                event=event,
                cadet=cadet, day=day
            )

            messages += message_for_day

def remove_availability_of_existing_cadet_on_day_and_return_messages(
        interface: abstractInterface,
        event: Event,
        cadet: Cadet,
        day: Day

) -> List[str]:

    interface.update(
        interface.object_store.data_api.data_cadets_at_event.make_cadet_unavailable_on_day,
        event_id=event.id,
        cadet_id=cadet.id,
        day=day
    )

    interface.update(
        interface.object_store.data_api.data_list_of_cadets_at_event_with_club_dinghies.delete_club_dinghy_allocated_for_cadet_on_day_of_event,
        event_id=event.id,
        cadet_id=cadet.id,
        day=day

    )

    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_groups.set_cadet_to_unallocated_group_on_day,
        event_id=event.id,
        cadet_id=cadet.id,
        day=day
    )

    msg= remove_cadet_from_boats_data_on_day_and_return_messages(
        interface=interface,
        event=event,
        cadet=cadet,
        day=day
    )

    return [msg]


def update_status_of_existing_cadet_at_event_when_not_cancelling_or_deleting(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    new_status: RegistrationStatus,
):
    interface.update(
        interface.object_store.data_api.data_cadets_at_event.update_status_of_existing_cadet_at_event,
        event_id=event.id,
        cadet_id=cadet.id,
        new_status=new_status
    )


def update_registration_details_for_existing_cadet_at_event_who_was_manual(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    row_in_registration_data: RowInRegistrationData,
        new_health: str
):
    interface.update(
        interface.object_store.data_api.data_cadets_at_event.update_registration_details_for_existing_cadet_at_event_who_was_manual,
        event_id=event.id,
        cadet_id=cadet.id,
        row_in_registration_data=row_in_registration_data
    ) ##also does health and notes

    update_health_for_existing_cadet_at_event(
        interface=interface,
        event=event,
        cadet=cadet,
        new_health=new_health
    )

    remove_requirements_for_clothing_for_cadet_at_event(
        interface=interface, event=event, cadet=cadet
    )

    remove_food_requirements_for_cadet_at_event(
        interface=interface, event=event, cadet=cadet
    )
