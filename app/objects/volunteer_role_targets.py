from dataclasses import dataclass

from app.objects.exceptions import missing_data,  arg_not_passed
from app.objects.generic_list_of_objects import GenericListOfObjects, get_unique_object_with_attr_in_list

from app.objects.generic_objects import GenericSkipperManObject


@dataclass
class TargetForRoleWithIdAtEvent(GenericSkipperManObject):
    role_id: str
    target: int


class ListOfTargetForRoleWithIdAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return TargetForRoleWithIdAtEvent

    def set_target_for_role(self, role_id: str, target: int):
        matching_item = self._get_target_object_for_role_at_event(role_id, default=missing_data)
        if matching_item is missing_data:
            self._add_target_for_role(role_id=role_id, target=target)
        else:
            self._update_target_for_role(role_id=role_id, target=target)

    def _add_target_for_role(self, role_id: str, target: int):
        self.append(TargetForRoleWithIdAtEvent(role_id=role_id, target=target))

    def _update_target_for_role(self, role_id: str, target):
        matching_item = self._get_target_object_for_role_at_event(role_id)
        matching_item.target = target

    def _get_target_object_for_role_at_event(self, role_id: str, default = arg_not_passed):
        return get_unique_object_with_attr_in_list(
            some_list=self,
            attr_name='role_id',
            attr_value=role_id,
            default=default
        )
