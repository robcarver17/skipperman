from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from app.data_access.configuration.field_list_groups import GROUP_ALLOCATION_FIELDS_HIDE

from app.objects.utilities.utils import flatten
from app.objects.utilities.exceptions import arg_not_passed, missing_data

from app.objects.utilities.utils import most_common

from app.objects.events import Event, ListOfEvents

from app.objects.cadets import Cadet, ListOfCadets

from app.objects.day_selectors import Day, DaySelector
from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.groups import Group, ListOfGroups, unallocated_group

CADET_NAME = "cadet"



@dataclass
class CadetWithGroupOnDay(GenericSkipperManObject):
    ## For display purposes, can't store
    cadet: Cadet
    group: Group
    day: Day

    @property
    def cadet_name_initials_only(self) -> str:
        return self.cadet.initial_and_surname

    @property
    def cadet_full_name(self) -> str:
        return self.cadet.name

    @property
    def cadet_id(self):
        return self.cadet.id

    def cadet_names_and_groups_as_str(self, display_full_names: bool = True) -> dict:
        if display_full_names:
            cadet = self.cadet.name
        else:
            cadet = self.cadet.initial_and_surname

        group = self.group.name
        # day = self.day.name

        return {"name": cadet, GROUP_STR_NAME: group}


class ListOfCadetsWithGroupOnDay(List[CadetWithGroupOnDay]):
    def as_df_of_cadet_names_and_groups_as_str(self, display_full_names: bool = True):
        list_of_dicts = [
            item.cadet_names_and_groups_as_str(display_full_names=display_full_names)
            for item in self
        ]
        return pd.DataFrame(list_of_dicts)

    def items_with_cadet_id(self, cadet_id: str) -> List[CadetWithGroupOnDay]:
        return [item for item in self if item.cadet_id == cadet_id]

    def unique_list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(set(self.list_of_cadets())))

    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets([cadet_with_group.cadet for cadet_with_group in self])

    def remove_unallocated(self) -> "ListOfCadetsWithGroupOnDay":
        new_list = [
            cadet_with_group_on_day
            for cadet_with_group_on_day in self
            if not cadet_with_group_on_day.group.is_unallocated
        ]

        return ListOfCadetsWithGroupOnDay(new_list)



class DaysAndGroups(Dict[Day, Group]):
    def update_group_on_day(self, day: Day, group: Group):
        if group.is_unallocated:
            try:
                self.pop(day)
            except:
                pass

        self[day] = group

    def group_on_day(self, day: Day, default=arg_not_passed) -> Group:
        if default is arg_not_passed:
            default = unallocated_group

        return self.get(day, default)


    def day_selector_when_cadet_in_group(self, group: Group) -> DaySelector:
        return DaySelector(
            [(day, True) for day, group_on_day in self.items() if group_on_day == group]
        )

    def most_common(self) -> Group:
        return most_common(self.list_of_groups, default=unallocated_group)

    @property
    def list_of_groups(self) -> List[Group]:
        return list(self.values())

    @classmethod
    def create_unallocated_for_all_event_days(cls, event: Event):
        return cls(dict([(day, unallocated_group) for day in event.days_in_event()]))

    @classmethod
    def create_empty(cls):
        return cls()




