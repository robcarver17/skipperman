from app.data_access.store.object_definitions import \
    object_definition_for_dict_of_cadets_with_food_requirements_at_event, \
    object_definition_for_dict_of_volunteers_with_food_requirements_at_event
from app.objects.composed.food_at_event import DictOfVolunteersWithFoodRequirementsAtEvent, DictOfCadetsWithFoodRequirementsAtEvent
from app.data_access.store.object_store import ObjectStore
from app.objects.events import Event

def get_dict_of_cadets_with_food_requirements_at_event(object_store: ObjectStore, event: Event) -> DictOfCadetsWithFoodRequirementsAtEvent:
    return object_store.get(
        object_definition=object_definition_for_dict_of_cadets_with_food_requirements_at_event,
        event_id = event.id
    )

def get_dict_of_volunteers_with_food_requirements_at_event(object_store: ObjectStore, event: Event) -> DictOfVolunteersWithFoodRequirementsAtEvent:
    return object_store.get(
        object_definition=object_definition_for_dict_of_volunteers_with_food_requirements_at_event,
        event_id = event.id
    )


def update_dict_of_cadets_with_food_requirements_at_event(object_store: ObjectStore, event: Event, dict_of_cadet_with_food_requirements: DictOfCadetsWithFoodRequirementsAtEvent):
    object_store.update(object_definition=object_definition_for_dict_of_cadets_with_food_requirements_at_event,
                        new_object=dict_of_cadet_with_food_requirements,
                        event_id = event.id)

def update_dict_of_volunteers_with_food_requirements_at_event(object_store: ObjectStore, event: Event,
                                                              dict_of_volunteers_with_food_requirements: DictOfVolunteersWithFoodRequirementsAtEvent):
    object_store.update(object_definition=object_definition_for_dict_of_volunteers_with_food_requirements_at_event,
                        new_object=dict_of_volunteers_with_food_requirements,
                        event_id = event.id)