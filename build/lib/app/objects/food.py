import datetime
from enum import Enum
from typing import Dict
from dataclasses import dataclass
from app.objects.generic import GenericSkipperManObject
from app.objects.volunteers import Volunteer

OTHER_IN_FOOD_REQUIRED = "other" ## must match key below
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