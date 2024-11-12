from dataclasses import dataclass

from app.objects.exceptions import arg_not_passed, MultipleMatches, MissingData
from app.objects.generic_objects import GenericSkipperManObjectWithIds
from app.objects.generic_list_of_objects import GenericListOfObjectsWithIds


@dataclass
class Skill(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed
    protected: bool = False

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name


class ListOfSkills(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return Skill

    def add(self, new_skill_name: str):
        try:
            assert new_skill_name not in self.list_of_names()
        except:
            raise Exception(
                "Can't add duplicate skill name %s already exists" % new_skill_name
            )
        skill = Skill(new_skill_name, protected=False)
        skill.id = self.next_id()

        self.append(skill)

    def modify(self, existing_skill: Skill, new_skill: Skill):
        existing_skill_idx = self.index(existing_skill)
        new_skill.id = existing_skill.id
        self[existing_skill_idx] = new_skill

    def matches_name(self, skill_name: str):
        matching_list = [object for object in self if object.name == skill_name]
        if len(matching_list) == 0:
            raise MissingData
        elif len(matching_list) > 1:
            raise MultipleMatches
        else:
            return matching_list[0]

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_names()
        assert len(list_of_names) == len(set(list_of_names))

    def list_of_names(self):
        return [skill.name for skill in self]


def skill_from_str(skill_str: str) -> Skill:
    return Skill(skill_str)


VOLUNTEERS_SKILL_FOR_PB2_NAME = "PB2"
SI_SKILL_NAME = "SI"
SI_skill = Skill(SI_SKILL_NAME)
PB2_skill = Skill(VOLUNTEERS_SKILL_FOR_PB2_NAME)
