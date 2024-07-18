from dataclasses import dataclass

from app.objects.exceptions import missing_data
from app.objects.generic_list_of_objects import GenericListOfObjects

from app.objects.generic_objects import GenericSkipperManObject


@dataclass
class TargetForRoleAtEvent(GenericSkipperManObject):
    role: str
    target: int


class ListOfTargetForRoleAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return TargetForRoleAtEvent

    def get_target_for_role(self, role: str) -> int:
        matching_item = self._get_target_object_for_role_at_event(role=role)
        if matching_item is missing_data:
            return 0

        return matching_item.target

    def set_target_for_role(self, role: str, target: int):
        matching_item = self._get_target_object_for_role_at_event(role=role)
        if matching_item is missing_data:
            self._add_target_for_role(role=role, target=target)
        else:
            self._update_target_for_role(role=role, target=target)

    def _add_target_for_role(self, role: str, target: int):
        self.append(TargetForRoleAtEvent(role=role, target=target))

    def _update_target_for_role(self, role: str, target):
        matching_item = self._get_target_object_for_role_at_event(role=role)
        matching_item.target = target

    def _get_target_object_for_role_at_event(self, role: str):
        matching = [item for item in self if item.role == role]
        if len(matching) > 1:
            raise Exception("Can't have duplicates")
        if len(matching) == 0:
            return missing_data

        return matching[0]
