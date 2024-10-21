from dataclasses import dataclass
from enum import Enum
from typing import List

from app.objects.exceptions import arg_not_passed, MissingData, MultipleMatches
from app.objects.generic_objects import GenericSkipperManObjectWithIds
from app.objects.generic_list_of_objects import GenericListOfObjectsWithIds

LAKE_TRAINING = "Lake training"
RIVER_TRAINING = "River training"
MG = "MG"
UNALLOCATED = "Unallocated"
UNDETERMINED = "Undetermined"

def sorted_locations_REPLACE_WITH_PROPER_SORT_NOT_STR(locations: List[str]):
    order = [LAKE_TRAINING, RIVER_TRAINING, MG]
    return [location for location in order if location in locations]


GroupLocation = Enum("GroupLocation", [LAKE_TRAINING, RIVER_TRAINING, MG, UNALLOCATED, UNDETERMINED])
lake_training_group_location = GroupLocation[LAKE_TRAINING]
river_training_group_location = GroupLocation[RIVER_TRAINING]
mg_training_group_location = GroupLocation[MG]
unallocated_group_location = GroupLocation[UNALLOCATED]
undetermined_group_location = GroupLocation[UNDETERMINED]

all_locations = [lake_training_group_location, river_training_group_location, mg_training_group_location]

@dataclass
class Group(GenericSkipperManObjectWithIds):
    name: str
    location: GroupLocation
    protected: bool
    hidden: bool
    id: str = arg_not_passed

    @classmethod
    def name_only(cls, name: str):
        return cls(name=name,
                   location=undetermined_group_location,
                   protected=True,
                   hidden=True)


    def __eq__(self, other):

        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __lt__(self, other: "Group"):
        raise Exception("Can't use sort for groups anymore - better solution required")

    def as_str_replace_unallocated_with_empty(self) -> str:
        if self.is_unallocated:
            return ""
        else:
            return self.name

    @classmethod
    def create_unallocated(cls):
        return cls(UNALLOCATED, location=unallocated_group_location, protected=True, id='0', hidden=False)

    @property
    def is_unallocated(self):
        return self == unallocated_group



unallocated_group = Group.create_unallocated()
GROUP_UNALLOCATED_TEXT_DONTUSE = "Unallocated"

class ListOfGroups(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return Group

    def add(self, group_name: str):
        try:
            assert group_name not in self.list_of_names()
        except:
            raise Exception("Can't add duplicate sailing group %s already exists" % group_name)
        group = Group(group_name, protected=False, location=lake_training_group_location, hidden=False)
        group.id = self.next_id()

        self.append(group)

    def replace(self,  existing_group: Group, new_group: Group):
        existing_idx = self.index(existing_group)
        new_group.id = existing_group.id
        self[existing_idx] = new_group

    def matches_name(self, group_name:str):
        matching_list = [object for object in self if object.name == group_name]
        if len(matching_list)==0:
            raise MissingData
        elif len(matching_list)>1:
            raise MultipleMatches
        else:
            return matching_list[0]

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_names()
        assert(len(list_of_names)==len(set(list_of_names)))

    def list_of_names(self):
        return [group.name for group in self]