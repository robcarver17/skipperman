from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import (
 DictOfCadetsAndBoatClassAndPartners,
)
from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore



def get_dict_of_cadets_and_boat_classes_and_partners_at_events(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsAndBoatClassAndPartners:
    return object_store.get(object_store.data_api.data_list_of_cadets_with_dinghies_at_event.get_dict_of_cadets_and_boat_classes_and_partners_at_events,
                            event=event)





