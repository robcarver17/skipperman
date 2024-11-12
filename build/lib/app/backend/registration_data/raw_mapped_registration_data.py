from app.objects.registration_data import RegistrationDataForEvent

from app.data_access.store.object_store import ObjectStore

from app.objects.events import Event

from app.data_access.store.object_definitions import (
    object_definition_for_mapped_registration_data,
)


def does_event_have_imported_registration_data(
    object_store: ObjectStore, event: Event
) -> bool:
    reg_data = get_raw_mapped_registration_data(object_store=object_store, event=event)
    return len(reg_data) > 0


def get_raw_mapped_registration_data(
    object_store: ObjectStore, event: Event
) -> RegistrationDataForEvent:
    return object_store.get(
        object_definition=object_definition_for_mapped_registration_data,
        event_id=event.id,
    )

def update_raw_mapped_registration_data(
    object_store: ObjectStore, event: Event, registration_data: RegistrationDataForEvent):
    object_store.update(
        object_definition=object_definition_for_mapped_registration_data,
        event_id=event.id,
        new_object=registration_data
    )