## table of groups
## we have groups for each event? No need, too complicated
## So can hard code all groups in configuration

from data_access.configuration.configuration import (
    LAKE_TRAINING_GROUPS,
    RIVER_TRAINING_GROUPS,
    MG_GROUPS,
)
from objects.cadets import Cadet, ListOfCadets
from dataclasses import dataclass
from objects.generic import GenericSkipperManObject


ALL_GROUPS = LAKE_TRAINING_GROUPS + RIVER_TRAINING_GROUPS + MG_GROUPS

LAKE_TRAINING = "Lake training"
RIVER_TRAINING = "River training"
MG = "MG"

UNALLOCATED_GROUP = "Unallocated"

ALL_GROUPS_INCLUDING_UNALLOCATED = [UNALLOCATED_GROUP] + ALL_GROUPS

class Group:
    def __init__(self, group_name: str):

        try:
            assert group_name in ALL_GROUPS_INCLUDING_UNALLOCATED
        except:
            raise Exception(
                "Group %s is not a valid group name - correct or add to configuration"
                % group_name
            )

        self._group_name = group_name

    def __repr__(self):
        return self.group_name

    @classmethod
    def create_unallocated(cls):
        return cls(UNALLOCATED_GROUP)

    @property
    def is_unallocated(self):
        return self.group_name==UNALLOCATED_GROUP

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



GROUP_STR_NAME = "group"
ID_NAME = "cadet_id"

@dataclass(frozen=True)
class CadetWithGroup(GenericSkipperManObject):
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

NOT_ALLOCATED= Group.create_unallocated()

class ListOfCadetsWithGroups(ListOfCadets):
    @property
    def _object_class_contained(self):
        return CadetWithGroup

    def update_group_for_cadet(self, cadet:Cadet, chosen_group:Group):
        if self.cadet_is_allocated_to_group(cadet):
            self._update_group_for_existing_cadet(cadet=cadet, chosen_group=chosen_group)
        else:
            self._update_group_for_new_cadet(cadet=cadet, chosen_group=chosen_group)

    def _update_group_for_existing_cadet(self, cadet:Cadet, chosen_group:Group):
        cadet_id = cadet.id
        list_of_ids = self.list_of_ids
        idx = list_of_ids.index(cadet_id)
        if chosen_group.create_unallocated:
            ## don't store group as unallocated instead remove entirely
            self.pop(idx)
        else:
            self[idx] = CadetWithGroup(cadet_id=cadet_id, group=chosen_group)

    def _update_group_for_new_cadet(self, cadet:Cadet, chosen_group:Group):
        if chosen_group.is_unallocated:
            ## don't store group as unallocated
            return
        else:
            cadet_id = cadet.id
            self.append(CadetWithGroup(cadet_id=cadet_id, group=chosen_group))

    def cadets_in_list_not_allocated_to_group(self, list_of_cadets: ListOfCadets) -> ListOfCadets:
        my_ids = self.list_of_ids
        list_ids = list_of_cadets.list_of_ids

        ids_in_list_not_given_group = list(set(list_ids).difference(set(my_ids)))

        return list_of_cadets.subset_from_list_of_ids(full_list=list_of_cadets,
                                                      list_of_ids=ids_in_list_not_given_group)

    def group_for_cadet(self, cadet: Cadet):
        return self.group_for_cadet_id(cadet.id)

    def group_for_cadet_id(self, cadet_id: str) ->Group:
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

    def item_with_cadet_id(self, cadet_id: str) -> CadetWithGroup:
        list_of_cadet_ids = self.list_of_ids
        try:
            idx = list_of_cadet_ids.index(cadet_id)
        except ValueError:
            raise Exception("Cadet %s not found" % cadet_id)

        return self[idx]

    @property
    def list_of_ids(self) -> list:
        return [item.cadet_id for item in self]

