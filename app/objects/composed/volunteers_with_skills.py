from dataclasses import dataclass
from typing import Dict, List

from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject
from app.objects.volunteer_skills import Skill, PB2_skill, SI_skill, skill_from_str, ListOfSkills
from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.volunteers_with_skills_and_ids import ListOfVolunteerSkillsWithIds


@dataclass
class VolunteerWithSkill(GenericSkipperManObject):
    volunteer: Volunteer
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

    def __eq__(self, other):
        return self.list_of_held_skill_names_sorted == other.list_of_held_skill_names_sorted

    def has_skill_name(self, skill_name:str):
        return self.get(skill_from_str(skill_name), False)

    def empty(self):
        return not any([held for held in self.values()])

    def skill_names_as_list_of_str(self):
        return [skill.name for skill in self.keys()]

    def skills_held_as_str(self):
        return  ", ".join([skill.name for skill, skill_held in self.items() if skill_held])

    @property
    def list_of_held_skill_names_sorted(self) -> List[str]:
        raw_list = [skill.name for skill, skill_held in self.items() if skill_held]
        raw_list.sort()

        return raw_list

    def skills_not_held_as_str(self):
        return  ", ".join([skill.name for skill, skill_held in self.items() if not skill_held])

    def as_dict_of_str_and_bool(self)-> Dict[str, bool]:
        return dict([(skill.name, skill_held) for skill, skill_held in self.items()])

    @classmethod
    def from_dict_of_str_and_bool(cls, skills_dict: Dict[str, bool]):
        return cls([(skill_from_str(skill_name), skill_held) for skill_name, skill_held in skills_dict.items()])

    @classmethod
    def from_list_of_skills(cls, list_of_skills: ListOfSkills):
        return cls(
            [
                (skill, True) for skill in list_of_skills
            ]
        )


    def as_list_of_skills(self):
        return ListOfSkills([skill for skill, held in self.items() if held])

    def pad_with_missing_skills(self, all_skills: ListOfSkills):
        for skill in all_skills:
            if skill not in self.keys():
                self[skill] = False

    @property
    def can_drive_safety_boat(self) -> bool:
        return self.get(PB2_skill, False)


class ListOfVolunteersWithSkills(List[VolunteerWithSkill]):
    def __init__(self, list_of_volunteers: ListOfVolunteers,
                 list_of_skills: ListOfSkills,
                 list_of_volunteers_with_skills_and_ids: ListOfVolunteerSkillsWithIds):

        super().__init__(compose_raw_list_of_volunteer_skills(
            list_of_volunteers=list_of_volunteers,
            list_of_skills=list_of_skills,
            list_of_volunteers_with_skills_and_ids=list_of_volunteers_with_skills_and_ids
        ))

        self._list_of_volunteers_with_skills_and_ids = list_of_volunteers_with_skills_and_ids

    @property
    def list_of_volunteers_with_skills_and_ids(self):
        return self._list_of_volunteers_with_skills_and_ids

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

    def dict_of_skills_for_volunteer(self, volunteer: Volunteer) -> SkillsDict:
        return self.dict_of_skills_for_volunteer_id(volunteer.id)

    def dict_of_skills_for_volunteer_id(self, volunteer_id: str) -> SkillsDict:
        skills_held = self.skills_for_volunteer_id(volunteer_id)
        dict_of_skills = dict(
            [(skill, True) for skill in skills_held]
        )

        return SkillsDict(dict_of_skills)

    def skills_for_volunteer_id(self, volunteer_id: str) -> List[Skill]:
        skills = [
            element.skill for element in self if element.volunteer.id == volunteer_id
        ]

        return skills

    def replace_skills_for_volunteer_with_new_skills_dict(
        self, volunteer: Volunteer, dict_of_skills: SkillsDict
    ):
        ## skills that are missing from dict won't be modified - should be fine
        for skill, skill_held in dict_of_skills.items():
            currently_held_skill = self.skill_held_for_id(skill, volunteer.id)
            if skill_held and not currently_held_skill:
                self.add_skill_for_id(skill=skill, volunteer=volunteer)

            if not skill_held and currently_held_skill:
                self.delete_skill_for_id(skill=skill, volunteer=volunteer)

    def skill_held_for_id(self, skill: Skill, volunteer_id: str) -> bool:
        present = [
            True
            for element in self
            if element.skill == skill and element.volunteer.id == volunteer_id
        ]
        return len(present) > 0

    def add_skill_for_id(self, skill: Skill, volunteer: Volunteer):
        if self.skill_held_for_id(skill = skill, volunteer_id=volunteer.id):
            return
        self.append(VolunteerWithSkill(skill=skill, volunteer=volunteer))
        self.list_of_volunteers_with_skills_and_ids.add(volunteer_id=volunteer.id, skill_id=skill.id)

    def delete_skill_for_id(self, skill: Skill, volunteer: Volunteer):
        element_with_skill_in_list = [
            element
            for element in self
            if element.skill.id == skill.id and element.volunteer.id == volunteer.id
        ]
        if len(element_with_skill_in_list) == 0:
            return
        element_with_skill = element_with_skill_in_list[0]
        self.remove(element_with_skill)
        self.list_of_volunteers_with_skills_and_ids.delete(volunteer_id=volunteer.id, skill_id=skill.id)

def compose_list_of_volunteer_skills(list_of_volunteers: ListOfVolunteers,
                 list_of_skills: ListOfSkills,
                 list_of_volunteers_with_skills_and_ids: ListOfVolunteerSkillsWithIds) -> ListOfVolunteersWithSkills:

    return ListOfVolunteersWithSkills(list_of_volunteers=list_of_volunteers,
                                      list_of_skills=list_of_skills,
                                      list_of_volunteers_with_skills_and_ids=list_of_volunteers_with_skills_and_ids)

def compose_raw_list_of_volunteer_skills(list_of_volunteers: ListOfVolunteers,
                 list_of_skills: ListOfSkills,
                 list_of_volunteers_with_skills_and_ids: ListOfVolunteerSkillsWithIds) -> List[VolunteerWithSkill]:

    raw_list = []
    for volunteer_with_skill_and_id in list_of_volunteers_with_skills_and_ids:
        volunteer_id = volunteer_with_skill_and_id.volunteer_id
        skill_id = volunteer_with_skill_and_id.skill_id

        raw_list.append(VolunteerWithSkill(skill=list_of_skills.object_with_id(skill_id), volunteer=list_of_volunteers.volunteer_with_id(volunteer_id)))

    return raw_list