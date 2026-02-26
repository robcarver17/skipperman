from dataclasses import dataclass

from app.objects.utilities.exceptions import arg_not_passed
from app.objects.utilities.generic_objects import GenericSkipperManObjectWithIds
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    get_idx_of_unique_object_with_attr_in_list,
    get_unique_object_with_attr_in_list,
)


@dataclass
class Skill(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed
    protected: bool = False

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name


VOLUNTEERS_SKILL_FOR_PB2_NAME = "PB2"  ### DO NOT CHANGE
SI_SKILL_NAME = "SI"  ### DO NOT CHANGE


class ListOfSkills(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return Skill

    @property
    def PB2_skill(self):
        return self[self.idx_of_skill_with_name(VOLUNTEERS_SKILL_FOR_PB2_NAME)]

    @property
    def SI_skill(self):
        return self[self.idx_of_skill_with_name(SI_SKILL_NAME)]


    def skill_with_id(self, skill_id: str, default=arg_not_passed):
        return self.object_with_id(skill_id, default=default)

    def skill_with_name(self, skill_name, default=arg_not_passed):
        return get_unique_object_with_attr_in_list(
            self, attr_name="name", attr_value=skill_name, default=default
        )

    def idx_of_skill_with_name(self, skill_name: str, default=arg_not_passed) -> int:
        return get_idx_of_unique_object_with_attr_in_list(
            some_list=self, attr_name="name", attr_value=skill_name, default=default
        )

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_names()
        assert len(list_of_names) == len(set(list_of_names))
