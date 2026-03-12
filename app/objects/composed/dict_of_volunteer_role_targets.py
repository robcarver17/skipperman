from typing import Dict

from app.objects.composed.volunteer_roles import (
    RoleWithSkills
)

class DictOfTargetsForRolesAtEvent(Dict[RoleWithSkills, int]):

    def get_target_for_role(self, role: RoleWithSkills) -> int:
        return self.get(role, 0)
