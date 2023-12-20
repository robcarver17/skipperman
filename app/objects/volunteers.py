from typing import Dict
from dataclasses import dataclass

from app.data_access.configuration.configuration import (
    SIMILARITY_LEVEL_TO_WARN_NAME,
VOLUNTEER_SKILLS
)
from app.objects.generic import GenericSkipperManObjectWithIds, GenericListOfObjectsWithIds, GenericListOfObjectsNoIds, GenericSkipperManObject, get_class_instance_from_str_dict
from app.objects.utils import transform_date_into_str, similar
from app.objects.constants import arg_not_passed, DAYS_IN_YEAR
from app.objects.generic import data_object_as_dict

@dataclass
class Volunteer(GenericSkipperManObjectWithIds):
    first_name: str
    surname: str
    id: str = arg_not_passed
    def __repr__(self):
        return "%s %s" % (
            self.first_name.title(),
            self.surname.title(),
        )

    def __eq__(self, other):
        return (
            (self.first_name == other.first_name)
            and (self.surname == other.surname)
        )

    def __hash__(self):
        return hash(
            self.first_name + "_" + self.surname
        )


    @property
    def name(self):
        return self.first_name.title() + " " + self.surname.title()


    def similarity_name(self, other_volunteer: "Volunteer") -> float:
        return similar(self.name, other_volunteer.name)



class ListOfVolunteers(GenericListOfObjectsWithIds):

    @property
    def _object_class_contained(self):
        return Volunteer

    def similar_volunteers(
        self,
        volunteer: Volunteer,
        name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME,
    ) -> "ListOfVolunteers":
        similar_names = [
            other_volunteer
            for other_volunteer in self
            if other_volunteer.similarity_name(volunteer) > name_threshold
        ]

        return ListOfVolunteers(similar_names)

    def sort_by_surname(self):
        return ListOfVolunteers(sorted(self, key=lambda x: x.surname))

    def sort_by_firstname(self):
        return ListOfVolunteers(sorted(self, key=lambda x: x.first_name))



default_volunteer = Volunteer(
    first_name=" ",
    surname=" "
)


@dataclass
class CadetVolunteerAssociation(GenericSkipperManObject):
    cadet_id: str
    volunteer_id: str

class ListOfCadetVolunteerAssociations(GenericListOfObjectsNoIds):

    @property
    def _object_class_contained(self):
        return CadetVolunteerAssociation

    def list_of_connections_for_volunteer(self, volunteer_id: str):
        return [element.cadet_id for element in self if element.volunteer_id == volunteer_id]

    def delete(self, cadet_id: str, volunteer_id: str):
        matching_elements_list = [element for element in self if element.volunteer_id==volunteer_id and element.cadet_id==cadet_id]
        if len(matching_elements_list)==0:
            return
        matching_element = matching_elements_list[0]
        self.remove(matching_element)

    def add(self, cadet_id: str, volunteer_id: str):
        if self.connection_exists(cadet_id=cadet_id, volunteer_id=volunteer_id):
            return
        self.append(CadetVolunteerAssociation(cadet_id=cadet_id, volunteer_id=volunteer_id))

    def connection_exists(self, cadet_id: str, volunteer_id: str):
        exists = [True for element in self if element.volunteer_id==volunteer_id and element.cadet_id == cadet_id]
        return len(exists)>0

@dataclass
class VolunteerSkill(GenericSkipperManObject):
    volunteer_id: str
    skill: str

class ListOfVolunteerSkills(GenericListOfObjectsNoIds):

    @property
    def _object_class_contained(self):
        return VolunteerSkill

    def dict_of_skills_for_volunteer_id(self, volunteer_id: str) -> Dict[str, bool]:
        skills_held = self.skills_for_volunteer_id(volunteer_id)
        dict_of_skills = dict([
            (skill, skill in skills_held) for skill in VOLUNTEER_SKILLS
        ])

        return dict_of_skills

    def skills_for_volunteer_id(self, volunteer_id: str):
        skills = [element.skill for element in self if element.volunteer_id==volunteer_id]

        return skills

    def replace_skills_for_volunteer_with_new_skills_dict(self, volunteer_id: str, dict_of_skills: Dict[str, bool]):
        ## skills that are missing from dict won't be modified - should be fine
        for skill, skill_held in dict_of_skills.items():
            currently_held_skill = self.skill_held_for_id(skill, volunteer_id)
            if skill_held and not currently_held_skill:
                self.add_skill_for_id(skill_name=skill, volunteer_id=volunteer_id)

            if not skill_held and currently_held_skill:
                self.delete_skill_for_id(skill_name=skill, volunteer_id=volunteer_id)

    def skill_held_for_id(self, skill_name: str, volunteer_id: str) -> bool:
        present = [True for element in self if element.skill==skill_name and element.volunteer_id==volunteer_id]
        return len(present)>0

    def add_skill_for_id(self, skill_name: str, volunteer_id: str):
        if self.skill_held_for_id(skill_name=skill_name, volunteer_id=volunteer_id):
            return
        self.append(VolunteerSkill(skill=skill_name, volunteer_id=volunteer_id))

    def delete_skill_for_id(self, skill_name: str, volunteer_id: str):
        element_with_skill_in_list = [element for element in self if element.skill==skill_name and element.volunteer_id==volunteer_id]
        if len(element_with_skill_in_list)==0:
            return
        element_with_skill = element_with_skill_in_list[0]
        self.remove(element_with_skill)

LIST_KEY = 'list_of_associated_cadet_id'

@dataclass
class VolunteerAtEvent(GenericSkipperManObject):
    volunteer_id: str
    location: str
    list_of_associated_cadet_id: list = arg_not_passed
    group: str = ""

    @property
    def associated_cadet_id(self) -> list:
        if self.list_of_associated_cadet_id is arg_not_passed:
            return []
        return self.list_of_associated_cadet_id

    @classmethod
    def from_dict(cls, dict_with_str):
        dict_with_str[LIST_KEY] = dict_with_str[LIST_KEY].split(",")
        class_dict = get_class_instance_from_str_dict(cls, dict_with_str=dict_with_str,)

    def as_str_dict(self) -> dict:
        as_dict = self.as_dict()

        ## all strings except the list
        list_of_associated_cadets = as_dict[LIST_KEY]
        list_of_associated_cadets = ",".join(list_of_associated_cadets)

        as_dict[LIST_KEY] = list_of_associated_cadets

    def as_dict(self) -> dict:
        as_dict = data_object_as_dict(self)
        as_dict[LIST_KEY] = self.associated_cadet_id ## instead of arg_not_passed

        return as_dict

## FIXME - Boats done seperately

class ListOfVolunteersAtEvent(GenericListOfObjectsNoIds):

    @property
    def _object_class_contained(self):
        return VolunteerAtEvent
