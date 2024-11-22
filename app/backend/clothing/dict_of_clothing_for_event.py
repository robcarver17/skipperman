from app.data_access.store.object_definitions import object_definition_for_list_of_cadets_with_clothing_at_event
from app.data_access.store.object_store import ObjectStore
from app.objects.events import Event
from app.objects.composed.clothing_at_event import ListOfCadetsWithClothingAtEvent

def get_list_of_cadets_with_clothing_at_event(object_store: ObjectStore, event: Event) -> ListOfCadetsWithClothingAtEvent:
    return object_store.get(object_definition_for_list_of_cadets_with_clothing_at_event, event_id = event.id)

def update_list_of_cadets_with_clothing_at_event(object_store: ObjectStore, event: Event, list_of_cadets_with_clothing_at_event:ListOfCadetsWithClothingAtEvent):
    object_store.update(
        object_definition=object_definition_for_list_of_cadets_with_clothing_at_event,
        new_object=list_of_cadets_with_clothing_at_event,
        event_id = event.id
    )