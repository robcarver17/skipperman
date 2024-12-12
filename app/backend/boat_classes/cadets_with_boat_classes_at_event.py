from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import (
    DictOfCadetsAndBoatClassAndPartners,
)
from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import (
    object_definition_for_cadets_with_ids_and_boat_classes_at_event,
    object_definition_for_dict_of_cadets_and_boat_classes_and_partners,
)
from app.objects.cadet_at_event_with_dinghy_with_ids import (
    ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
)


def get_dict_of_cadets_and_boat_classes_and_partners_at_events(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsAndBoatClassAndPartners:
    return object_store.get(
        object_definition=object_definition_for_dict_of_cadets_and_boat_classes_and_partners,
        event_id=event.id,
    )


def update_dict_of_cadets_and_boat_classes_and_partners_at_events(
    object_store: ObjectStore,
    event: Event,
    dict_of_cadets_and_boat_classes_and_partners_at_events: DictOfCadetsAndBoatClassAndPartners,
):
    object_store.update(
        object_definition=object_definition_for_dict_of_cadets_and_boat_classes_and_partners,
        event_id=event.id,
        new_object=dict_of_cadets_and_boat_classes_and_partners_at_events,
    )


def get_list_of_cadets_with_ids_with_boat_classes_at_event(
    object_store: ObjectStore, event: Event
) -> ListOfCadetAtEventWithBoatClassAndPartnerWithIds:
    return object_store.get(
        object_definition=object_definition_for_cadets_with_ids_and_boat_classes_at_event,
        event_id=event.id,
    )


def update_list_of_cadets_with_ids_with_boat_classes_at_event(
    object_store: ObjectStore,
    event: Event,
    list_of_cadet_ids_with_boat_classes_at_event: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
):
    object_store.update(
        new_object=list_of_cadet_ids_with_boat_classes_at_event,
        object_definition=object_definition_for_cadets_with_ids_and_boat_classes_at_event,
        event_id=event.id,
    )


