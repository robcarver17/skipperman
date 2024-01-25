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

