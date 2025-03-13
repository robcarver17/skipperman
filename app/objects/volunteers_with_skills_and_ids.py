from dataclasses import dataclass

from app.objects.exceptions import (
    MissingData,
    MultipleMatches,
    arg_not_passed,
    missing_data,
)
from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject
from app.objects.generic_list_of_objects import (
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

    def add(self, volunteer_id: str, skill_id: str):
        matching_object = self.object_matching_ids(
            volunteer_id=volunteer_id, skill_id=skill_id, default=missing_data
        )
        if matching_object is not missing_data:
            return

        self.append(VolunteerSkillWithIds(volunteer_id=volunteer_id, skill_id=skill_id))

    def delete(self, volunteer_id: str, skill_id: str):
        matching_object = self.object_matching_ids(
            volunteer_id=volunteer_id, skill_id=skill_id, default=missing_data
        )
        if matching_object is missing_data:
            return

        self.remove(matching_object)

    def object_matching_ids(
        self, volunteer_id: str, skill_id: str, default=arg_not_passed
    ):
        return get_unique_object_with_multiple_attr_in_list(
            some_list=self,
            dict_of_attributes={"skill_id": skill_id, "volunteer_id": volunteer_id},
            default=default,
        )
