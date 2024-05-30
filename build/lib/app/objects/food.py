
from dataclasses import dataclass
from typing import List

from app.objects.generic import GenericSkipperManObject, GenericListOfObjects, from_str_to_bool, from_bool_to_str

OTHER_IN_FOOD_REQUIRED = "other"
@dataclass
class FoodRequirements(GenericSkipperManObject):
    other: str = ""
    vegetarian: bool = False
    vegan: bool = False
    pescatarian: bool= False
    nut_allergy: bool= False
    lactose_intolerant: bool= False
    gluten_intolerant:  bool= False
    kosher: bool = False
    halal: bool = False


no_food_requirements = FoodRequirements()


def guess_food_requirements_from_food_field(food_field_str: str)-> FoodRequirements:
    food_field_str_lower = food_field_str.lower()
    vegetarian = "vegetarian" in food_field_str_lower or "veggie" in food_field_str_lower
    vegan = "vegan" in food_field_str_lower
    pescatarian = "pescatarian" in food_field_str_lower
    nut_allergy = "nut" in food_field_str_lower
    lactose_intolerant = "lactose" in food_field_str_lower
    gluten_intolerant = "gluten" in food_field_str_lower or "coeliac" in food_field_str_lower
    kosher = "kosher" in food_field_str_lower
    halal = "halal" in food_field_str_lower

    if food_field_str_lower in ["none", "na", "n/a", "no", "no allergies"]:
        food_field_str = ""

    return FoodRequirements(
        other=food_field_str,
        vegetarian=vegetarian,
        vegan=vegan,
        pescatarian=pescatarian,
        nut_allergy=nut_allergy,
        lactose_intolerant=lactose_intolerant,
        gluten_intolerant=gluten_intolerant,
        kosher=kosher,
        halal=halal
    )




CADET_ID = "cadet_id"

@dataclass
class CadetWithFoodRequirementsAtEvent(GenericSkipperManObject):
    cadet_id: str
    food_requirements: FoodRequirements

    def as_str_dict(self) ->dict:
        food_required_as_dict = self.food_requirements.as_str_dict()
        food_required_as_dict[CADET_ID] = self.cadet_id

        return food_required_as_dict

    @classmethod
    def from_dict(cls, some_dict: dict) -> 'CadetWithFoodRequirementsAtEvent':
        cadet_id = str(some_dict.pop(CADET_ID))
        food_required = FoodRequirements.from_dict(some_dict)

        return cls(cadet_id=cadet_id, food_requirements = food_required)

class ListOfCadetsWithFoodRequirementsAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetWithFoodRequirementsAtEvent

    def change_food_requirements_for_cadet(self, cadet_id: str, food_requirements: FoodRequirements):
        cadet_in_data = self.object_with_cadet_id(cadet_id)
        cadet_in_data.food_requirements = food_requirements

    def add_new_cadet_with_food_to_event(
            self,
            cadet_id: str,
            food_requirements: FoodRequirements,
    ):
        try:
            assert cadet_id not in self.list_of_cadet_ids()
        except:
            raise ("Cadet already has food_and_clothing requirements")

        self.append(CadetWithFoodRequirementsAtEvent(cadet_id=cadet_id, food_requirements=food_requirements))

    def list_of_cadet_ids(self) -> List[str]:
        return [object.cadet_id for object in self]

    def object_with_cadet_id(self, cadet_id) -> CadetWithFoodRequirementsAtEvent:
        list_of_ids = self.list_of_cadet_ids()
        idx = list_of_ids.index(cadet_id)

        return self[idx]

    def filter_for_list_of_cadet_ids(self, list_of_cadet_ids: List[str]) -> 'ListOfCadetsWithFoodRequirementsAtEvent':
        return ListOfCadetsWithFoodRequirementsAtEvent([object for object in self if object.cadet_id in list_of_cadet_ids])

VOLUNTEER_ID = "volunteer_id"
@dataclass
class VolunteerWithFoodRequirementsAtEvent(GenericSkipperManObject):
    volunteer_id: str
    food_requirements: FoodRequirements


    def as_str_dict(self) ->dict:
        food_required_as_dict = self.food_requirements.as_str_dict()
        food_required_as_dict[VOLUNTEER_ID] = self.volunteer_id

        return food_required_as_dict

    @classmethod
    def from_dict(cls, some_dict: dict) -> 'VolunteerWithFoodRequirementsAtEvent':
        volunteer_id = str(some_dict.pop(VOLUNTEER_ID))
        food_required = FoodRequirements.from_dict(some_dict)

        return cls(volunteer_id=volunteer_id, food_requirements = food_required)

class ListOfVolunteersWithFoodRequirementsAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return VolunteerWithFoodRequirementsAtEvent

    def change_food_requirements_for_volunteer(self, volunteer_id: str, food_requirements: FoodRequirements):
        volunteer_in_data = self.object_with_volunteer_id(volunteer_id)
        volunteer_in_data.food_requirements = food_requirements

    def add_new_volunteer_with_food_to_event(
            self,
            volunteer_id: str,
            food_requirements: FoodRequirements,
    ):
        try:
            assert volunteer_id not in self.list_of_volunteer_ids()
        except:
            raise ("Volunteer already has food_and_clothing requirements")

        self.append(VolunteerWithFoodRequirementsAtEvent(volunteer_id=volunteer_id, food_requirements=food_requirements))

    def list_of_volunteer_ids(self) -> List[str]:
        return [object.volunteer_id for object in self]

    def object_with_volunteer_id(self, volunteer_id: str) -> VolunteerWithFoodRequirementsAtEvent:
        list_of_ids = self.list_of_volunteer_ids()
        idx = list_of_ids.index(volunteer_id)

        return self[idx]

    def filter_for_list_of_volunteer_ids(self, list_of_volunteer_ids: List[str]) -> 'ListOfVolunteersWithFoodRequirementsAtEvent':
        return ListOfVolunteersWithFoodRequirementsAtEvent([object for object in self if object.volunteer_id in list_of_volunteer_ids])


PERSON_NAME = "name"
CHILD = "child"
MEAL = "meal_name"
@dataclass
class PersonWithFoodRequirementsAtEvent(GenericSkipperManObject):
    name: str
    food_requirements: FoodRequirements
    meal_name: str = ''
    child: bool = False

    def as_str_dict(self) ->dict:
        food_required_as_dict = self.food_requirements.as_str_dict()
        food_required_as_dict[PERSON_NAME] = getattr(self, PERSON_NAME)
        food_required_as_dict[CHILD] = from_bool_to_str(getattr(self, CHILD))
        food_required_as_dict[MEAL] = getattr(self, MEAL)

        return food_required_as_dict

    @classmethod
    def from_dict(cls, some_dict: dict) -> 'PersonWithFoodRequirementsAtEvent':
        name = str(some_dict.pop(PERSON_NAME))
        child = from_str_to_bool(some_dict.pop(CHILD))
        meal = str(some_dict.pop(MEAL))
        food_required = FoodRequirements.from_dict(some_dict)

        return cls(name=name, food_requirements=food_required, child=child, meal_name=meal)


class ListOfPeopleWithFoodRequirementsAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return PersonWithFoodRequirementsAtEvent

    def subset_for_adults(self):
        return ListOfPeopleWithFoodRequirementsAtEvent([object for object in self if not object.child])

    def subset_for_children(self):
        return ListOfPeopleWithFoodRequirementsAtEvent([object for object in self if object.child])