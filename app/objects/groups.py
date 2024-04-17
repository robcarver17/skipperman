
from typing import List
import pandas as pd
from app.objects.utils import in_x_not_in_y

from app.data_access.configuration.configuration import (
    LAKE_TRAINING_GROUP_NAMES,
    RIVER_TRAINING_GROUP_NAMES,
    MG_GROUP_NAMES,
    ALL_GROUPS_NAMES,
    UNALLOCATED_GROUP_NAME,
)
from app.objects.cadets import Cadet, ListOfCadets
from dataclasses import dataclass
from app.objects.constants import missing_data
from app.objects.generic import GenericSkipperManObjectWithIds, GenericListOfObjectsWithIds, GenericSkipperManObject, GenericListOfObjects

LAKE_TRAINING = "Lake training"
RIVER_TRAINING = "River training"
MG = "MG"


class Group:

    def __init__(self, group_name: str):
        try:
            assert group_name in ALL_GROUPS_NAMES
        except:
            raise Exception(
                "Group %s is not a valid group name - correct or add to configuration"
                % group_name
            )

        self._group_name = group_name

    def __eq__(self, other):
        if type(other) is str:
            return self.group_name==other

        return self.group_name == other.group_name

    def __hash__(self):
        return hash(self.group_name)

    def __str__(self):
        return self.group_name

    def __repr__(self):
        return self.group_name

    def __lt__(self, other: 'Group'):
        return index_group(self)<index_group(other)

    def as_str_replace_unallocated_with_empty(self)-> str:
        if self.is_unallocated:
            return ""
        else:
            return self.group_name

    @classmethod
    def create_unallocated(cls):
        return cls(UNALLOCATED_GROUP_NAME)

    @property
    def is_unallocated(self):
        return self.group_name == UNALLOCATED_GROUP_NAME

    @property
    def group_name(self):
        return self._group_name

    def type_of_group(self):
        if self.is_unallocated:
            return UNALLOCATED_GROUP_NAME
        elif self.is_lake_training():
            return LAKE_TRAINING
        elif self.is_river_training():
            return RIVER_TRAINING
        elif self.is_race_group():
            return MG
        else:
            raise Exception(
                "Group %s doesn't seem to be one of the recognised types - check or change configuration"
                % self.group_name
            )

    def is_lake_training(self) -> bool:
        return self.group_name in LAKE_TRAINING_GROUP_NAMES

    def is_river_training(self) -> bool:
        return self.group_name in RIVER_TRAINING_GROUP_NAMES

    def is_race_group(self) -> bool:
        return self.group_name in MG_GROUP_NAMES

GROUP_UNALLOCATED = Group.create_unallocated()
GROUP_UNALLOCATED_TEXT = "Unallocated"

def index_group(group: Group):
    all_groups = ALL_GROUPS_NAMES + [GROUP_UNALLOCATED_TEXT]
    return all_groups.index(group)


@dataclass
class CadetIdWithGroup(GenericSkipperManObjectWithIds):
    cadet_id: str
    group: Group



