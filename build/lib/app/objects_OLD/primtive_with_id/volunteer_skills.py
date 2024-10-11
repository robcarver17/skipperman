from dataclasses import dataclass
from typing import Dict, List

from app.data_access.configuration.skills_and_roles import all_volunteer_skill_names
from app.objects.volunteer_skills import VOLUNTEERS_SKILL_FOR_PB2, SI_SKILL
from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject

from enum import Enum


Skill = Enum("Skill", all_volunteer_skill_names)

def skill_from_str(skill_str: str) -> Skill:
    return Skill[skill_str]

PB2_skill = Skill[VOLUNTEERS_SKILL_FOR_PB2]
SI_skill = Skill[SI_SKILL]

all_skills = [Skill[skill_str] for skill_str in all_volunteer_skill_names]

@dataclass
class VolunteerSkill(GenericSkipperManObject):
    volunteer_id: str
    skill: Skill

    @property
    def volunteer_can_drive_safety_boat(self) -> bool:
        return self.skill == PB2_skill

    @property
    def volunteer_is_senior_instructor(self) -> bool:
        return self.skill == SI_skill

class SkillsDict(Dict[Skill, bool]):
    def __repr__(self):
        skills_as_list = [str(skill) for skill, has_skill in self.items() if has_skill]
        skills_as_str = ", ".join(skills_as_list)

        return skills_as_str

    def has_skill_name(self, skill_name:str):
        return self.get(skill_from_str(skill_name), False)

    def empty(self):
        return not any([held for held in self.values()])

    def skill_names_as_list_of_str(self):
        return [skill.name for skill in self.keys()]

    def skills_held_as_str(self):
        return  ", ".join([skill.name for skill, skill_held in self.items() if skill_held])

    def skills_not_held_as_str(self):
        return  ", ".join([skill.name for skill, skill_held in self.items() if not skill_held])

    def as_dict_of_str_and_bool(self)-> Dict[str, bool]:
        return dict([(skill.name, skill_held) for skill, skill_held in self.items()])

    @classmethod
    def from_dict_of_str_and_bool(cls, skills_dict: Dict[str, bool]):
        return cls([(skill_from_str(skill_name), skill_held) for skill_name, skill_held in skills_dict.items()])

    def pad_with_missing_skills(self):
        for skill in all_skills:
            if skill in self.keys():
                continue
            self[skill] = False

    @property
    def can_drive_safety_boat(self) -> bool:
        return self.get(PB2_skill, False)


default_skills_dict = SkillsDict([(skill, False) for skill in all_skills])


class ListOfVolunteerSkills(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return VolunteerSkill

    def add_volunteer_driving_qualification(self, volunteer_id: str):
        self.add_skill_for_id(PB2_skill, volunteer_id=volunteer_id)

    def remove_volunteer_driving_qualification(self, volunteer_id: str):
        self.delete_skill_for_id(
            volunteer_id=volunteer_id, skill=PB2_skill
        )

    def volunteer_id_can_drive_safety_boat(self, volunteer_id: str) -> bool:
        return volunteer_id in self.list_of_volunteer_ids_who_can_drive_safety_boat()

    def volunteer_is_senior_instructor(self, volunteer_id: str) -> bool:
        return volunteer_id in self.list_of_volunteer_ids_who_are_senior_instructors()

    def list_of_volunteer_ids_who_can_drive_safety_boat(self) -> List[str]:
        return list(
            set([item.volunteer_id for item in self if item.volunteer_can_drive_safety_boat])
        )

    def list_of_volunteer_ids_who_are_senior_instructors(self) -> List[str]:
        return list(
            set([item.volunteer_id for item in self if item.volunteer_is_senior_instructor])
        )

    def dict_of_skills_for_volunteer_id(self, volunteer_id: str) -> SkillsDict:
        skills_held = self.skills_for_volunteer_id(volunteer_id)
        dict_of_skills = dict(
            [(skill, skill in skills_held) for skill in all_skills]
        )

        return SkillsDict(dict_of_skills)

    def skills_for_volunteer_id(self, volunteer_id: str) -> List[Skill]:
        skills = [
            element.skill for element in self if element.volunteer_id == volunteer_id
        ]

        return skills

    def replace_skills_for_volunteer_with_new_skills_dict(
        self, volunteer_id: str, dict_of_skills: SkillsDict
    ):
        ## skills that are missing from dict won't be modified - should be fine
        for skill, skill_held in dict_of_skills.items():
            currently_held_skill = self.skill_held_for_id(skill, volunteer_id)
            if skill_held and not currently_held_skill:
                self.add_skill_for_id(skill=skill, volunteer_id=volunteer_id)

            if not skill_held and currently_held_skill:
                self.delete_skill_for_id(skill=skill, volunteer_id=volunteer_id)

    def skill_held_for_id(self, skill: Skill, volunteer_id: str) -> bool:
        present = [
            True
            for element in self
            if element.skill == skill and element.volunteer_id == volunteer_id
        ]
        return len(present) > 0

    def add_skill_for_id(self, skill: Skill, volunteer_id: str):
        if self.skill_held_for_id(skill = skill, volunteer_id=volunteer_id):
            return
        self.append(VolunteerSkill(skill=skill, volunteer_id=volunteer_id))

    def delete_skill_for_id(self, skill: Skill, volunteer_id: str):
        element_with_skill_in_list = [
            element
            for element in self
            if element.skill == skill and element.volunteer_id == volunteer_id
        ]
        if len(element_with_skill_in_list) == 0:
            return
        element_with_skill = element_with_skill_in_list[0]
        self.remove(element_with_skill)
