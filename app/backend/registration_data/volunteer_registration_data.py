from typing import Dict

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadet_attendance import DictOfDaySelectors
from app.objects.day_selectors import DaySelector

from app.data_access.store.object_store import ObjectStore
from app.objects.composed.volunteers_at_event_with_registration_data import (
    DictOfRegistrationDataForVolunteerAtEvent,
)
from app.objects.events import Event
from app.objects.volunteer_at_event_with_id import ListOfVolunteersAtEventWithId
from app.objects.volunteers import Volunteer

def get_availability_volunteer_at_event(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
) -> DaySelector:
    dict_of_availability = get_availability_dict_for_volunteers_at_event(
        object_store=object_store,
        event=event
    )
    return dict_of_availability[volunteer]


def get_availability_dict_for_volunteers_at_event(
    object_store: ObjectStore, event: Event
) -> Dict[Volunteer, DaySelector]:
    return object_store.get(
        object_store.data_api.data_list_of_volunteers_at_event.get_availability_dict_for_volunteers_at_event,
        event_id=event.id
    )

def get_dict_of_registration_data_for_volunteers_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfRegistrationDataForVolunteerAtEvent:
    return object_store.get(
        object_store.data_api.data_list_of_volunteers_at_event.get_dict_of_registration_data_for_volunteers_at_event,
        event_id=event.id
    )


def get_list_of_registration_data_for_volunteers_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfVolunteersAtEventWithId:
    return object_store.get(
        object_store.data_api.data_list_of_volunteers_at_event.read,
        event_id=event.id
    )


def update_list_of_registration_data_for_volunteers_at_event(
    interface: abstractInterface, event: Event,
list_of_volunteers_at_event: ListOfVolunteersAtEventWithId
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event.write,
        list_of_volunteers_at_event=list_of_volunteers_at_event,
        event_id=event.id
    )

def is_volunteer_already_at_event(
    object_store: ObjectStore, volunteer: Volunteer, event: Event
) -> bool:
    return object_store.data_api.data_list_of_volunteers_at_event.is_volunteer_already_at_event(
        event_id=event.id, volunteer_id=volunteer.id
    )


def get_attendance_matrix_for_list_of_volunteers_at_event(
    object_store: ObjectStore,
    event: Event,
) -> DictOfDaySelectors:
    dict_of_registration_data_for_volunteers_at_event= get_dict_of_registration_data_for_volunteers_at_event(object_store=object_store, event=event)
    dict_of_availability = dict([
        (volunteer, registration_data.availablity) for volunteer, registration_data in dict_of_registration_data_for_volunteers_at_event.items()
    ])

    return DictOfDaySelectors(dict_of_availability)
