
from dataclasses import dataclass
from app.objects.generic import GenericSkipperManObject, GenericListOfObjects

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
        cadet_id = some_dict.pop(CADET_ID)
        food_required = FoodRequirements.from_dict(some_dict)

        return cls(cadet_id=cadet_id, food_requirements = food_required)

class ListOfCadetsWithFoodRequirementsAtEvent(GenericListOfObjects):
    def _object_class_contained(self):
        return CadetWithFoodRequirementsAtEvent


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
        volunteer_id = some_dict.pop(VOLUNTEER_ID)
        food_required = FoodRequirements.from_dict(some_dict)

        return cls(volunteer_id=volunteer_id, food_requirements = food_required)

class ListOfVolunteersWithFoodRequirementsAtEvent(GenericListOfObjects):
    def _object_class_contained(self):
        return VolunteerWithFoodRequirementsAtEvent
