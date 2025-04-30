from dataclasses import dataclass
from enum import Enum
from typing import List

from app.objects.utilities.exceptions import arg_not_passed
from app.objects.utilities.generic_objects import GenericSkipperManObjectWithIds
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    get_idx_of_unique_object_with_attr_in_list,
)

UNALLOCATED_GROUP_STR = "No group set"
UNALLOCATED_GROUP_ID = "0"  ## dont change

GroupLocation = Enum(
    "GroupLocation",
    ["Lake_training", "River_training", "MG", "Unallocated", "Undetermined"],
)

lake_training_group_location = GroupLocation.Lake_training
river_training_group_location = GroupLocation.River_training
mg_training_group_location = GroupLocation.MG
unallocated_group_location = GroupLocation.Unallocated
undetermined_group_location = GroupLocation.Undetermined

all_locations_for_input = [
    lake_training_group_location,
    river_training_group_location,
    mg_training_group_location,
]

all_allocations = [
    lake_training_group_location,
    river_training_group_location,
    mg_training_group_location,
    unallocated_group_location,
    undetermined_group_location,
]


def sorted_locations(passed_list_of_locations: List[GroupLocation]):
    return [
        location for location in all_allocations if location in passed_list_of_locations
    ]


@dataclass
class Group(GenericSkipperManObjectWithIds):
    name: str
    location: GroupLocation
    protected: bool
    hidden: bool
    id: str = arg_not_passed

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.location == other.location
            and self.hidden == other.hidden
        )

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @classmethod
    def create_unallocated(cls):
        return cls(
            UNALLOCATED_GROUP_STR,
            location=unallocated_group_location,
            protected=True,
            id=UNALLOCATED_GROUP_ID,  ## DO NOT CHANGE
            hidden=False,
        )

    @classmethod
    def create_missing(cls):
        return cls(
            "Not at event",
            location=unallocated_group_location,
            protected=True,
            id="-9asmissing",  ## DO NOT CHANGE
            hidden=False,
        )

    @property
    def is_unallocated(self):
        return self == unallocated_group


unallocated_group = Group.create_unallocated()
unallocated_group_id = unallocated_group.id
missing_group_display_only = Group.create_missing()

from app.objects.utilities.generic_list_of_objects import (
    get_unique_object_with_attr_in_list,
)


class ListOfGroups(GenericListOfObjectsWithIds):
    def sort_to_match_other_group_list_order(self, other_groups: "ListOfGroups"):
        return ListOfGroups([group for group in other_groups if group in self])

    @property
    def _object_class_contained(self):
        return Group

    def add(self, group_name: str):
        try:
            assert group_name not in self.list_of_names()
        except:
            raise Exception(
                "Can't add duplicate sailing group %s already exists" % group_name
            )
        group = Group(
            group_name,
            protected=False,
            location=lake_training_group_location,
            hidden=False,
        )
        group.id = self.next_id()

        self.append(group)

    def group_with_id(self, group_id: str, default=arg_not_passed):
        if group_id == unallocated_group_id:
            return unallocated_group

        return self.object_with_id(group_id, default=default)

    def replace(self, existing_group: Group, new_group: Group):
        existing_idx = self.idx_given_name(group_name=existing_group.name)
        new_group.id = existing_group.id
        self[existing_idx] = new_group

    def idx_given_name(self, group_name: str, default=arg_not_passed):
        return get_idx_of_unique_object_with_attr_in_list(
            some_list=self, attr_name="name", attr_value=group_name, default=default
        )

    def matches_name(self, group_name: str, default=arg_not_passed):
        if group_name == unallocated_group.name:
            return unallocated_group

        return get_unique_object_with_attr_in_list(
            some_list=self, attr_name="name", attr_value=group_name, default=default
        )

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_names()
        assert len(list_of_names) == len(set(list_of_names))

    def has_lake_group(self):
        return self.contains_specific_location(lake_training_group_location)

    def contains_specific_location(self, location: GroupLocation):
        return any([group.location == location for group in self])

    def add_unallocated(self):
        if unallocated_group in self:
            pass
        else:
            self.append(unallocated_group)

    def remove_unallocated(self):
        if unallocated_group in self:
            self.remove(unallocated_group)
