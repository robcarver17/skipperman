from typing import Dict, List


from app.objects.food import (
    FoodRequirements,
    no_food_requirements,
)
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.volunteers import ListOfVolunteers, Volunteer
from app.objects.utilities.exceptions import arg_not_passed


class DictOfCadetsWithFoodRequirementsAtEvent(Dict[Cadet, FoodRequirements]):
    def remove_empty_food_required(self):
        for food_required in self.values():
            food_required.clear_other_field_if_empty()

    def subset_matches_food_required_description(
        self, specific_food_requirements: FoodRequirements
    ):
        raw_dict = dict(
            [
                (cadet, food_requirements)
                for cadet, food_requirements in self.items()
                if food_requirements == specific_food_requirements
            ]
        )
        return DictOfCadetsWithFoodRequirementsAtEvent(raw_dict)

    def unique_list_of_food_requirements(self) -> List[FoodRequirements]:
        unique_list = list(set(self.values()))
        unique_list = [item for item in unique_list if not item.is_empty()]

        return unique_list

    def filter_for_list_of_cadets(self, list_of_cadets: ListOfCadets):
        raw_dict = dict(
            [(cadet, self.food_for_cadet(cadet)) for cadet in list_of_cadets]
        )
        return DictOfCadetsWithFoodRequirementsAtEvent(raw_dict)

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))

    def food_for_cadet(self, cadet: Cadet, default=arg_not_passed) -> FoodRequirements:
        if default is arg_not_passed:
            default = no_food_requirements

        food = self.get(cadet, default)

        return food


class DictOfVolunteersWithFoodRequirementsAtEvent(Dict[Volunteer, FoodRequirements]):
    def remove_empty_food_required(self):
        for food_required in self.values():
            food_required.clear_other_field_if_empty()

    def subset_matches_food_required_description(
        self, specific_food_requirements: FoodRequirements
    ):
        raw_dict = dict(
            [
                (volunteer, food_requirements)
                for volunteer, food_requirements in self.items()
                if food_requirements == specific_food_requirements
            ]
        )
        return DictOfVolunteersWithFoodRequirementsAtEvent(raw_dict)

    def unique_list_of_food_requirements(self) -> List[FoodRequirements]:
        unique_list = list(set(self.values()))
        unique_list = [item for item in unique_list if not item.is_empty()]

        return unique_list

    def filter_for_list_of_volunteers(self, list_of_volunteers: ListOfVolunteers):
        raw_dict = dict(
            [
                (volunteer, self.food_for_volunteer(volunteer))
                for volunteer in list_of_volunteers
            ]
        )
        return DictOfVolunteersWithFoodRequirementsAtEvent(raw_dict)

    def food_for_volunteer(
        self, volunteer: Volunteer, default=arg_not_passed
    ) -> FoodRequirements:
        if default is arg_not_passed:
            default = no_food_requirements
        food = self.get(volunteer, default)

        return food

    def list_of_volunteers(self) -> ListOfVolunteers:
        return ListOfVolunteers(list(self.keys()))
