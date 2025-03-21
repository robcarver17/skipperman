from dataclasses import dataclass
from typing import Dict, List

from app.objects.generic_objects import GenericSkipperManObject
from app.objects.volunteer_skills import (
    Skill,
    SI_SKILL_NAME,
    VOLUNTEERS_SKILL_FOR_PB2_NAME,
    ListOfSkills,
)
from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.volunteers_with_skills_and_ids import (
    ListOfVolunteerSkillsWithIds,
    VolunteerSkillWithIds,
)


@dataclass
class VolunteerWithSkill(GenericSkipperManObject):
    volunteer: Volunteer
    skill: Skill

    @classmethod
    def from_volunteer_skills_with_id(
        cls,
        volunteer_skill_with_id: VolunteerSkillWithIds,
        list_of_volunteers: ListOfVolunteers,
        list_of_skills: ListOfSkills,
    ):
        return cls(
            volunteer=list_of_volunteers.volunteer_with_id(
                volunteer_skill_with_id.volunteer_id
            ),
            skill=list_of_skills.skill_with_id(volunteer_skill_with_id.skill_id),
        )


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

    def list_of_held_skill_names(self) -> List[str]:
        raw_list = [skill.name for skill, skill_held in self.items() if skill_held]

        return raw_list

    def skills_not_held_as_str(self):
        return ", ".join(
            [skill.name for skill, skill_held in self.items() if not skill_held]
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
    def from_list_of_skills(cls, list_of_skills: ListOfSkills):
        return cls([(skill, True) for skill in list_of_skills])

    def as_list_of_skillnames_or_empty(self):
        return ['' if not held else skill.name for skill, held in self.items()]

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


class ListOfVolunteersWithSkills(List[VolunteerWithSkill]):
    @classmethod
    def from_list_of_volunteer_skills_with_ids(
        cls,
        list_of_volunteer_skills_with_id: ListOfVolunteerSkillsWithIds,
        list_of_volunteers: ListOfVolunteers,
        list_of_skills: ListOfSkills,
    ):
        return cls(
            [
                VolunteerWithSkill.from_volunteer_skills_with_id(
                    volunteer_skill_with_id=volunteer_skill_with_id,
                    list_of_skills=list_of_skills,
                    list_of_volunteers=list_of_volunteers,
                )
                for volunteer_skill_with_id in list_of_volunteer_skills_with_id
            ]
        )

    def unique_list_of_volunteers(self) -> ListOfVolunteers:
        return ListOfVolunteers(
            list(
                set([volunteer_with_skills.volunteer for volunteer_with_skills in self])
            )
        )

    def skills_dict_for_volunteer(self, volunteer: Volunteer) -> SkillsDict:
        subset_for_volunteer = self.subset_for_volunteer(volunteer)
        list_of_skills_held_by_volunteer = ListOfSkills(
            [
                volunteer_with_skill.skill
                for volunteer_with_skill in subset_for_volunteer
            ]
        )
        return SkillsDict.from_list_of_skills(list_of_skills_held_by_volunteer)

    def subset_for_volunteer(
        self, volunteer: Volunteer
    ) -> "ListOfVolunteersWithSkills":
        return ListOfVolunteersWithSkills(
            [
                volunteer_with_skills
                for volunteer_with_skills in self
                if volunteer_with_skills.volunteer == volunteer
            ]
        )


class DictOfVolunteersWithSkills(Dict[Volunteer, SkillsDict]):
    def __init__(
        self,
        raw_dict: Dict[Volunteer, SkillsDict],
        list_of_skills: ListOfSkills,
        list_of_volunteers_with_skills_and_ids: ListOfVolunteerSkillsWithIds,
    ):
        super().__init__(raw_dict)

        self._list_of_volunteers_with_skills_and_ids = (
            list_of_volunteers_with_skills_and_ids
        )
        self._list_of_skills = list_of_skills

    def add_volunteer_driving_qualification(self, volunteer: Volunteer):
        PB2_skill = self.list_of_skills.PB2_skill
        self.add_skill_for_volunteer(volunteer=volunteer, skill=PB2_skill)

    def remove_volunteer_driving_qualification(self, volunteer: Volunteer):
        PB2_skill = self.list_of_skills.PB2_skill
        self.delete_skill_for_volunteer(volunteer=volunteer, skill=PB2_skill)

    def dict_of_skills_for_volunteer(self, volunteer: Volunteer) -> SkillsDict:
        return self.get(volunteer, SkillsDict())

    def replace_skills_for_volunteer_with_new_skills_dict(
        self, volunteer: Volunteer, dict_of_skills: SkillsDict
    ):
        existing_skills_dict = self.dict_of_skills_for_volunteer(volunteer)
        if len(existing_skills_dict) == 0:
            self[volunteer] = SkillsDict()

        self.replace_skills_for_existing_volunteer_with_new_skills_dict(
            volunteer=volunteer, dict_of_skills=dict_of_skills
        )

    def replace_skills_for_existing_volunteer_with_new_skills_dict(
        self, volunteer: Volunteer, dict_of_skills: SkillsDict
    ):
        ## skills that are missing from dict won't be modified - should be fine
        for skill, skill_held in dict_of_skills.items():
            currently_held_skill = self.skill_held_for_volunteer(skill, volunteer)
            if skill_held and not currently_held_skill:
                self.add_skill_for_volunteer(skill=skill, volunteer=volunteer)

            if not skill_held and currently_held_skill:
                self.delete_skill_for_volunteer(skill=skill, volunteer=volunteer)

    def skill_held_for_volunteer(self, skill: Skill, volunteer: Volunteer) -> bool:
        existing_skills_dict = self.dict_of_skills_for_volunteer(volunteer)
        return existing_skills_dict.get(skill, False)

    def add_skill_for_volunteer(self, skill: Skill, volunteer: Volunteer):
        if self.skill_held_for_volunteer(skill=skill, volunteer=volunteer):
            return
        existing_skills_dict = self.dict_of_skills_for_volunteer(volunteer)
        existing_skills_dict[skill] = True

        self.list_of_volunteers_with_skills_and_ids.add(
            volunteer_id=volunteer.id, skill_id=skill.id
        )

    def delete_skill_for_volunteer(self, skill: Skill, volunteer: Volunteer):
        if not self.skill_held_for_volunteer(skill=skill, volunteer=volunteer):
            return
        existing_skills_dict = self.dict_of_skills_for_volunteer(volunteer)
        existing_skills_dict[skill] = False

        self.list_of_volunteers_with_skills_and_ids.delete(
            volunteer_id=volunteer.id, skill_id=skill.id
        )

    @property
    def list_of_volunteers_with_skills_and_ids(self):
        return self._list_of_volunteers_with_skills_and_ids

    @property
    def list_of_skills(self):
        return self._list_of_skills


def compose_dict_of_volunteer_skills(
    list_of_volunteers: ListOfVolunteers,
    list_of_skills: ListOfSkills,
    list_of_volunteers_with_skills_and_ids: ListOfVolunteerSkillsWithIds,
) -> DictOfVolunteersWithSkills:
    raw_dict = compose_raw_dict_of_volunteer_skills(
        list_of_volunteers=list_of_volunteers,
        list_of_skills=list_of_skills,
        list_of_volunteers_with_skills_and_ids=list_of_volunteers_with_skills_and_ids,
    )

    return DictOfVolunteersWithSkills(
        raw_dict=raw_dict,
        list_of_volunteers_with_skills_and_ids=list_of_volunteers_with_skills_and_ids,
        list_of_skills=list_of_skills,
    )


def compose_raw_dict_of_volunteer_skills(
    list_of_volunteers: ListOfVolunteers,
    list_of_skills: ListOfSkills,
    list_of_volunteers_with_skills_and_ids: ListOfVolunteerSkillsWithIds,
) -> Dict[Volunteer, SkillsDict]:
    list_of_volunteers_with_skills = (
        ListOfVolunteersWithSkills.from_list_of_volunteer_skills_with_ids(
            list_of_volunteers=list_of_volunteers,
            list_of_skills=list_of_skills,
            list_of_volunteer_skills_with_id=list_of_volunteers_with_skills_and_ids,
        )
    )
    unique_list_of_volunteers = (
        list_of_volunteers_with_skills.unique_list_of_volunteers()
    )

    raw_dict = dict(
        [
            (
                volunteer,
                list_of_volunteers_with_skills.skills_dict_for_volunteer(volunteer),
            )
            for volunteer in unique_list_of_volunteers
        ]
    )

    return raw_dict
