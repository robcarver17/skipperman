from dataclasses import dataclass
from typing import List, Dict

from app.data_access.configuration.groups import all_groups_names, unallocated_group_name, lake_training_group_names, \
    river_training_group_names, mg_group_names
from app.objects.cadets import ListOfCadets, Cadet
from app.objects.day_selectors import Day
from app.objects.events import Event
from app.objects.exceptions import missing_data
from app.objects.generic_list_of_objects import GenericListOfObjectsWithIds
from app.objects.generic_objects import GenericSkipperManObjectWithIds
from app.objects.utils import in_x_not_in_y

LAKE_TRAINING = "Lake training"
RIVER_TRAINING = "River training"
MG = "MG"


def sorted_locations(locations: List[str]):
    order = [LAKE_TRAINING, RIVER_TRAINING, MG]
    return [location for location in order if location in locations]


class Group:
    def __init__(self, group_name: str):
        try:
            assert group_name in all_groups_names
        except:
            raise Exception(
                "Group %s is not a valid group name - correct or add to configuration"
                % group_name
            )

        self._group_name = group_name

    def __eq__(self, other):
        if type(other) is str:
            return self.group_name == other

        return self.group_name == other.group_name

    def __hash__(self):
        return hash(self.group_name)

    def __str__(self):
        return self.group_name

    def __repr__(self):
        return self.group_name

    def __lt__(self, other: "Group"):
        return index_group(self) < index_group(other)

    def as_str_replace_unallocated_with_empty(self) -> str:
        if self.is_unallocated:
            return ""
        else:
            return self.group_name

    @classmethod
    def create_unallocated(cls):
        return cls(unallocated_group_name)

    @property
    def is_unallocated(self):
        return self.group_name == unallocated_group_name

    @property
    def group_name(self):
        return self._group_name

    def type_of_group(self):
        if self.is_unallocated:
            return unallocated_group_name
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
        return self.group_name in lake_training_group_names

    def is_river_training(self) -> bool:
        return self.group_name in river_training_group_names

    def is_race_group(self) -> bool:
        return self.group_name in mg_group_names


GROUP_UNALLOCATED = Group.create_unallocated()
GROUP_UNALLOCATED_TEXT = "Unallocated"
ALL_GROUPS = [Group(group) for group in all_groups_names]


def index_group(group: Group):
    all_groups = all_groups_names + [GROUP_UNALLOCATED_TEXT]
    return all_groups.index(group)


def order_list_of_groups(list_of_groups: List[Group]) -> List[Group]:
    return [group for group in ALL_GROUPS if group in list_of_groups]


@dataclass
class CadetIdWithGroup(GenericSkipperManObjectWithIds):
    cadet_id: str
    group: Group
    day: Day


