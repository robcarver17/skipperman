from app.objects.composed.food_at_event import (
    DictOfCadetsWithFoodRequirementsAtEvent,
    DictOfVolunteersWithFoodRequirementsAtEvent,
)
from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore
from app.backend.registration_data.cadet_registration_data import (
    DEPRECATE_get_dict_of_cadets_with_registration_data,
)
from app.backend.registration_data.volunteer_registration_data import (
    get_dict_of_registration_data_for_volunteers_at_event,
)
from app.backend.food.dict_of_food_for_event import (
    get_dict_of_cadets_with_food_requirements_at_event,
    get_dict_of_volunteers_with_food_requirements_at_event,
)


def get_dict_of_active_cadets_with_food_requirements_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsWithFoodRequirementsAtEvent:
    registration_data = DEPRECATE_get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )
    all_food_data = get_dict_of_cadets_with_food_requirements_at_event(
        object_store=object_store, event=event
    )

    all_food_data_active_cadets = all_food_data.filter_for_list_of_cadets(
        registration_data.list_of_active_cadets()
    )
    all_food_data_active_cadets.remove_empty_food_required()

    return all_food_data_active_cadets


def get_dict_of_active_volunteers_with_food_requirements_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfVolunteersWithFoodRequirementsAtEvent:
    registration_data = get_dict_of_registration_data_for_volunteers_at_event(
        object_store=object_store, event=event
    )
    all_food_data = get_dict_of_volunteers_with_food_requirements_at_event(
        object_store=object_store, event=event
    )
    all_food_data_active_volunteers = all_food_data.filter_for_list_of_volunteers(
        registration_data.list_of_volunteers_at_event()
    )
    all_food_data_active_volunteers.remove_empty_food_required()


    return all_food_data_active_volunteers
