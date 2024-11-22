from dataclasses import dataclass
from typing import Dict

from app.objects.food import ListOfCadetsWithFoodRequirementsAtEvent, FoodRequirements, ListOfVolunteersWithFoodRequirementsAtEvent
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.volunteers import ListOfVolunteers, Volunteer

class DictOfCadetsWithFoodRequirementsAtEvent(Dict[Cadet, FoodRequirements]):
    def __init__(self, raw_dict: Dict[Cadet, FoodRequirements],
                 list_of_cadets_with_ids_and_food_requirements: ListOfCadetsWithFoodRequirementsAtEvent):
        super().__init__(raw_dict)
        self._list_of_cadets_with_ids_and_food_requirements = list_of_cadets_with_ids_and_food_requirements

    @property
    def list_of_cadets_with_ids_and_food_requirements(self) -> ListOfCadetsWithFoodRequirementsAtEvent:
        return self._list_of_cadets_with_ids_and_food_requirements

def compose_dict_of_cadets_with_food_requirements_at_event(list_of_cadets: ListOfCadets,
                                                           list_of_cadets_with_ids_and_food_requirements: ListOfCadetsWithFoodRequirementsAtEvent)\
        -> DictOfCadetsWithFoodRequirementsAtEvent:

    raw_dict = dict([
        (list_of_cadets.cadet_with_id(cadet_with_id_and_food.cadet_id), cadet_with_id_and_food.food_requirements) for cadet_with_id_and_food in list_of_cadets_with_ids_and_food_requirements
    ])

    return DictOfCadetsWithFoodRequirementsAtEvent(
        raw_dict=raw_dict,
        list_of_cadets_with_ids_and_food_requirements=list_of_cadets_with_ids_and_food_requirements
    )



class DictOfVolunteersWithFoodRequirementsAtEvent(Dict[Volunteer, FoodRequirements]):
    def __init__(self, raw_dict: Dict[Volunteer, FoodRequirements],
                 list_of_volunteers_with_ids_and_food_requirements: ListOfVolunteersWithFoodRequirementsAtEvent):
        super().__init__(raw_dict)
        self._list_of_volunteers_with_ids_and_food_requirements = list_of_volunteers_with_ids_and_food_requirements

    @property
    def list_of_volunteers_with_ids_and_food_requirements(self) -> ListOfVolunteersWithFoodRequirementsAtEvent:
        return self._list_of_volunteers_with_ids_and_food_requirements


def compose_dict_of_volunteers_with_food_requirements_at_event(list_of_volunteers: ListOfVolunteers,
                                                           list_of_volunteers_with_ids_and_food_requirements: ListOfVolunteersWithFoodRequirementsAtEvent)\
        -> DictOfVolunteersWithFoodRequirementsAtEvent:

    raw_dict = dict([
        (list_of_volunteers.volunteer_with_id(volunteer_with_id_and_food.volunteer_id), volunteer_with_id_and_food.food_requirements)
        for volunteer_with_id_and_food in list_of_volunteers_with_ids_and_food_requirements
    ])

    return DictOfVolunteersWithFoodRequirementsAtEvent(
        raw_dict=raw_dict,
        list_of_volunteers_with_ids_and_food_requirements=list_of_volunteers_with_ids_and_food_requirements
    )


