from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet
from app.objects.composed.food_at_event import (
    DictOfVolunteersWithFoodRequirementsAtEvent,
    DictOfCadetsWithFoodRequirementsAtEvent,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.events import Event


def get_dict_of_cadets_with_food_requirements_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsWithFoodRequirementsAtEvent:
    return object_store.get(
        object_store.data_api.data_list_of_cadets_with_food_requirement_at_event.get_dict_of_cadets_with_food_requirements_at_event,
        event_id=event.id,
    )


def get_dict_of_volunteers_with_food_requirements_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfVolunteersWithFoodRequirementsAtEvent:
    return object_store.get(
        object_store.data_api.data_list_of_volunteers_with_food_requirement_at_event.get_dict_of_volunteers_with_food_requirements_at_event,
        event_id=event.id,
    )


def merge_food_at_event(interface: abstractInterface, cadet_to_delete: Cadet, cadet_to_keep: Cadet, event: Event):
    try:
        interface.update(
            interface.object_store.data_api.data_list_of_cadets_with_food_requirement_at_event.merge_food_at_event,
            event_id=event.id,
            cadet_id_to_delete=cadet_to_delete.id,
            cadet_id_to_keep=cadet_to_keep.id
        )
        interface.log_error("Merged food for %s and %s at event %s" % (cadet_to_keep, cadet_to_delete, event))
    except Exception as e:
        raise Exception("Can't merge food for %s with %s at %s, because %s" % (cadet_to_keep, cadet_to_delete, event, str(e)))