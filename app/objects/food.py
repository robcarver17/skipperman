from copy import copy
from dataclasses import dataclass
from typing import List

from app.objects.utilities.exceptions import (
    arg_not_passed,
    missing_data,
)
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,
    get_unique_object_with_attr_in_list,
)
from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.utilities.utils import all_spaces

OTHER_IN_FOOD_REQUIRED = "other"

food_keys = [
    "vegetarian",
    "vegan",
    "pescatarian",
    "nut_allergy",
    "lactose_intolerant",
    "gluten_intolerant",
    "kosher",
    "halal",
]


@dataclass
class FoodRequirements(GenericSkipperManObject):
    other: str = ""
    vegetarian: bool = False
    vegan: bool = False
    pescatarian: bool = False
    nut_allergy: bool = False
    lactose_intolerant: bool = False
    gluten_intolerant: bool = False
    kosher: bool = False
    halal: bool = False

    def __repr__(self):
        return self.describe()

    def __hash__(self):
        return hash(self.describe())

    def __eq__(self, other):
        for key in food_keys:
            if not getattr(self, key) == getattr(other, key):
                return False

        return True

    @classmethod
    def create_empty(cls):
        return cls()

    def clear_other_field_if_empty(self):
        if all_spaces(self.other):
            self.other = ""

    def describe(self):
        description_list = []
        for key in food_keys:
            if getattr(self, key):
                description_list.append(key)

        if len(self.other) > 0:
            description_list.append(self.other)

        return ", ".join(description_list)


no_food_requirements = FoodRequirements.create_empty()


def guess_food_requirements_from_food_field(raw_food_field_str: str) -> FoodRequirements:
    food_field_str = copy(raw_food_field_str)
    food_field_str_lower = food_field_str.lower()
    for null_fields in ["just tasty food", "none", "na", "n/a", "no", "no allergies", ",", "-"]:
        food_field_str_lower = food_field_str_lower.replace(null_fields,'')

    food_required = FoodRequirements(
        other=food_field_str_lower)

    convert_food_required_from_str_to_bool(food_required, ["vegetarian", "veggie"], 'vegetarian', True)
    convert_food_required_from_str_to_bool(food_required, ["vegan"], 'vegan', True)
    convert_food_required_from_str_to_bool(food_required, ["pescatarian"], 'pescatarian', True)
    convert_food_required_from_str_to_bool(food_required, ["kohser", "kosher"], 'kosher', True)
    convert_food_required_from_str_to_bool(food_required, ["halal"], 'halal', True)

    convert_food_required_from_str_to_bool(food_required, ["lactose"], 'lactose', False)
    convert_food_required_from_str_to_bool(food_required, ["gluten", "coeliac", "gluten free"], 'gluten', False)
    convert_food_required_from_str_to_bool(food_required, ["nut"], 'nut_allergy',drop_from_text=False )

    food_required.clear_other_field_if_empty()

    return food_required


def convert_food_required_from_str_to_bool(food_requirements: FoodRequirements, list_of_str_to_check_for: List[str],
                                           attribute_to_modify: str, drop_from_text: bool = False):
    for str_to_check in list_of_str_to_check_for:
        if str_to_check in food_requirements.other:
            setattr(food_requirements, attribute_to_modify, True)
            if drop_from_text:
                food_requirements.other = food_requirements.other.replace(str_to_check, '')

    return food_requirements

CADET_ID = "cadet_id"


@dataclass
class CadetWithFoodRequirementsAtEvent(GenericSkipperManObject):
    cadet_id: str
    food_requirements: FoodRequirements

    def as_str_dict(self) -> dict:
        food_required_as_dict = self.food_requirements.as_str_dict()
        food_required_as_dict[CADET_ID] = self.cadet_id

        return food_required_as_dict

    @classmethod
    def from_dict_of_str(cls, some_dict: dict) -> "CadetWithFoodRequirementsAtEvent":
        cadet_id = str(some_dict.pop(CADET_ID))
        food_required = FoodRequirements.from_dict_of_str(some_dict)

        return cls(cadet_id=cadet_id, food_requirements=food_required)


class ListOfCadetsWithFoodRequirementsAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetWithFoodRequirementsAtEvent

    def remove_food_requirements_for_cadet_at_event(self, cadet_id: str):
        cadet_with_food = self.cadet_with_food_with_cadet_id(
            cadet_id, default=missing_data
        )
        if cadet_with_food is missing_data:
            return
        self.remove(cadet_with_food)

    def subset_matches_food_required_description(
        self, food_requirements: FoodRequirements
    ) -> "ListOfCadetsWithFoodRequirementsAtEvent":
        return ListOfCadetsWithFoodRequirementsAtEvent(
            [object for object in self if object.food_requirements == food_requirements]
        )

    def change_food_requirements_for_cadet(
        self, cadet_id: str, food_requirements: FoodRequirements
    ):
        cadet_in_data = self.cadet_with_food_with_cadet_id(
            cadet_id, default=missing_data
        )
        if cadet_in_data is missing_data:
            self.add_new_cadet_with_food_to_event(
                cadet_id=cadet_id, food_requirements=food_requirements
            )
        else:
            cadet_in_data.food_requirements = food_requirements

    def add_new_cadet_with_food_to_event(
        self,
        cadet_id: str,
        food_requirements: FoodRequirements,
    ):
        try:
            assert cadet_id not in self.list_of_cadet_ids()
        except:
            raise ("Cadet already has food requirements")

        self.append(
            CadetWithFoodRequirementsAtEvent(
                cadet_id=cadet_id, food_requirements=food_requirements
            )
        )

    def list_of_cadet_ids(self) -> List[str]:
        return [cadet_with_food.cadet_id for cadet_with_food in self]

    def cadet_with_food_with_cadet_id(
        self, cadet_id, default=arg_not_passed
    ) -> CadetWithFoodRequirementsAtEvent:
        return get_unique_object_with_attr_in_list(
            some_list=self, attr_name="cadet_id", attr_value=cadet_id, default=default
        )

    def filter_for_list_of_cadet_ids(
        self, list_of_cadet_ids: List[str]
    ) -> "ListOfCadetsWithFoodRequirementsAtEvent":
        return ListOfCadetsWithFoodRequirementsAtEvent(
            [object for object in self if object.cadet_id in list_of_cadet_ids]
        )


VOLUNTEER_ID = "volunteer_id"


@dataclass
class VolunteerWithFoodRequirementsAtEvent(GenericSkipperManObject):
    volunteer_id: str
    food_requirements: FoodRequirements

    def as_str_dict(self) -> dict:
        food_required_as_dict = self.food_requirements.as_str_dict()
        food_required_as_dict[VOLUNTEER_ID] = self.volunteer_id

        return food_required_as_dict

    @classmethod
    def from_dict_of_str(
        cls, some_dict: dict
    ) -> "VolunteerWithFoodRequirementsAtEvent":
        volunteer_id = str(some_dict.pop(VOLUNTEER_ID))
        food_required = FoodRequirements.from_dict_of_str(some_dict)

        return cls(volunteer_id=volunteer_id, food_requirements=food_required)


class ListOfVolunteersWithFoodRequirementsAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return VolunteerWithFoodRequirementsAtEvent

    def subset_matches_food_requirements(
        self, food_requirements: FoodRequirements
    ) -> "ListOfVolunteersWithFoodRequirementsAtEvent":
        return ListOfVolunteersWithFoodRequirementsAtEvent(
            [object for object in self if object.food_requirements == food_requirements]
        )

    def change_food_requirements_for_volunteer(
        self, volunteer_id: str, food_requirements: FoodRequirements
    ):
        if self.volunteer_has_food_already(volunteer_id):
            volunteer_in_data = self.volunteer_with_food_with_volunteer_id(volunteer_id)
            volunteer_in_data.food_requirements = food_requirements
        else:
            self.add_new_volunteer_with_food_to_event(
                volunteer_id=volunteer_id, food_requirements=food_requirements
            )

    def add_new_volunteer_with_food_to_event(
        self,
        volunteer_id: str,
        food_requirements: FoodRequirements,
    ):
        if self.volunteer_has_food_already(volunteer_id):
            raise ("Volunteer already has food requirements")

        self.append(
            VolunteerWithFoodRequirementsAtEvent(
                volunteer_id=volunteer_id, food_requirements=food_requirements
            )
        )

    def list_of_volunteer_ids(self) -> List[str]:
        return [object.volunteer_id for object in self]

    def drop_volunteer(self, volunteer_id: str):
        object_with_id = self.volunteer_with_food_with_volunteer_id(
            volunteer_id, default=missing_data
        )
        if object_with_id is missing_data:
            return
        self.remove(object_with_id)

    def volunteer_has_food_already(self, volunteer_id):
        volunteer_with_food = self.volunteer_with_food_with_volunteer_id(
            volunteer_id, default=missing_data
        )

        return not volunteer_with_food is missing_data

    def volunteer_with_food_with_volunteer_id(
        self, volunteer_id: str, default=arg_not_passed
    ) -> VolunteerWithFoodRequirementsAtEvent:
        return get_unique_object_with_attr_in_list(
            some_list=self,
            attr_name="volunteer_id",
            attr_value=volunteer_id,
            default=default,
        )

    def filter_for_list_of_volunteer_ids(
        self, list_of_volunteer_ids: List[str]
    ) -> "ListOfVolunteersWithFoodRequirementsAtEvent":
        return ListOfVolunteersWithFoodRequirementsAtEvent(
            [object for object in self if object.volunteer_id in list_of_volunteer_ids]
        )
