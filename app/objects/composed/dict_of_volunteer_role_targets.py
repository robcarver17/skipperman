from typing import Dict

from app.objects.composed.volunteer_roles import RoleWithSkills, ListOfRolesWithSkills
from app.objects.events import Event, ListOfEvents
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

    def update_new_volunteer_target(self, role: RoleWithSkills, target: int):
        self[role] = target
        self.list_of_targets_with_role_ids.set_target_for_role(
            role_id=role.id, target=target
        )

    def get_target_for_role(self, role: RoleWithSkills) -> int:
        return self.get(role, 0)

    @property
    def event(self) -> Event:
        return self._event

    @property
    def list_of_targets_with_role_ids(self) -> ListOfTargetForRoleWithIdAtEvent:
        return self._list_of_targets_with_role_ids


def compose_list_of_targets_for_roles_at_event(
    list_of_targets_with_role_ids: ListOfTargetForRoleWithIdAtEvent,
    list_of_roles_and_skills: ListOfRolesWithSkills,
    list_of_events: ListOfEvents,
    event_id: str,
) -> DictOfTargetsForRolesAtEvent:
    raw_dict = compose_raw_dict_of_targets_for_roles_at_event(
        list_of_roles_and_skills=list_of_roles_and_skills,
        list_of_targets_with_role_ids=list_of_targets_with_role_ids,
    )

    return DictOfTargetsForRolesAtEvent(
        raw_dict=raw_dict,
        list_of_targets_with_role_ids=list_of_targets_with_role_ids,
        event=list_of_events.event_with_id(event_id),
    )


def compose_raw_dict_of_targets_for_roles_at_event(
    list_of_targets_with_role_ids: ListOfTargetForRoleWithIdAtEvent,
    list_of_roles_and_skills: ListOfRolesWithSkills,
) -> Dict[RoleWithSkills, int]:
    raw_dict = dict(
        [
            (
                list_of_roles_and_skills.role_with_id(target_with_role_id.role_id),
                target_with_role_id.target,
            )
            for target_with_role_id in list_of_targets_with_role_ids
        ]
    )

    return raw_dict
