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



