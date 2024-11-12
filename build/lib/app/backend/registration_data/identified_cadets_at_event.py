from app.objects.identified_cadets_at_event import ListOfIdentifiedCadetsAtEvent

from app.data_access.store.object_store import ObjectStore

from app.objects.events import Event

from app.data_access.store.object_definitions import (
    object_definition_for_identified_cadets_at_event,
)


def get_list_of_identified_cadets_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfIdentifiedCadetsAtEvent:
    return object_store.get(
        object_definition=object_definition_for_identified_cadets_at_event,
        event_id=event.id,
    )
