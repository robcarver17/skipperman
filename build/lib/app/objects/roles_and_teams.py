from dataclasses import dataclass
from enum import Enum
from typing import List
from app.objects.exceptions import arg_not_passed, MissingData, MultipleMatches

from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    GenericListOfObjects,
)
from app.objects.generic_objects import (
    GenericSkipperManObjectWithIds,
    GenericSkipperManObject,
    from_str_to_bool,
    from_bool_to_str,
)
from app.objects.groups import LAKE_TRAINING, RIVER_TRAINING

NO_WARNING = "No warning"
RoleLocation = Enum("RoleLocation", [LAKE_TRAINING, RIVER_TRAINING, NO_WARNING])

NO_SKILLS_REQUIRED = "-1"

role_location_lake = RoleLocation[LAKE_TRAINING]
role_location_river = RoleLocation[RIVER_TRAINING]
role_location_no_warning = RoleLocation[NO_WARNING]

all_role_locations = [role_location_no_warning, role_location_lake, role_location_river]


@dataclass
class RolesWithSkillIds(GenericSkipperManObjectWithIds):
    name: str
    skill_ids_required: List[str]
    hidden: bool
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


class ListOfRolesWithSkillIds(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return RolesWithSkillIds

    def sort_to_match_other_role_list_order(self, other_list: 'ListOfRolesWithSkillIds'):
        return ListOfRolesWithSkillIds([
            role for role in other_list if role in self
        ])

    def replace_at_index(self, index: int, new_role_with_skill_ids: RolesWithSkillIds):
        existing_role_as_skill_id = self[index]
        new_role_with_skill_ids.id = existing_role_as_skill_id.id
        self[index] = new_role_with_skill_ids

    def add_returning_id(self, new_role_with_skill_ids: RolesWithSkillIds):
        new_role_with_skill_ids.id = self.next_id()
        self.append(new_role_with_skill_ids)

        return new_role_with_skill_ids.id

    def matches_name(self, role_name: str):
        matching_list = [object for object in self if object.name == role_name]
        if len(matching_list) == 0:
            raise MissingData
        elif len(matching_list) > 1:
            raise MultipleMatches
        else:
            return matching_list[0]


INSTRUCTOR_TEAM = "Instructors"


@dataclass
class Team(GenericSkipperManObjectWithIds):
    name: str
    location_for_cadet_warning: RoleLocation
    protected: bool
    id: str = arg_not_passed

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


no_team = Team(
    "No team", location_for_cadet_warning=role_location_no_warning, protected=True
)

instructor_team = Team(
    INSTRUCTOR_TEAM, location_for_cadet_warning=role_location_no_warning, protected=True
)


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
            name=new_team_name,
            protected=False,
            location_for_cadet_warning=role_location_river,
        )
        team.id = self.next_id()

        self.append(team)

    def replace(self, existing_team: Team, new_team: Team):
        try:
            existing_team_idx = self.index(existing_team)
        except:
            return
        new_team.id = existing_team.id
        self[existing_team_idx] = new_team

    def matching_team_name(self, team_name: str) -> Team:
        list_of_matches = [
            matching_team for matching_team in self if team_name == matching_team.name
        ]
        if len(list_of_matches) == 0:
            raise MissingData
        elif len(list_of_matches) > 1:
            raise MultipleMatches

        return list_of_matches[0]

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_names()
        assert len(list_of_names) == len(set(list_of_names))

    def list_of_names(self):
        return [team.name for team in self]


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

    def ordered_roles_for_team_id(self, team_id: str):
        raw_list = [
            team_and_role for team_and_role in self if team_and_role.team_id == team_id
        ]
        raw_list.sort(key=lambda x: x.order_idx)
        ordered_list = ListOfTeamsAndRolesWithIds(raw_list)

        return ordered_list.list_of_role_ids()

    def list_of_role_ids(self):
        return [team_and_role.role_id for team_and_role in self]
