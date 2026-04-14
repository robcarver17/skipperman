from typing import Dict, List

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
        object_store=object_store, event=event
    )
    return dict_of_availability[volunteer]


def get_availability_dict_for_volunteers_at_event(
    object_store: ObjectStore, event: Event
) -> Dict[Volunteer, DaySelector]:
    availability_dict = object_store.get(
        object_store.data_api.data_list_of_volunteers_at_event.get_availability_dict_for_volunteers_at_event,
        event_id=event.id,
    )
    availability_dict = filter_out_registration_date(
        availability_dict=availability_dict, event=event
    )

    return availability_dict


def filter_out_registration_date(
    availability_dict: Dict[Volunteer, DaySelector], event: Event
) -> Dict[Volunteer, DaySelector]:
    event_volunteer_days_as_selector = DaySelector.from_list_of_days(
        event.volunteer_days_in_event()
    )
    return dict(
        [
            (
                volunteer,
                availability_combine_with_event_days_for_volunteer(
                    availability=availability,
                    event_volunteer_days_as_selector=event_volunteer_days_as_selector,
                ),
            )
            for volunteer, availability in availability_dict.items()
        ]
    )


def availability_combine_with_event_days_for_volunteer(
    availability: DaySelector, event_volunteer_days_as_selector: DaySelector
) -> DaySelector:
    return DaySelector.from_list_of_days(
        availability.days_that_intersect_with(event_volunteer_days_as_selector)
    )


def get_dict_of_registration_data_for_volunteers_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfRegistrationDataForVolunteerAtEvent:
    return object_store.get(
        object_store.data_api.data_list_of_volunteers_at_event.get_dict_of_registration_data_for_volunteers_at_event,
        event_id=event.id,
    )


def get_list_of_registration_data_for_volunteers_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfVolunteersAtEventWithId:
    return object_store.get(
        object_store.data_api.data_list_of_volunteers_at_event.read, event_id=event.id
    )


def update_list_of_registration_data_for_volunteers_at_event(
    interface: abstractInterface,
    event: Event,
    list_of_volunteers_at_event: ListOfVolunteersAtEventWithId,
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_at_event.write,
        list_of_volunteers_at_event=list_of_volunteers_at_event,
        event_id=event.id,
    )


def is_volunteer_at_event(
    object_store: ObjectStore, volunteer: Volunteer, event: Event
) -> bool:
    list_of_volunteer_ids_at_event = get_list_of_volunteer_ids_at_event(object_store=object_store, event=event)
    return volunteer.id in list_of_volunteer_ids_at_event

def get_list_of_volunteer_ids_at_event(object_store: ObjectStore,  event: Event) -> List[str]:
    return object_store.get(
        object_store.data_api.data_list_of_volunteers_at_event.list_of_volunteer_ids_at_event,
        event_id = event.id
    )


def get_attendance_matrix_for_list_of_volunteers_at_event(
    object_store: ObjectStore,
    event: Event,
) -> DictOfDaySelectors:
    dict_of_registration_data_for_volunteers_at_event = (
        get_dict_of_registration_data_for_volunteers_at_event(
            object_store=object_store, event=event
        )
    )
    dict_of_availability = dict(
        [
            (volunteer, registration_data.availablity)
            for volunteer, registration_data in dict_of_registration_data_for_volunteers_at_event.items()
        ]
    )

    return DictOfDaySelectors(dict_of_availability)
