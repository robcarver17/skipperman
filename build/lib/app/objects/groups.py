## table of groups
## we have groups for each event? No need, too complicated
## So can hard code all groups in configuration
import pandas as pd

from app.data_access.configuration.configuration import (
    LAKE_TRAINING_GROUPS,
    RIVER_TRAINING_GROUPS,
    MG_GROUPS,
    ALL_GROUPS,
    UNALLOCATED_GROUP,
)
from app.objects.cadets import Cadet, ListOfCadets
from dataclasses import dataclass

from app.objects.field_list import CADET_NAME, GROUP_STR_NAME, ID_NAME
from app.objects.generic import GenericSkipperManObjectWithIds, GenericListOfObjectsWithIds

LAKE_TRAINING = "Lake training"
RIVER_TRAINING = "River training"
MG = "MG"


class Group:
    def __init__(self, group_name: str):
        try:
            assert group_name in ALL_GROUPS
        except:
            raise Exception(
                "Group %s is not a valid group name - correct or add to configuration"
                % group_name
            )

        self._group_name = group_name

    def __repr__(self):
        return self.group_name

    def __lt__(self, other):
        return self.group_name<other.group_name


    @classmethod
    def create_unallocated(cls):
        return cls(UNALLOCATED_GROUP)

    @property
    def is_unallocated(self):
        return self.group_name == UNALLOCATED_GROUP

    @property
    def group_name(self):
        return self._group_name

    def type_of_group(self):
        if self.create_unallocated:
            return UNALLOCATED_GROUP
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
        return self.group_name in LAKE_TRAINING_GROUPS

    def is_river_training(self) -> bool:
        return self.group_name in RIVER_TRAINING_GROUPS

    def is_race_group(self) -> bool:
        return self.group_name in MG_GROUPS


@dataclass(frozen=True)
class CadetIdWithGroup(GenericListOfObjectsWithIds):
    cadet_id: str
    group: Group

    def as_dict(self) -> dict:
        return_dict = {}
        return_dict[ID_NAME] = self.cadet_id
        return_dict[GROUP_STR_NAME] = str(self.group)

        return return_dict

    @classmethod
    def from_dict(cls, dict_with_str: dict):
        group_name = dict_with_str.pop(GROUP_STR_NAME)
        group = Group(group_name)
        cadet_id = dict_with_str.pop(ID_NAME)

        return cls(cadet_id=cadet_id, group=group)


NOT_ALLOCATED = Group.create_unallocated()


class ListOfCadetIdsWithGroups(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetIdWithGroup

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
        self.append(CadetIdWithGroup(cadet_id=cadet_id, group=NOT_ALLOCATED))

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

    def cadets_in_list_not_allocated_to_group(
        self, list_of_cadets: ListOfCadets
    ) -> ListOfCadets:
        my_ids = self.list_of_ids
        list_ids = list_of_cadets.list_of_ids

        ids_in_list_not_given_group = list(set(list_ids).difference(set(my_ids)))

        return list_of_cadets.subset_from_list_of_ids(
            full_list=list_of_cadets, list_of_ids=ids_in_list_not_given_group
        )

    def group_for_cadet(self, cadet: Cadet):
        return self.group_for_cadet_id(cadet.id)

    def group_for_cadet_id(self, cadet_id: str) -> Group:
        try:
            item = self.item_with_cadet_id(cadet_id)
        except:
            return NOT_ALLOCATED

        return item.group

    def cadet_is_allocated_to_group(self, cadet: Cadet) -> bool:
        try:
            self.item_with_cadet_id(cadet_id=cadet.id)
            return True
        except:
            return False

    def item_with_cadet_id(self, cadet_id: str) -> CadetIdWithGroup:
        list_of_cadet_ids = self.list_of_ids
        try:
            idx = list_of_cadet_ids.index(cadet_id)
        except ValueError:
            raise Exception("Cadet %s not found" % cadet_id)

        return self[idx]

    @property
    def list_of_ids(self) -> list:
        return [item.cadet_id for item in self]

    def sort_by_group(self):
        new_list = sorted(self, key=lambda x: x.group, reverse=False)
        return ListOfCadetIdsWithGroups(new_list)

@dataclass
class CadetWithGroup(GenericSkipperManObjectWithIds):
    ## For display purposes, can't store
    cadet: Cadet
    group: Group

    def as_str_dict(self, display_full_names: bool = True) -> dict:
        ## for display purposes
        if display_full_names:
            cadet_name = self.cadet.name
        else:
            cadet_name = self.cadet.initial_and_surname

        return {CADET_NAME: cadet_name, GROUP_STR_NAME: str(self.group)}


class ListOfCadetsWithGroup(GenericListOfObjectsWithIds):
    def _object_class_contained(self):
        return CadetWithGroup

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
