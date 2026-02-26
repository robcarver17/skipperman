from typing import Dict

from app.objects.composed.volunteer_roles import (
    RoleWithSkills
)
from app.objects.events import Event
from app.objects.volunteer_role_targets import ListOfTargetForRoleWithIdAtEvent


class DictOfTargetsForRolesAtEvent(Dict[RoleWithSkills, int]):
    def __init__(
        self,
        raw_dict: Dict[RoleWithSkills, int],
        list_of_targets_with_role_ids: ListOfTargetForRoleWithIdAtEvent,
        event: Event,
    ):
        super().__init__(raw_dict)
        self._list_of_targets_with_role_ids = list_of_targets_with_role_ids
        self._event = event


    def get_target_for_role(self, role: RoleWithSkills) -> int:
        return self.get(role, 0)

    @property
    def event(self) -> Event:
        return self._event

    @property
    def list_of_targets_with_role_ids(self) -> ListOfTargetForRoleWithIdAtEvent:
        return self._list_of_targets_with_role_ids