class ListOfCadetIdsWithGroups(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetIdWithGroup

    def list_of_cadet_ids_in_group(self, group: Group) -> List[str]:
        ids = [item.cadet_id for item in self if item.group == group]

        return ids

    def total_in_each_group_as_dict(self) -> dict:
        list_of_groups = self.unique_list_of_groups()
        total_by_group = dict([(str(group),0) for group in list_of_groups])
        for cadet_id_with_group in self:
            total_by_group[str(cadet_id_with_group.group)]+=1

        return total_by_group

    def unique_list_of_groups(self) -> list:
        list_of_groups = self.groups
        return list(set(list_of_groups))

    @property
    def groups(self) -> list:
        list_of_groups = [cadet_id_with_group.group for cadet_id_with_group in self]
        return list_of_groups

    def add_list_of_unallocated_cadets(self, list_of_unallocated_cadets: ListOfCadets):
        [self.add_unallocated_cadet(cadet) for cadet in list_of_unallocated_cadets]

    def add_unallocated_cadet(self, cadet: Cadet):
        cadet_id = cadet.id
        self.append(CadetIdWithGroup(cadet_id=cadet_id, group=GROUP_UNALLOCATED))

    def remove_cadet_with_id_from_allocation(self, cadet_id: str):
        idx = self.index_of_item_with_cadet_id(cadet_id)
        __ = self.pop(idx)

    def update_group_for_cadet(self, cadet: Cadet, chosen_group: Group):
        if self.cadet_is_allocated_to_group(cadet):
            self._update_group_for_existing_cadet(
                cadet=cadet, chosen_group=chosen_group
            )
        else:
            self._update_group_for_new_cadet(cadet=cadet, chosen_group=chosen_group)

    def _update_group_for_existing_cadet(self, cadet: Cadet, chosen_group: Group):
        cadet_id = cadet.id
        list_of_ids = self.list_of_ids
        idx = list_of_ids.index(cadet_id)
        if self[idx].group == chosen_group:
            pass
        if chosen_group.is_unallocated:
            ## don't store group as unallocated instead remove entirely
            self.pop(idx)
        else:
            self[idx] = CadetIdWithGroup(cadet_id=cadet_id, group=chosen_group)

    def _update_group_for_new_cadet(self, cadet: Cadet, chosen_group: Group):
        if chosen_group.is_unallocated:
            ## don't store group as unallocated
            return
        else:
            cadet_id = cadet.id
            self.append(CadetIdWithGroup(cadet_id=cadet_id, group=chosen_group))

    def cadet_ids_in_passed_list_not_allocated_to_any_group(self,
                                                            list_of_cadet_ids: List[str]):
        my_ids = self.list_of_ids
        ids_in_list_not_given_group = in_x_not_in_y(x=list_of_cadet_ids, y=my_ids)

        return ids_in_list_not_given_group

    def cadets_in_passed_list_not_allocated_to_any_group(
        self, list_of_cadets: ListOfCadets
    ) -> ListOfCadets:
        my_ids = self.list_of_ids
        list_ids = list_of_cadets.list_of_ids

        ids_in_list_not_given_group = in_x_not_in_y(x=list_ids, y=my_ids)

        return list_of_cadets.subset_from_list_of_ids(
            full_list=list_of_cadets, list_of_ids=ids_in_list_not_given_group
        )

    def group_for_cadet(self, cadet: Cadet):
        return self.group_for_cadet_id(cadet.id)

    def group_for_cadet_id(self, cadet_id: str) -> Group:
        try:
            item = self.item_with_cadet_id(cadet_id)
        except:
            return GROUP_UNALLOCATED

        return item.group

    def cadet_is_allocated_to_group(self, cadet: Cadet) -> bool:
        try:
            self.item_with_cadet_id(cadet_id=cadet.id)
            return True
        except:
            return False

    def item_with_cadet_id(self, cadet_id: str) -> CadetIdWithGroup:
        idx = self.index_of_item_with_cadet_id(cadet_id)
        return self[idx]

    def index_of_item_with_cadet_id(self, cadet_id: str) -> int:
        list_of_cadet_ids = self.list_of_ids
        try:
            idx = list_of_cadet_ids.index(cadet_id)
        except ValueError:
            raise Exception("Cadet %s not found" % cadet_id)

        return idx


    @property
    def list_of_ids(self) -> list:
        return [item.cadet_id for item in self]

    def sort_by_group(self):
        new_list = sorted(self, key=lambda x: x.group, reverse=False)
        return ListOfCadetIdsWithGroups(new_list)


## Following used for reporting, must match field names below
CADET_NAME = "cadet" #### FIXME USED IN REPORTING DELETE
GROUP_STR_NAME = "group"#### FIXME USED IN REPORTING DELETE

@dataclass
class CadetWithGroup(GenericSkipperManObject):
    ## For display purposes, can't store
    cadet: Cadet
    group: Group

    @property
    def cadet_name_initials_only(self) -> str:
        return self.cadet.initial_and_surname

    @property
    def cadet_full_name(self) -> str:
        return self.cadet.name

    def as_str_dict(self, display_full_names: bool = True) -> dict:
        if display_full_names:
            cadet_name = self.cadet_full_name
        else:
            cadet_name = self.cadet_name_initials_only

        group_name = str(self.group)

        return {
            CADET_NAME: cadet_name,
             GROUP_STR_NAME: group_name
        }

class ListOfCadetsWithGroup(GenericListOfObjects):
    def _object_class_contained(self):
        return CadetWithGroup

    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets([cadet_with_group.cadet for cadet_with_group in self])

    @classmethod
    def from_list_of_cadets_and_list_of_allocations(
        cls, list_of_cadets: ListOfCadets, list_of_allocations: ListOfCadetIdsWithGroups
    ):
        list_of_cadets_with_group = [
            CadetWithGroup(
                cadet=list_of_cadets.has_id(allocation.cadet_id), group=allocation.group
            )
            for allocation in list_of_allocations
        ]

        return cls(list_of_cadets_with_group)

    def to_df_of_str(self, display_full_names: bool = True) -> pd.DataFrame:
        list_of_dicts = [
            item.as_str_dict(display_full_names=display_full_names) for item in self
        ]

        return pd.DataFrame(list_of_dicts)


