import os
from dataclasses import dataclass
from typing import List, Dict

import yaml
from app.data_access.configuration.configuration import DATAPATH

home_directory = os.path.expanduser("~")
master_data_path = os.path.join(home_directory, DATAPATH)

ROLES_AND_SKILLS_YAML_FILE = 'roles_and_skills.yaml'
roles_and_skills_filename = os.path.join(master_data_path, ROLES_AND_SKILLS_YAML_FILE)


### Core skills
VOLUNTEERS_SKILL_FOR_PB2 = "PB2"
SI_SKILL = "SI"
core_skills = [SI_SKILL, VOLUNTEERS_SKILL_FOR_PB2]

SKILLS_KEY = "skills"

@dataclass
class SkillsAndRolesConfiguration(List[str]):
    volunteer_skills_from_config: List[str]
    dict_of_volunteer_teams: Dict[str,List[str]]
    role_and_skills_required: Dict[str, List[str]]
    volunteers_requiring_boats: List[str]
    volunteers_requiring_group: List[str]
    instructor_team_name: str
    SI_role: str

    @property
    def volunteer_skills(self):
        return list(set(self.core_skills()+self.volunteer_skills_from_config))

    @property
    def volunteer_roles(self):
        volunteer_roles = []
        for team in self.dict_of_volunteer_teams.values():
            for role in team:
                if (
                        role not in volunteer_roles
                ):  ## avoids duplication eg deputy skipper while preserving order
                    volunteer_roles.append(role)

        return volunteer_roles

    def instructor_team_members(self):
        return self.dict_of_volunteer_teams[self.instructor_team_name]

    def save_to_filename(self, filename:str):
        with open(filename, 'w') as file_to_parse:
            yaml.dump(self.self_as_dict(), file_to_parse)

    @classmethod
    def get_from_filename(cls, filename:str):
        with open(roles_and_skills_filename) as file_to_parse:
            skills_and_roles_configuration = yaml.load(file_to_parse, Loader=yaml.FullLoader)

        return cls(
            volunteer_skills_from_config=skills_and_roles_configuration['volunteer_skills'],
            dict_of_volunteer_teams=skills_and_roles_configuration["dict_of_volunteer_teams"],
            role_and_skills_required=skills_and_roles_configuration["role_and_skills_required"],
            volunteers_requiring_boats=skills_and_roles_configuration["volunteers_requiring_boats"],
            volunteers_requiring_group=skills_and_roles_configuration["volunteers_requiring_group"],
            instructor_team_name=skills_and_roles_configuration["instructor_team_name"],
            SI_role= skills_and_roles_configuration["SI_role"]

        )

    def self_as_dict(self):
        raise NotImplemented

    def core_skills(self):
        return [self.pb2_skill, self.si_skill]

    @property
    def pb2_skill(self):
        VOLUNTEERS_SKILL_FOR_PB2 = "PB2" ## DO NOT CHANGE
        return VOLUNTEERS_SKILL_FOR_PB2

    @property
    def si_skill(self):
        SI_SKILL = "SI"
        return SI_SKILL

skills_and_roles_configuration = SkillsAndRolesConfiguration.get_from_filename(roles_and_skills_filename)


def save_skills_and_rolls_to_configuration_file(skills_and_rolls:SkillsAndRolesConfiguration):
    skills_and_rolls.save_to_filename(roles_and_skills_filename)

all_volunteer_skill_names = skills_and_roles_configuration.volunteer_skills
dict_of_volunteer_teams = skills_and_roles_configuration.dict_of_volunteer_teams
dict_of_roles_and_skills_required = skills_and_roles_configuration.role_and_skills_required
volunteers_requiring_boats = skills_and_roles_configuration.volunteers_requiring_boats
volunteers_requiring_group = skills_and_roles_configuration.volunteers_requiring_group
instructor_team = skills_and_roles_configuration.instructor_team_members()
si_role = skills_and_roles_configuration.SI_role
all_volunteer_role_names = skills_and_roles_configuration.volunteer_roles


def get_volunteer_roles():
    ## FIXME REPLACE WITH CONFIGURABLE FILE
    volunteer_roles = []
    for team in dict_of_volunteer_teams.values():
        for role in team:
            if (
                role not in volunteer_roles
            ):  ## avoids duplication eg deputy skipper while preserving order
                volunteer_roles.append(role)

    return volunteer_roles


volunteer_roles = get_volunteer_roles()
