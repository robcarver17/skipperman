from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.volunteers import Volunteer

from app.objects.cadets import Cadet

from app.data_access.store.object_store import ObjectStore

from app.objects.events import Event
from app.objects.food import FoodRequirements


def is_cadet_with_already_at_event_with_food(
    object_store: ObjectStore, event: Event, cadet: Cadet
) -> bool:
    return object_store.data_api.data_list_of_cadets_with_food_requirement_at_event.is_cadet_with_already_at_event_with_food(
                            event_id=event.id,
                            cadet_id=cadet.id)


def add_new_cadet_with_food_to_event(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    food_requirements: FoodRequirements,
):
    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_food_requirement_at_event.add_new_cadet_with_food_to_event,
        event_id=event.id,
        cadet_id=cadet.id,
        food_requirements=food_requirements)



def remove_food_requirements_for_cadet_at_event(
        interface: abstractInterface, event: Event, cadet: Cadet
):
    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_food_requirement_at_event.remove_food_requirements_for_cadet_at_event,
        event_id=event.id,
        cadet_id=cadet.id,
        )

def is_volunteer_with_already_at_event_with_food(
    object_store: ObjectStore, event: Event, volunteer: Volunteer
) -> bool:
    return object_store.data_api.data_list_of_volunteers_with_food_requirement_at_event.is_volunteer_with_already_at_event_with_food(
                            event_id=event.id,
                            volunteer_id=volunteer.id)


def add_new_volunteer_with_food_to_event(
    interface: abstractInterface,
    event: Event,
    food_requirements: FoodRequirements,
    volunteer: Volunteer,
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_with_food_requirement_at_event.add_new_volunteer_with_food_to_event,
        event_id=event.id,
        volunteer_id=volunteer.id,
        food_requirements=food_requirements)

def update_cadet_food_data(
        interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    new_food_requirements: FoodRequirements,
):
    print("updating %s with %s" % (cadet, new_food_requirements))
    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_food_requirement_at_event.update_cadet_food_data,
        event_id=event.id,
        cadet_id=cadet.id,
        new_food_requirements=new_food_requirements)


def update_volunteer_food_data(
        interface: abstractInterface,
    volunteer: Volunteer,
    event: Event,
    new_food_requirements: FoodRequirements,
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteers_with_food_requirement_at_event.update_volunteer_food_data,
        event_id=event.id,
        volunteer_id=volunteer.id,
        new_food_requirements=new_food_requirements)
