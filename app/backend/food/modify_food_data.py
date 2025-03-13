from app.objects.volunteers import Volunteer

from app.objects.cadets import Cadet

from app.data_access.store.object_store import ObjectStore

from app.backend.food.dict_of_food_for_event import (
    get_dict_of_volunteers_with_food_requirements_at_event,
    get_dict_of_cadets_with_food_requirements_at_event,
    update_dict_of_cadets_with_food_requirements_at_event,
    update_dict_of_volunteers_with_food_requirements_at_event,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event
from app.objects.food import FoodRequirements


def is_cadet_with_already_at_event_with_food(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> bool:
    food_data = get_dict_of_cadets_with_food_requirements_at_event(
        object_store=object_store, event=event
    )
    return cadet in food_data.list_of_cadets()


def add_new_cadet_with_food_to_event(
    object_store: ObjectStore,
    event: Event,
    cadet: Cadet,
    food_requirements: FoodRequirements,
):
    food_data = get_dict_of_cadets_with_food_requirements_at_event(
        object_store=object_store, event=event
    )
    food_data.add_new_cadet_with_food_to_event(
        cadet=cadet, food_requirements=food_requirements
    )
    update_dict_of_cadets_with_food_requirements_at_event(
        object_store=object_store,
        event=event,
        dict_of_cadet_with_food_requirements=food_data,
    )


def remove_food_requirements_for_cadet_at_event(
    object_store: ObjectStore, event: Event, cadet: Cadet
):

    food_data = get_dict_of_cadets_with_food_requirements_at_event(
        object_store=object_store, event=event
    )
    food_data.remove_food_requirements_for_cadet_at_event(cadet=cadet)
    update_dict_of_cadets_with_food_requirements_at_event(
        object_store=object_store,
        event=event,
        dict_of_cadet_with_food_requirements=food_data,
    )


def is_volunteer_with_already_at_event_with_food(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
) -> bool:

    volunteers_with_food = get_dict_of_volunteers_with_food_requirements_at_event(
        object_store=object_store, event=event
    )

    return volunteer in volunteers_with_food.list_of_volunteers()


def add_new_volunteer_with_food_to_event(
    object_store: ObjectStore,
    event: Event,
    food_requirements: FoodRequirements,
    volunteer: Volunteer,
):
    volunteers_with_food = get_dict_of_volunteers_with_food_requirements_at_event(
        object_store=object_store, event=event
    )
    volunteers_with_food.add_new_volunteer_with_food_to_event(
        volunteer=volunteer, food_requirements=food_requirements
    )
    update_dict_of_volunteers_with_food_requirements_at_event(
        object_store=object_store,
        dict_of_volunteers_with_food_requirements=volunteers_with_food,
        event=event,
    )


def update_cadet_food_data(
    object_store: ObjectStore,
    event: Event,
    cadet: Cadet,
    new_food_requirements: FoodRequirements,
):
    food_data = get_dict_of_cadets_with_food_requirements_at_event(
        object_store=object_store, event=event
    )
    food_data.update_cadet_food_data(
        cadet=cadet, new_food_requirements=new_food_requirements
    )
    update_dict_of_cadets_with_food_requirements_at_event(
        object_store=object_store,
        event=event,
        dict_of_cadet_with_food_requirements=food_data,
    )


def update_volunteer_food_data(
    object_store: ObjectStore,
    volunteer: Volunteer,
    event: Event,
    new_food_requirements: FoodRequirements,
):
    dict_of_volunteers_with_food_requirements = (
        get_dict_of_volunteers_with_food_requirements_at_event(
            object_store=object_store, event=event
        )
    )
    dict_of_volunteers_with_food_requirements.update_volunteer_food_data(
        volunteer=volunteer, new_food_requirements=new_food_requirements
    )
    update_dict_of_volunteers_with_food_requirements_at_event(
        object_store=object_store,
        event=event,
        dict_of_volunteers_with_food_requirements=dict_of_volunteers_with_food_requirements,
    )
