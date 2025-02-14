from dataclasses import dataclass
from enum import Enum
from typing import List
from app.objects.exceptions import arg_not_passed, MissingData, MultipleMatches

from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    GenericListOfObjects, get_unique_object_with_attr_in_list, get_idx_of_unique_object_with_attr_in_list,
)
from app.objects.generic_objects import (
    GenericSkipperManObjectWithIds,
    GenericSkipperManObject,
    from_str_to_bool,
    from_bool_to_str,
)

NO_SKILLS_REQUIRED = "-1"
NO_ROLE_ALLOCATED = "No role allocated"
NO_ROLE_ALLOCATED_ID = str(-9999)

RoleLocation = Enum(
    "RoleLocation", ['Lake_training', 'No_warning', 'River_training']
)


role_location_lake = RoleLocation.Lake_training
role_location_river = RoleLocation.River_training
role_location_no_warning = RoleLocation.No_warning

all_role_locations = [role_location_no_warning, role_location_lake, role_location_river]



@dataclass
class RolesWithSkillIds(GenericSkipperManObjectWithIds):
    name: str
    skill_ids_required: List[str]
    hidden: bool = False
    id: str = arg_not_passed
    associate_sailing_group: bool = False
    protected: bool = False

    @classmethod
    def from_dict_of_str(cls, dict_with_str: dict):
        skill_ids_required = str(dict_with_str["skill_ids_required"])
        if skill_ids_required == NO_SKILLS_REQUIRED:
            skill_ids_required = []
        else:
            skill_ids_required = skill_ids_required.split(",")
        return cls(
            name=dict_with_str["name"],
            skill_ids_required=skill_ids_required,
            id=str(dict_with_str["id"]),
            associate_sailing_group=from_str_to_bool(
                dict_with_str["associate_sailing_group"]
            ),
            protected=from_str_to_bool(dict_with_str["protected"]),
            hidden=from_str_to_bool(dict_with_str["hidden"]),
        )

    def as_str_dict(self) -> dict:
        skill_ids_required = self.skill_ids_required
        if len(skill_ids_required) == 0:
            skill_ids_required = NO_SKILLS_REQUIRED
        else:
            skill_ids_required = ",".join(skill_ids_required)

        return dict(
            name=self.name,
            skill_ids_required=skill_ids_required,
            id=self.id,
            associate_sailing_group=from_bool_to_str(self.associate_sailing_group),
            protected=from_bool_to_str(self.protected),
            hidden=from_bool_to_str(self.hidden),
        )

    @classmethod
    def create_empty(cls):
        return cls(
            name=NO_ROLE_ALLOCATED,
            id=NO_ROLE_ALLOCATED_ID,
            skill_ids_required=[NO_SKILLS_REQUIRED],
            associate_sailing_group=False,
            hidden=False,
            protected=True
        )

no_role_allocated = RolesWithSkillIds.create_empty()
no_role_allocated_id = no_role_allocated.id

class ListOfRolesWithSkillIds(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return RolesWithSkillIds

    def replace_at_index(self, index: int, new_role_with_skill_ids: RolesWithSkillIds):
        existing_role_as_skill_id = self[index]
        new_role_with_skill_ids.id = existing_role_as_skill_id.id
        self[index] = new_role_with_skill_ids

    def add_returning_id(self, new_role_with_skill_ids: RolesWithSkillIds):
        new_role_with_skill_ids.id = self.next_id()
        self.append(new_role_with_skill_ids)

        return new_role_with_skill_ids.id

    def matches_name(self, role_name: str, default = arg_not_passed):
        if role_name == no_role_allocated.name:
            return no_role_allocated

        return get_unique_object_with_attr_in_list(
            some_list=self,
            attr_name='name',
            attr_value=role_name,
            default=default
        )


INSTRUCTOR_TEAM = "Instructors" ## DO NOT CHANGE PROTECTED IN DATA
NO_TEAM = "No team"
NO_TEAM_ID = str(-999)

@dataclass
class Team(GenericSkipperManObjectWithIds):
    name: str
    location_for_cadet_warning: RoleLocation = role_location_river
    protected: bool = False
    id: str = arg_not_passed

    def __eq__(self, other):
        return self.name == other.name and self.location_for_cadet_warning == other.location_for_cadet_warning

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def is_instructor_team(self):
        return self.name == INSTRUCTOR_TEAM

    @classmethod
    def create_empty(cls):
        return cls(
            NO_TEAM,
            location_for_cadet_warning=role_location_no_warning,
            protected=True,
            id=NO_TEAM_ID
        )


no_team = Team.create_empty()



class ListOfTeams(GenericListOfObjectsWithIds):
    def sort_to_match_other_team_list_order(self, other_team_list: "ListOfTeams"):
        return ListOfTeams([team for team in other_team_list if team in self])

    @property
    def _object_class_contained(self):
        return Team

    def add(self, new_team_name: str):
        try:
            assert new_team_name not in self.list_of_names()
        except:
            raise Exception(
                "Can't add duplicate team name %s already exists" % new_team_name
            )
        team = Team(
            name=new_team_name
        )
        team.id = self.next_id()

        self.append(team)

    def replace(self, existing_team: Team, new_team: Team):
        try:
            existing_team_idx = self.index_of_existing_team(existing_team)
        except:
            return
        new_team.id = existing_team.id
        self[existing_team_idx] = new_team

    def index_of_existing_team(self, existing_team: Team, default=arg_not_passed):
        return get_idx_of_unique_object_with_attr_in_list(
            some_list=self,
            attr_name='name',
            attr_value=existing_team.name,
            default=default
        )

    def instructor_team_from_list(self):
        return self.matching_team_name(INSTRUCTOR_TEAM)

    def team_with_id(self, team_id: str, default =arg_not_passed):
        if team_id == no_team.id:
            return no_team

        return self.object_with_id(team_id)

    def matching_team_name(self, team_name: str, default = arg_not_passed) -> Team:
        if team_name == no_team.name:
            return no_team

        return get_unique_object_with_attr_in_list(
            some_list=self,
            attr_name='name',
            attr_value=team_name,
            default=default
        )

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_names()
        assert len(list_of_names) == len(set(list_of_names))



@dataclass
class TeamsAndRolesWithIds(GenericSkipperManObject):
    team_id: str
    role_id: str
    order_idx: int


class ListOfTeamsAndRolesWithIds(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return TeamsAndRolesWithIds

    def remove_roles_for_team_id(self, team_id: str):
        new_list = [
            role_and_team for role_and_team in self if role_and_team.team_id != team_id
        ]
        return ListOfTeamsAndRolesWithIds(new_list)

    def ordered_role_ids_for_team_id(self, team_id: str):
        raw_list = [
            team_and_role for team_and_role in self if team_and_role.team_id == team_id
        ]
        raw_list.sort(key=lambda x: x.order_idx)
        ordered_list = ListOfTeamsAndRolesWithIds(raw_list)

        return ordered_list.list_of_role_ids()

    def list_of_role_ids(self):
        return [team_and_role.role_id for team_and_role in self]

