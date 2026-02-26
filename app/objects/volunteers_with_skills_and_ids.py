from dataclasses import dataclass

from app.objects.utilities.exceptions import (
    arg_not_passed,

)
from app.objects.utilities.generic_list_of_objects import GenericListOfObjects
from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.utilities.generic_list_of_objects import (
    get_unique_object_with_multiple_attr_in_list,
)




@dataclass
class VolunteerSkillWithIds(GenericSkipperManObject):
    volunteer_id: str
    skill_id: str


class ListOfVolunteerSkillsWithIds(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return VolunteerSkillWithIds


    def object_matching_ids(
        self, volunteer_id: str, skill_id: str, default=arg_not_passed
    ):
        return get_unique_object_with_multiple_attr_in_list(
            some_list=self,
            dict_of_attributes={"skill_id": skill_id, "volunteer_id": volunteer_id},
            default=default,
        )
