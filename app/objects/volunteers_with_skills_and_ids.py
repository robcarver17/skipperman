from dataclasses import dataclass

from app.objects.exceptions import MissingData, MultipleMatches
from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject


@dataclass
class VolunteerSkillWithIds(GenericSkipperManObject):
    volunteer_id: str
    skill_id:str

class ListOfVolunteerSkillsWithIds(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return VolunteerSkillWithIds

    def add(self, volunteer_id: str, skill_id: str):
        try:
            self.object_matching_ids(volunteer_id=volunteer_id, skill_id=skill_id)
            return
        except MissingData:
            self.append(VolunteerSkillWithIds(volunteer_id=volunteer_id, skill_id=skill_id))

    def delete(self, volunteer_id: str, skill_id: str):
        try:
            matching_object = self.object_matching_ids(volunteer_id=volunteer_id, skill_id=skill_id)
            self.remove(matching_object)
        except MissingData:
            return


    def object_matching_ids(self, volunteer_id: str, skill_id: str):
        matching = [object for object in self if object.volunteer_id == volunteer_id and object.skill_id == skill_id]
        if len(matching)==0:
            raise MissingData
        elif len(matching)>1:
            raise MultipleMatches

        return matching[0]


