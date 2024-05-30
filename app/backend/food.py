from app.objects.food import FoodRequirements

from app.backend.data.food import FoodData
from app.objects.events import Event

from app.objects.abstract_objects.abstract_interface import abstractInterface


def is_cadet_with_id_already_at_event_with_food(interface: abstractInterface, event: Event, cadet_id: str)-> bool:
    food_data = FoodData(interface.data)
    cadets_with_food= food_data.get_list_of_cadets_with_food_at_event(event)

    return cadet_id in cadets_with_food.list_of_cadet_ids()



def add_new_cadet_with_food_to_event(
        interface: abstractInterface,
        event: Event, food_requirements: FoodRequirements,
        cadet_id: str
    ):
    food_data = FoodData(interface.data)
    food_data.add_new_cadet_with_food_to_event(event=event, cadet_id=cadet_id, food_requirements=food_requirements)

def is_volunteer_with_id_already_at_event_with_food(interface: abstractInterface, event: Event, volunteer_id: str) -> bool:
    food_data = FoodData(interface.data)
    volunteers_with_food = food_data.get_list_of_volunteeers_with_food_at_event(event)

    return volunteer_id in volunteers_with_food.list_of_volunteer_ids()

def add_new_volunteer_with_food_to_event(
        interface: abstractInterface,
        event: Event, food_requirements: FoodRequirements,
        volunteer_id: str
):
    food_data = FoodData(interface.data)
    food_data.add_new_volunteer_with_food_to_event(event=event, volunteer_id=volunteer_id, food_requirements=food_requirements)


def update_cadet_food_data(interface: abstractInterface, event: Event, cadet_id: str, new_food_requirements: FoodRequirements):
    food_data = FoodData(interface.data)
    food_data.change_food_requirements_for_cadet(event=event, cadet_id=cadet_id, food_requirements=new_food_requirements)

def update_volunteer_food_data(interface: abstractInterface, event: Event, volunteer_id: str, new_food_requirements: FoodRequirements):
    food_data = FoodData(interface.data)
    food_data.change_food_requirements_for_volunteer(event=event, volunteer_id=volunteer_id, food_requirements=new_food_requirements)
