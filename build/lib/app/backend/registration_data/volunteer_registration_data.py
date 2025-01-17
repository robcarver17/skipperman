from typing import Dict

from app.objects.day_selectors import DaySelector

from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_registration_data_for_volunteers_at_event,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.composed.volunteers_at_event_with_registration_data import (
    DictOfRegistrationDataForVolunteerAtEvent,
)
from app.objects.events import Event
from app.objects.volunteers import Volunteer


def get_availability_dict_for_volunteers_at_event(
    object_store: ObjectStore, event: Event
) -> Dict[Volunteer, DaySelector]:
    registration_data = get_dict_of_registration_data_for_volunteers_at_event(
        object_store=object_store, event=event
    )
    return dict(
        [
            (volunteer, registration_data.get_data_for_volunteer(volunteer).availablity)
            for volunteer in registration_data.list_of_volunteers_at_event()
        ]
    )


def get_dict_of_registration_data_for_volunteers_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfRegistrationDataForVolunteerAtEvent:
    return object_store.get(
        object_definition=object_definition_for_dict_of_registration_data_for_volunteers_at_event,
        event_id=event.id,
    )


def update_dict_of_registration_data_for_volunteers_at_event(
    object_store: ObjectStore,
    dict_of_registration_data: DictOfRegistrationDataForVolunteerAtEvent,
):
    object_store.update(
        new_object=dict_of_registration_data,
        object_definition=object_definition_for_dict_of_registration_data_for_volunteers_at_event,
        event_id=dict_of_registration_data.event.id,
    )


def is_volunteer_already_at_event(
    object_store: ObjectStore, volunteer: Volunteer, event: Event
) -> bool:
    dict_of_volunteers_at_event = get_dict_of_registration_data_for_volunteers_at_event(
        object_store=object_store, event=event
    )
    return volunteer in dict_of_volunteers_at_event.list_of_volunteers_at_event()
