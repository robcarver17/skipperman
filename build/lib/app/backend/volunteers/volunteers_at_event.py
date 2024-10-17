from app.objects.composed.volunteers_at_event_with_registration_data import DictOfRegistrationDataForVolunteerAtEvent
from app.objects.composed.volunteers_with_all_event_data import DictOfAllEventDataForVolunteers
from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import    object_definition_for_dict_of_registration_data_for_volunteers_at_event, \
    object_definition_for_dict_of_all_event_data_for_volunteers


def get_dict_of_all_event_data_for_volunteers(object_store: ObjectStore,event: Event)-> DictOfAllEventDataForVolunteers:
    return object_store.get(object_definition=
        object_definition_for_dict_of_all_event_data_for_volunteers,
                            event_id=event.id
    )

def get_dict_of_registration_data_for_volunteers_at_event(object_store: ObjectStore,event: Event) -> DictOfRegistrationDataForVolunteerAtEvent:
    return object_store.get(object_definition=object_definition_for_dict_of_registration_data_for_volunteers_at_event,
                            event_id = event.id)