class DictOfCadetsWithDaysAndGroupsAtEvent(Dict[Cadet, DaysAndGroups]):
    def add_or_upate_group_for_cadet_on_day(
        self,
        cadet: Cadet,
        day: Day,
        group: Group,
    ):
        current_allocation = self.get_days_and_groups_for_cadet(cadet=cadet)
        current_group = current_allocation.group_on_day(day)

        if current_group == group:
            return

        current_allocation.update_group_on_day(day=day, group=group)
        self[cadet] = current_allocation

    def days_and_groups_for_cadet(self, cadet: Cadet):
        return self.get(cadet, DaysAndGroups())

    def cadets_in_group_during_event(self, group: Group) -> ListOfCadets:
        return ListOfCadets(
            [
                cadet
                for cadet, days_and_groups in self.items()
                if group in days_and_groups.list_of_groups
            ]
        )

    def get_most_common_group_for_cadet(
        self, cadet: Cadet, default_group=missing_data
    ) -> Group:
        group_dict = self.get_days_and_groups_for_cadet(cadet, default=missing_data)
        if group_dict is missing_data:
            return default_group

        return group_dict.most_common()

    def get_days_and_groups_for_cadet(
        self, cadet: Cadet, default=arg_not_passed
    ) -> DaysAndGroups:
        if default is arg_not_passed:
            default = DaysAndGroups()

        return self.get(cadet, default)

    def list_of_cadets_in_group_on_day(self, day: Day, group: Group):
        return ListOfCadets(
            [
                cadet
                for cadet, days_and_groups in self.items()
                if days_and_groups.group_on_day(day) == group
            ]
        )

    def get_list_of_cadets_with_group_for_specific_day(
        self, day: Day, include_unallocated_cadets: bool
    ) -> ListOfCadetsWithGroupOnDay:
        list_of_cadets_by_group = []
        list_of_cadets = self.list_of_cadets.sort_by_name()
        for cadet in list_of_cadets:
            days_and_groups_for_cadet = self.get_days_and_groups_for_cadet(cadet)
            group_on_day = days_and_groups_for_cadet.group_on_day(day)
            list_of_cadets_by_group.append(
                CadetWithGroupOnDay(cadet=cadet, group=group_on_day, day=day)
            )

        list_of_cadets_by_group = ListOfCadetsWithGroupOnDay(list_of_cadets_by_group)
        if not include_unallocated_cadets:
            list_of_cadets_by_group = list_of_cadets_by_group.remove_unallocated()

        return list_of_cadets_by_group

    def subset_for_day(self, day: Day) -> Dict[Cadet, Group]:
        raw_dict = dict(
            [
                (cadet, days_and_groups.group_on_day(day))
                for cadet, days_and_groups in self.items()
            ]
        )
        dict_without_unallocated = dict(
            [
                (cadet, group)
                for cadet, group in raw_dict.items()
                if not group.is_unallocated
            ]
        )

        return dict_without_unallocated

    def sorted_all_groups_at_event(self, all_groups: ListOfGroups) -> ListOfGroups:
        unique_list = self.unique_list_of_groups_at_event()
        list_of_groups = [group for group in all_groups if group in unique_list]

        return ListOfGroups(list_of_groups)

    def unique_list_of_groups_at_event(self)-> ListOfGroups:
        all_days_and_groups = self.days_and_groups()
        list_of_groups = [
            day_and_group.list_of_groups for day_and_group in all_days_and_groups
        ]
        list_of_groups = flatten(list_of_groups)

        unique_list = list(set(list_of_groups))

        return ListOfGroups(unique_list)

    def days_and_groups(self) -> List[DaysAndGroups]:
        return list(self.values())

    def subset_for_list_of_cadets(
        self, list_of_cadets: ListOfCadets
    ) -> "DictOfCadetsWithDaysAndGroupsAtEvent":
        raw_dict = dict(
            [
                (cadet, self.get_days_and_groups_for_cadet(cadet))
                for cadet in list_of_cadets
            ]
        )

        return DictOfCadetsWithDaysAndGroupsAtEvent(raw_dict)

    def all_groups_at_event_excluding_unallocated(self) -> ListOfGroups:
        unique_list = self.unique_list_of_groups_at_event()
        unique_list.remove_unallocated()

        return unique_list


    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))




GROUP_STR_NAME = "group"


class DictOfEventAllocations(Dict[Cadet, Dict[Event, str]]):
    def __init__(
        self, raw_dict: Dict[Cadet, Dict[Event, str]], list_of_events: ListOfEvents
    ):
        super().__init__(raw_dict)
        self._list_of_events = list_of_events

    def previous_group_names_for_cadet_as_list(self, cadet: Cadet):
        previous_groups_for_cadet_by_event = self.get(cadet)
        ## ordered by event already
        return list(previous_groups_for_cadet_by_event.values())

    @property
    def list_of_events(self) -> ListOfEvents:
        return self._list_of_events


@dataclass
class GroupAllocationInfo:
    dict_of_dicts: Dict[str, Dict[Cadet, str]]

    def visible_field_names(self) -> list:
        fields = [
            field
            for field in self.field_names
            if field not in GROUP_ALLOCATION_FIELDS_HIDE
        ]

        return fields

    @property
    def field_names(self) -> list:
        return list(self.dict_of_dicts.keys())

    def dict_for_field_name(self, field_name: str) -> Dict[Cadet, str]:
        info_dict_for_key = self.dict_of_dicts.get(field_name, None)
        if info_dict_for_key is None:
            raise Exception("Group allocation info not found for %s" % field_name)

        return info_dict_for_key

    def group_info_dict_for_cadet_as_ordered_list(self, cadet: Cadet):
        info_dict = self.get_allocation_info_for_cadet(cadet)

        return [
            info_dict.get(field_name, "") for field_name in self.visible_field_names()
        ]

    def get_allocation_info_for_cadet(self, cadet: Cadet) -> dict:
        field_names = self.field_names
        info_dict = dict(
            [
                (
                    field_name,
                    cadet_info_from_info_dict(self, cadet=cadet, field_name=field_name),
                )
                for field_name in field_names
            ]
        )

        return info_dict

    def remove_empty_fields(self):
        dict_of_dicts = self.dict_of_dicts
        ## in place
        for field_name in list(self.field_names):
            if all_empty(self.dict_for_field_name(field_name)):
                dict_of_dicts.pop(field_name)


def cadet_info_from_info_dict(
    group_allocation_info: GroupAllocationInfo, cadet: Cadet, field_name: str
):
    info_dict_for_key = group_allocation_info.dict_for_field_name(field_name)

    cadet_value = info_dict_for_key.get(cadet, None)
    if cadet_value is None:
        raise Exception("Group allocation info not found for cadet %s" % cadet)

    return cadet_value


def all_empty(some_dict: dict):
    all_values = list(some_dict.values())
    all_values_as_str = [str(x) for x in all_values]
    return all([len(value) == 0 for value in all_values_as_str])