class ListOfCadetIdsWithGroups(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return CadetIdWithGroup

    def count_of_ids_by_day(self, event: Event) -> Dict[Day, int]:
        return dict(
            [(day, self.count_of_ids_for_day(day)) for day in event.weekdays_in_event()]
        )

    def count_of_ids_for_day(self, day: Day) -> int:
        matches = [item for item in self if item.day == day]

        return len(matches)

    def unique_list_of_cadet_ids(self, group: Group) -> List[str]:
        ids = list(set([item.cadet_id for item in self if item.group == group]))

        return ids

    def list_of_cadet_ids_in_group_on_day(self, group: Group, day: Day) -> List[str]:
        ids = [
            item.cadet_id for item in self if item.group == group and item.day == day
        ]

        return ids

    def total_in_each_group_as_dict(self) -> dict:
        list_of_groups = self.unique_list_of_groups()
        total_by_group = dict([(str(group), 0) for group in list_of_groups])
        for cadet_id_with_group in self:
            total_by_group[str(cadet_id_with_group.group)] += 1

        return total_by_group

    def unique_list_of_groups(self) -> list:
        list_of_groups = self.groups
        return list(set(list_of_groups))

    @property
    def groups(self) -> list:
        list_of_groups = [cadet_id_with_group.group for cadet_id_with_group in self]
        return list_of_groups

    def add_list_of_unallocated_cadets_on_day(
        self, list_of_unallocated_cadets: ListOfCadets, day: Day
    ):
        [self.add_unallocated_cadet(cadet, day) for cadet in list_of_unallocated_cadets]

    def add_unallocated_cadet(self, cadet: Cadet, day: Day):
        cadet_id = cadet.id
        self.append(
            CadetIdWithGroup(cadet_id=cadet_id, group=GROUP_UNALLOCATED, day=day)
        )

    def remove_group_allocation_for_cadet_on_day(self, cadet_id: str, day: Day):
        self.update_group_for_cadet_on_day(
            cadet_id=cadet_id, day=day, chosen_group=GROUP_UNALLOCATED
        )

    def update_group_for_cadet_on_day(
        self, cadet_id: str, day: Day, chosen_group: Group
    ):
        if self.cadet_is_allocated_to_group_on_day(cadet_id=cadet_id, day=day):
            self._update_group_for_existing_cadet_id_on_day(
                cadet_id=cadet_id, chosen_group=chosen_group, day=day
            )
        else:
            self._update_group_for_new_cadet(
                cadet_id=cadet_id, chosen_group=chosen_group, day=day
            )

    def _update_group_for_existing_cadet_id_on_day(
        self, cadet_id: str, day: Day, chosen_group: Group
    ):
        item_with_cadet_id_and_day = self.item_with_cadet_id_on_day(
            cadet_id=cadet_id, day=day
        )
        idx = self.index(item_with_cadet_id_and_day)
        if item_with_cadet_id_and_day.group == chosen_group:
            pass
        if chosen_group.is_unallocated:
            ## don't store group as unallocated instead remove entirely
            self.pop(idx)
        else:
            self[idx] = CadetIdWithGroup(cadet_id=cadet_id, group=chosen_group, day=day)

    def _update_group_for_new_cadet(self, cadet_id: str, chosen_group: Group, day: Day):
        if chosen_group.is_unallocated:
            ## don't store group as unallocated
            return
        else:
            self.append(
                CadetIdWithGroup(cadet_id=cadet_id, group=chosen_group, day=day)
            )

    def cadet_ids_in_passed_list_not_allocated_to_any_group(
        self, list_of_cadet_ids: List[str]
    ):
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

    def group_for_cadet_id_on_day(self, cadet_id: str, day: Day) -> Group:
        item = self.item_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        if item is missing_data:
            return GROUP_UNALLOCATED

        return item.group

    def cadet_is_allocated_to_group_on_day(self, cadet_id: str, day: Day) -> bool:
        item = self.item_with_cadet_id_on_day(cadet_id=cadet_id, day=day)
        return not item is missing_data

    def item_with_cadet_id(self, cadet_id: str) -> CadetIdWithGroup:
        idx = self.DEPRECATE_index_of_item_with_cadet_id(cadet_id)
        return self[idx]

    def item_with_cadet_id_on_day(self, cadet_id: str, day: Day) -> CadetIdWithGroup:
        items = [item for item in self if item.cadet_id == cadet_id and item.day == day]
        if len(items) == 0:
            return missing_data
        elif len(items) > 1:
            raise Exception("dupilicate groups")
        else:
            return items[0]

    def DEPRECATE_index_of_item_with_cadet_id(self, cadet_id: str) -> int:
        list_of_cadet_ids = self.list_of_ids
        try:
            idx = list_of_cadet_ids.index(cadet_id)
        except ValueError:
            raise Exception("Cadet %s not found" % cadet_id)

        return idx

    def subset_for_day(self, day: Day):
        return ListOfCadetIdsWithGroups([item for item in self if item.day == day])

    @property
    def list_of_ids(self) -> list:
        return [item.cadet_id for item in self]

    def sort_by_group(self):
        new_list = sorted(self, key=lambda x: x.group, reverse=False)
        return ListOfCadetIdsWithGroups(new_list)


CADET_NAME = "cadet"  #### FIXME USED IN REPORTING DELETE
GROUP_STR_NAME = "group"  #### FIXME USED IN REPORTING DELETE
