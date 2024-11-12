from app.objects.cadet_with_id_at_event import ListOfCadetsWithIDAtEvent

from app.data_access.store.object_store import ObjectStore

from app.objects.events import Event

from app.data_access.store.object_definitions import \
    object_definition_for_cadets_with_ids_and_registration_data_at_event, \
    object_definition_for_dict_of_cadets_with_registration_data_at_event
from app.objects.composed.cadets_at_event_with_registration_data import DictOfCadetsWithRegistrationData


def get_dict_of_cadets_with_registration_data(object_store: ObjectStore,
                                                              event: Event) -> DictOfCadetsWithRegistrationData:

    return object_store.get(object_definition=object_definition_for_dict_of_cadets_with_registration_data_at_event,
                            event_id=event.id)


def update_dict_of_cadets_with_registration_data(object_store: ObjectStore,
                                                 event: Event, dict_of_cadets_with_registration_data: DictOfCadetsWithRegistrationData):

    object_store.update(new_object=dict_of_cadets_with_registration_data,
                        object_definition=object_definition_for_dict_of_cadets_with_registration_data_at_event,
                        event_id = event.id)

def get_list_of_cadets_with_id_and_registration_data_at_event(object_store: ObjectStore,
                                                              event: Event) -> ListOfCadetsWithIDAtEvent:

    return object_store.get(object_definition_for_cadets_with_ids_and_registration_data_at_event,
                            event_id=event.id)

def update_list_of_cadets_with_id_and_registration_data_at_event(object_store: ObjectStore,
                                                              event: Event, list_of_cadets_with_id_at_event: ListOfCadetsWithIDAtEvent):

    object_store.update(list_of_cadets_with_id_at_event, object_definition=object_definition_for_cadets_with_ids_and_registration_data_at_event, event=event)
