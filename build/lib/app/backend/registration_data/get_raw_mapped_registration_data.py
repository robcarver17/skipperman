from app.objects.registration_data import RegistrationDataForEvent

from app.data_access.store.object_store import ObjectStore

from app.objects.events import Event

from app.data_access.store.object_definitions import object_definition_for_mapped_registration_data

def get_raw_mapped_registration_data(object_store: ObjectStore, event: Event) -> RegistrationDataForEvent:
    return object_store.get(object_definition=object_definition_for_mapped_registration_data, event_id= event.id)