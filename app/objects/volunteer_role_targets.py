from dataclasses import dataclass

from app.objects.utilities.generic_list_of_objects import GenericListOfObjects

from app.objects.utilities.generic_objects import GenericSkipperManObject


@dataclass
class TargetForRoleWithIdAtEvent(GenericSkipperManObject):
    role_id: str
    target: int


class ListOfTargetForRoleWithIdAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return TargetForRoleWithIdAtEvent
