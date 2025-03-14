from dataclasses import dataclass
from typing import List, Tuple, Union

from app.objects.exceptions import arg_not_passed, MissingData, missing_data
from app.objects.volunteer_skills import ListOfSkills
from app.objects.roles_and_teams import RolesWithSkillIds, ListOfRolesWithSkillIds
from app.objects.composed.volunteers_with_skills import SkillsDict


SI_ROLE_NAME = "SI"
NO_ROLE_SET = "No role allocated"


@dataclass
class RoleWithSkills:
    name: str
    skills_dict: SkillsDict
    hidden: bool
    associate_sailing_group: bool
    protected: bool
    id: str = arg_not_passed

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.skills_dict == other.skills_dict
            and self.hidden == other.hidden
            and self.associate_sailing_group == other.associate_sailing_group
            and self.protected == other.protected
        )

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def is_no_role_set(self):
        return self == no_role_set

    def as_role_with_skill_ids(self) -> RolesWithSkillIds:
        return RolesWithSkillIds(
            name=self.name,
            id=self.id,
            skill_ids_required=self.list_of_skill_ids(),
            associate_sailing_group=self.associate_sailing_group,
            protected=self.protected,
            hidden=self.hidden,
        )

    def list_of_skill_ids(self) -> List[str]:
        return self.list_of_skills().list_of_ids

    def list_of_skills(self) -> ListOfSkills:
        return self.skills_dict.as_list_of_skills()

    def is_si(self):
        return self.name == SI_ROLE_NAME


no_role_set = RoleWithSkills(
    name=NO_ROLE_SET,
    skills_dict=SkillsDict(),
    protected=True,
    hidden=False,
    associate_sailing_group=True,
)


def from_list_of_skill_ids_to_padded_dict_of_skills(
    list_of_skill_ids: List[str], list_of_skills: ListOfSkills
) -> SkillsDict:
    skills_held = list_of_skills.subset_from_list_of_ids_retaining_order(
        list_of_ids=list_of_skill_ids
    )

    skills_dict = SkillsDict.from_list_of_skills(skills_held)
    skills_dict.pad_with_missing_skills(list_of_skills)

    return skills_dict


from app.objects.generic_list_of_objects import (
    get_unique_object_with_attr_in_list,
    get_idx_of_unique_object_with_attr_in_list,
)


class ListOfRolesWithSkills(List[RoleWithSkills]):
    def __init__(
        self,
        list_of_roles_with_skill_ids: ListOfRolesWithSkillIds = arg_not_passed,
        list_of_skills: ListOfSkills = arg_not_passed,
        list_of_roles_with_skills: List[RoleWithSkills] = arg_not_passed,
    ):
        (
            raw_list_of_roles,
            list_of_roles_with_skill_ids,
        ) = get_raw_list_of_roles_and_list_of_roles_with_skill_ids(
            list_of_roles_with_skill_ids=list_of_roles_with_skill_ids,
            list_of_skills=list_of_skills,
            list_of_roles_with_skills=list_of_roles_with_skills,
        )
        super().__init__(raw_list_of_roles)
        self._list_of_roles_with_skill_ids = list_of_roles_with_skill_ids

    @classmethod
    def from_list_of_roles_with_skills(
        cls, list_of_roles_with_skills: List[RoleWithSkills]
    ):
        return cls(list_of_roles_with_skills=list_of_roles_with_skills)

    @classmethod
    def from_raw_list_of_roles_with_skill_ids_and_list_of_skills(
        cls,
        list_of_roles_with_skill_ids: ListOfRolesWithSkillIds = arg_not_passed,
        list_of_skills: ListOfSkills = arg_not_passed,
    ):
        return cls(
            list_of_roles_with_skill_ids=list_of_roles_with_skill_ids,
            list_of_skills=list_of_skills,
        )


    def modify(self, existing_role: RoleWithSkills, new_role: RoleWithSkills):
        index = self.index_of_matching_existing_named_role(existing_role)
        existing_role_in_self = self[index]
        new_role.id = existing_role_in_self.id

        self[index] = new_role
        new_role_with_skill_ids = new_role.as_role_with_skill_ids()
        self.list_of_roles_with_skill_ids.replace_at_index(
            index=index, new_role_with_skill_ids=new_role_with_skill_ids
        )

    def add_no_role_set(self):
        if self.contains_no_role_set():
            pass

        self.append(no_role_set)

    def contains_no_role_set(self):
        exists = self.role_with_name(NO_ROLE_SET, default=missing_data)
        return exists is not missing_data

    def add(self, new_role_name: str):
        try:
            assert new_role_name not in self.list_of_names()
        except:
            raise Exception("Role %s already exists" % new_role_name)

        new_role = RoleWithSkills(
            name=new_role_name,
            protected=False,
            hidden=False,
            skills_dict=SkillsDict({}),
            associate_sailing_group=False,
        )
        new_id = self.list_of_roles_with_skill_ids.add_returning_id(
            new_role.as_role_with_skill_ids()
        )
        new_role.id = new_id
        self.append(new_role)

    def index_of_matching_existing_named_role(
        self, existing_role: RoleWithSkills, default=arg_not_passed
    ) -> int:
        return self.index_of_matching_existing_role_name(existing_role.name)

    def index_of_matching_existing_role_name(
        self, existing_role_name: str, default=arg_not_passed
    ) -> int:
        return get_idx_of_unique_object_with_attr_in_list(
            some_list=self,
            attr_name="name",
            attr_value=existing_role_name,
            default=default,
        )

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_names()
        assert len(list_of_names) == len(set(list_of_names))

    def list_of_names(self):
        return [role.name for role in self]

    def sort_to_match_other_role_list_order(
        self, other_list: Union["ListOfRolesWithSkills", ListOfRolesWithSkillIds]
    ) -> "ListOfRolesWithSkills":
        new_list = []
        for role_with_skill in other_list:
            if role_with_skill.name in self.list_of_names():
                new_list.append(self.role_with_name(role_with_skill.name))

        return ListOfRolesWithSkills.from_list_of_roles_with_skills(new_list)

    def subset_for_ids(self, subset_list_of_ids: List[str]) -> List[RoleWithSkills]:
        list_of_ids = self.list_of_ids()
        list_of_idx = [list_of_ids.index(id) for id in subset_list_of_ids]

        return [self[idx] for idx in list_of_idx]

    def list_of_ids(self) -> List[str]:
        return [role.id for role in self]

    def role_with_id(self, id: str, default=arg_not_passed) -> RoleWithSkills:
        return get_unique_object_with_attr_in_list(
            some_list=self, attr_name="id", attr_value=id, default=default
        )

    def role_with_name(self, role_name, default=arg_not_passed):
        if role_name == no_role_set.name:
            return no_role_set

        return get_unique_object_with_attr_in_list(
            some_list=self, attr_name="name", attr_value=role_name, default=default
        )

    @property
    def list_of_roles_with_skill_ids(self) -> ListOfRolesWithSkillIds:
        return self._list_of_roles_with_skill_ids


