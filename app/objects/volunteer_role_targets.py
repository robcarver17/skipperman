from dataclasses import dataclass

from app.objects.exceptions import missing_data, MultipleMatches, MissingData
from app.objects.generic_list_of_objects import GenericListOfObjects

from app.objects.generic_objects import GenericSkipperManObject


@dataclass
class TargetForRoleWithIdAtEvent(GenericSkipperManObject):
    role_id: str
    target: int


class ListOfTargetForRoleWithIdAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return TargetForRoleWithIdAtEvent

    def get_target_for_role(self, role: str) -> int:
        matching_item = self._get_target_object_for_role_at_event(role=role)
        if matching_item is missing_data:
            return 0

        return matching_item.target

    def set_target_for_role(self, role_id: str, target: int):
        matching_item = self._get_target_object_for_role_at_event(role_id)
        if matching_item is missing_data:
            self._add_target_for_role(role_id=role_id, target=target)
        else:
            self._update_target_for_role(role_id=role_id, target=target)

    def _add_target_for_role(self, role_id: str, target: int):
        self.append(TargetForRoleWithIdAtEvent(role_id=role_id, target=target))

    def _update_target_for_role(self, role_id: str, target):
        matching_item = self._get_target_object_for_role_at_event(role_id)
        matching_item.target = target

    def _get_target_object_for_role_at_event(self, role_id: str):
        matching = [item for item in self if item.role_id == role_id]
        if len(matching) > 1:
            raise MultipleMatches("Can't have duplicates")
        if len(matching) == 0:
            raise MissingData

        return matching[0]
