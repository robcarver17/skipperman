from dataclasses import dataclass
from typing import List, Dict

from app.objects.exceptions import missing_data
from app.objects.generic_list_of_objects import GenericListOfObjects

from app.objects.generic_objects import GenericSkipperManObject
from app.objects.roles_and_teams import RolesWithSkillIds, ListOfRolesWithSkillIds
from app.objects.events import Event, ListOfEvents


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

    def set_target_for_role(self, role: str, target: int):
        matching_item = self._get_target_object_for_role_at_event(role=role)
        if matching_item is missing_data:
            self._add_target_for_role(role=role, target=target)
        else:
            self._update_target_for_role(role=role, target=target)

    def _add_target_for_role(self, role: str, target: int):
        self.append(TargetForRoleWithIdAtEvent(role=role, target=target))

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


class DictOfTargetsForRolesAtEvent(Dict[RolesWithSkillIds, int]):
    def __init__(self, raw_dict: Dict[RolesWithSkillIds, int], list_of_targets_with_role_ids: ListOfTargetForRoleWithIdAtEvent, event: Event):
        super().__init__(raw_dict)
        self._list_of_targets_with_role_ids = list_of_targets_with_role_ids
        self._event = event

    def get_target_for_role(self, role: RolesWithSkillIds) -> int:
        return self.get(role, 0)

    @property
    def event(self) -> Event:
        return self._event

    @property
    def list_of_targets_with_role_ids(self)-> ListOfTargetForRoleWithIdAtEvent:
        return self._list_of_targets_with_role_ids

def compose_list_of_targets_for_roles_at_event(list_of_targets_with_role_ids: ListOfTargetForRoleWithIdAtEvent,
                                               list_of_roles: ListOfRolesWithSkillIds,
                                               list_of_events: ListOfEvents,
                                               event_id: str) -> DictOfTargetsForRolesAtEvent:
    raw_dict = compose_raw_dict_of_targets_for_roles_at_event(
        list_of_roles=list_of_roles,
        list_of_targets_with_role_ids=list_of_targets_with_role_ids,

    )

    return DictOfTargetsForRolesAtEvent(
        raw_dict=raw_dict,
        list_of_targets_with_role_ids=list_of_targets_with_role_ids,
        event = list_of_events.object_with_id(event_id)
    )

def compose_raw_dict_of_targets_for_roles_at_event(list_of_targets_with_role_ids: ListOfTargetForRoleWithIdAtEvent,
                                               list_of_roles: ListOfRolesWithSkillIds) -> Dict[RolesWithSkillIds, int]:

    raw_dict = dict([(
        list_of_roles.object_with_id(target_with_role_id.role_id),
                                     target_with_role_id.target)
    for target_with_role_id in list_of_targets_with_role_ids])

    return raw_dict