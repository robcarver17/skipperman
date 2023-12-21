from copy import copy
from dataclasses import dataclass

from app.data_access.configuration.configuration import VOLUNTEER_ROLES, LAKE, RIVER, OTHER, LAKE_VOLUNTEER_ROLES, RIVER_VOLUNTEER_ROLES
from app.objects.generic import GenericSkipperManObject, get_class_instance_from_str_dict, GenericListOfObjectsNoIds
from app.objects.groups import Group

LIST_KEY = 'list_of_associated_cadet_id'

## FIXME - Boats done seperately


@dataclass
class VolunteerAtEvent(GenericSkipperManObject):
    volunteer_id: str
    role: str
    list_of_associated_cadet_id: list
    group: str = ""

    @property
    def is_no_volunteer(self) -> bool:
        return self.volunteer_id==NO_VOLUNTEER_ID

    @classmethod
    def from_dict(cls, dict_with_str):
        list_of_cadet_ids_as_str = dict_with_str[LIST_KEY]
        if len(list_of_cadet_ids_as_str)==0:
            list_of_cadet_ids=[]
        else:
            list_of_cadet_ids= list_of_cadet_ids_as_str.split(",")

        new_dict = copy(dict_with_str)
        new_dict[LIST_KEY] = list_of_cadet_ids

        return get_class_instance_from_str_dict(cls, dict_with_str=new_dict)

    def as_str_dict(self) -> dict:
        as_dict = self.as_dict()

        ## all strings except the list
        list_of_associated_cadets = as_dict[LIST_KEY]
        list_of_associated_cadets_as_str = ",".join(list_of_associated_cadets)

        as_dict[LIST_KEY] = list_of_associated_cadets_as_str

        return as_dict

    @property
    def location(self):
        if self.role in LAKE_VOLUNTEER_ROLES:
            return LAKE
        elif self.role in RIVER_VOLUNTEER_ROLES:
            return RIVER
        elif not self.group == "":
            group = Group(self.group)
            if group.is_lake_training():
                return LAKE
            elif group.is_race_group() or group.is_river_training():
                return RIVER

        return OTHER

NO_VOLUNTEER_ID = '-99'
def no_volunteer_for_cadet(cadet_id):
    return VolunteerAtEvent(volunteer_id=NO_VOLUNTEER_ID, role="None",  list_of_associated_cadet_id=[cadet_id])

class ListOfVolunteersAtEvent(GenericListOfObjectsNoIds):

    @property
    def _object_class_contained(self):
        return VolunteerAtEvent

    def any_volunteers_associated_with_cadet_id_including_no_volunteer(self, cadet_id: str)-> bool:
        list_of_volunteers = self.list_of_volunteer_ids_associated_with_cadet_id_including_no_volunteer(cadet_id)
        return len(list_of_volunteers)>0
    
    def list_of_volunteer_ids_associated_with_cadet_id(self, cadet_id: str):
        list_of_volunteers = self.list_of_volunteer_ids_associated_with_cadet_id_including_no_volunteer(cadet_id)
        return list_of_volunteers.list_excluding_no_volunteers()

    def list_of_volunteer_ids_associated_with_cadet_id_including_no_volunteer(self, cadet_id: str):
        return ListOfVolunteersAtEvent([volunteer_at_event for volunteer_at_event in self if cadet_id in volunteer_at_event.list_of_associated_cadet_id])


    def list_excluding_no_volunteers(self):
        return ListOfVolunteersAtEvent([volunteer_at_event for volunteer_at_event in self if not volunteer_at_event.is_no_volunteer])