def get_raw_list_of_roles_and_list_of_roles_with_skill_ids(
    list_of_roles_with_skill_ids: ListOfRolesWithSkillIds = arg_not_passed,
    list_of_skills: ListOfSkills = arg_not_passed,
    list_of_roles_with_skills: List[RoleWithSkills] = arg_not_passed,
) -> Tuple[List[RoleWithSkills], ListOfRolesWithSkillIds]:
    if (
        (list_of_skills is arg_not_passed)
        and (list_of_roles_with_skill_ids is arg_not_passed)
        and (list_of_roles_with_skills is not arg_not_passed)
    ):
        return get_raw_list_of_roles_and_list_of_roles_with_skill_ids_from_list_with_skills(
            list_of_roles_with_skills=list_of_roles_with_skills
        )
    if (
        (list_of_skills is not arg_not_passed)
        and (list_of_roles_with_skill_ids is not arg_not_passed)
        and (list_of_roles_with_skills is arg_not_passed)
    ):
        return get_raw_list_of_roles_and_list_of_roles_with_skill_ids_from_list_with_skill_ids(
            list_of_roles_with_skill_ids=list_of_roles_with_skill_ids,
            list_of_skills=list_of_skills,
        )

    raise Exception(
        "Must pass list_of_skills AND list_of_roles_with_skill_ids OR list_of_roles_with_skills - use class methods not bare init"
    )


def get_raw_list_of_roles_and_list_of_roles_with_skill_ids_from_list_with_skill_ids(
    list_of_roles_with_skill_ids: ListOfRolesWithSkillIds, list_of_skills: ListOfSkills
) -> Tuple[List[RoleWithSkills], ListOfRolesWithSkillIds]:
    raw_list_of_roles = get_raw_list_of_roles_with_skills(
        list_of_roles_with_skill_ids=list_of_roles_with_skill_ids,
        list_of_skills=list_of_skills,
    )

    return raw_list_of_roles, list_of_roles_with_skill_ids


def get_raw_list_of_roles_and_list_of_roles_with_skill_ids_from_list_with_skills(
    list_of_roles_with_skills: List[RoleWithSkills],
) -> Tuple[List[RoleWithSkills], ListOfRolesWithSkillIds]:
    list_of_roles_with_skill_ids = [
        role_with_skill_id.as_role_with_skill_ids()
        for role_with_skill_id in list_of_roles_with_skills
    ]

    return list_of_roles_with_skills, ListOfRolesWithSkillIds(
        list_of_roles_with_skill_ids
    )


def compose_list_of_roles_with_skills(
    list_of_roles_with_skill_ids: ListOfRolesWithSkillIds, list_of_skills: ListOfSkills
) -> ListOfRolesWithSkills:
    return (
        ListOfRolesWithSkills.from_raw_list_of_roles_with_skill_ids_and_list_of_skills(
            list_of_roles_with_skill_ids=list_of_roles_with_skill_ids,
            list_of_skills=list_of_skills,
        )
    )


def get_raw_list_of_roles_with_skills(
    list_of_roles_with_skill_ids: ListOfRolesWithSkillIds, list_of_skills: ListOfSkills
) -> List[RoleWithSkills]:
    new_list = []
    for role_with_skill_id in list_of_roles_with_skill_ids:
        new_list.append(
            RoleWithSkills(
                name=role_with_skill_id.name,
                skills_dict=from_list_of_skill_ids_to_padded_dict_of_skills(
                    list_of_skills=list_of_skills,
                    list_of_skill_ids=role_with_skill_id.skill_ids_required,
                ),
                hidden=role_with_skill_id.hidden,
                protected=role_with_skill_id.protected,
                associate_sailing_group=role_with_skill_id.associate_sailing_group,
                id=role_with_skill_id.id,
            )
        )

    return new_list


def empty_if_qualified_for_role_else_warnings(
    role: RoleWithSkills, dict_of_skills: SkillsDict
) -> str:

    skills_required = role.skills_dict
    missing_skills = []
    for skill, skill_needed in skills_required.items():
        if skill_needed:
            has_skill = dict_of_skills.has_skill(skill)
            if not has_skill:
                missing_skills.append(skill.name)

    return ", ".join(missing_skills)
