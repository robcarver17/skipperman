from typing import Dict, List


from app.objects.utilities.transform_data import from_bool_to_str, from_str_to_bool
from app.objects.volunteer_skills import (
    Skill,
    SI_SKILL_NAME,
    VOLUNTEERS_SKILL_FOR_PB2_NAME,
    ListOfSkills,
)
from app.objects.volunteers import Volunteer


class SkillsDict(Dict[Skill, bool]):
    def __repr__(self):
        skills_as_list = [str(skill) for skill, has_skill in self.items() if has_skill]
        skills_as_str = ", ".join(skills_as_list)

        return skills_as_str

    def __eq__(self, other):
        return (
            self.list_of_held_skill_names_sorted
            == other.list_of_held_skill_names_sorted
        )

    def has_skill(self, skill: Skill):
        return self.get(skill, False)

    def empty(self):
        return not any([held for held in self.values()])

    def skill_names_as_list_of_str(self):
        return [skill.name for skill in self.keys()]

    def skills_held_as_str(self):
        return ", ".join(self.list_of_held_skill_names_sorted)

    @property
    def list_of_held_skill_names_sorted(self) -> List[str]:
        raw_list = self.list_of_held_skill_names()
        raw_list.sort()

        return raw_list

    def list_of_held_skills(self) -> ListOfSkills:
        raw_list = [skill for skill, skill_held in self.items() if skill_held]

        return ListOfSkills(raw_list)

    def list_of_held_skill_names(self) -> List[str]:
        raw_list = [skill.name for skill, skill_held in self.items() if skill_held]

        return raw_list

    def skills_not_held_as_str(self):
        return ", ".join(
            [skill.name for skill, skill_held in self.items() if not skill_held]
        )

    def as_dict_of_str_and_str(self) -> Dict[str, str]:
        return dict(
            [
                (skill.name, from_bool_to_str(skill_held))
                for skill, skill_held in self.items()
            ]
        )

    def as_dict_of_str_and_bool(self) -> Dict[str, bool]:
        return dict([(skill.name, skill_held) for skill, skill_held in self.items()])

    @classmethod
    def from_dict_of_str_and_bool(cls, skills_dict: Dict[str, bool]):
        return cls(
            [
                (Skill(skill_name), skill_held)
                for skill_name, skill_held in skills_dict.items()
            ]
        )

    @classmethod
    def from_dict_of_str_and_str(cls, skills_dict: Dict[str, str]):
        return cls(
            [
                (Skill(skill_name), from_str_to_bool(skill_held))
                for skill_name, skill_held in skills_dict.items()
            ]
        )

    @classmethod
    def from_list_of_skills(cls, list_of_skills: ListOfSkills):
        return cls([(skill, True) for skill in list_of_skills])

    def as_list_of_skillnames_or_empty(self):
        return ["" if not held else skill.name for skill, held in self.items()]

    def as_list_of_skills(self):
        return ListOfSkills([skill for skill, held in self.items() if held])

    def pad_with_missing_skills(self, all_skills: ListOfSkills):
        for skill in all_skills:
            if skill not in self.keys():
                self[skill] = False

    @property
    def can_drive_safety_boat(self) -> bool:
        has_skill = VOLUNTEERS_SKILL_FOR_PB2_NAME in self.list_of_held_skill_names()
        return has_skill

    @property
    def is_SI(self) -> bool:
        return SI_SKILL_NAME in self.list_of_held_skill_names()


class DictOfVolunteersWithSkills(Dict[Volunteer, SkillsDict]):
    def dict_of_skills_for_volunteer(self, volunteer: Volunteer) -> SkillsDict:
        return self.get(volunteer, SkillsDict())
