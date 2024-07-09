import os
from typing import List

import yaml
from app.data_access.configuration.configuration import DATAPATH

home_directory = os.path.expanduser("~")

master_data_path = os.path.join(home_directory, DATAPATH)

ROLES_AND_SKILLS_YAML_FILE = 'roles_and_skills.yaml'
roles_and_skills_filename = os.path.join(master_data_path, ROLES_AND_SKILLS_YAML_FILE)
VOLUNTEERS_SKILL_FOR_PB2 = "PB2"
SI_SKILL = "SI"

core_skills = [SI_SKILL, VOLUNTEERS_SKILL_FOR_PB2]

SKILLS_KEY = "skills"
class SkillsAndRolesConfiguration(List[str]):
    def as_dict(self):
        return

    @classmethod
    def from_dict_and_core_skills(cls, skills_dict):
        list_of_skills = skills_dict[SKILLS_KEY]
        list_with_core = list_of_skills+core_skills

        return cls(list(set(list_with_core)))

def get_skills_from_configuration_file() -> SkillsAndRolesConfiguration:
    with open(roles_and_skills_filename) as file_to_parse:
        skills_dict = yaml.load(file_to_parse, Loader=yaml.FullLoader)

    return SkillsAndRolesConfiguration.from_dict_and_core_skills(skills_dict)



def save_skills_to_configuration_file(skills_dict: dict):
    with open(roles_and_skills_filename, 'w') as file_to_parse:
        yaml.dump(skills_dict, file_to_parse)


with open(roles_and_skills_filename) as file_to_parse:
    configuration = yaml.load(file_to_parse, Loader=yaml.FullLoader)

VOLUNTEER_SKILLS = configuration['volunteer_skills']
VOLUNTEER_TEAMS = configuration["volunteer_teams"]
VOLUNTEER_SKILL_DICT = configuration["role_and_skills_required"]
VOLUNTEERS_REQUIRING_BOATS = configuration["volunteers_requiring_boats"]
VOLUNTEERS_REQUIRING_GROUP = configuration["volunteers_requiring_group"]
INSTRUCTOR_TEAM_NAME = configuration["instructor_team"]
INSTRUCTOR_TEAM = VOLUNTEER_TEAMS[INSTRUCTOR_TEAM_NAME]
SI_ROLE = configuration["senior_instructor"]
RIVER_SAFETY = "River safety"
LAKE_SAFETY = "Lake safety"


def DEPRECATE_get_volunteer_roles():
    ## FIXME REPLACE WITH CONFIGURABLE FILE in backend
    volunteer_roles = []
    for team in VOLUNTEER_TEAMS.values():
        for role in team:
            if (
                role not in volunteer_roles
            ):  ## avoids duplication eg deputy skipper while preserving order
                volunteer_roles.append(role)

    return volunteer_roles


VOLUNTEER_ROLES = DEPRECATE_get_volunteer_roles()
