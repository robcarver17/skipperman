from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from app.objects.utilities.utils import flatten
from app.objects.utilities.exceptions import arg_not_passed, missing_data

from app.objects.utilities.utils import most_common

from app.objects.events import Event, ListOfEvents

from app.objects.cadet_with_id_with_group_at_event import (
    ListOfCadetIdsWithGroups,
)
from app.objects.cadets import Cadet, ListOfCadets

from app.objects.day_selectors import Day, DaySelector
from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.groups import Group, ListOfGroups, unallocated_group

CADET_NAME = "cadet"


@dataclass
class CadetWithGroup:
    ## display purposes
    cadet: Cadet
    group: Group


class ListOfCadetsWithGroups(List[CadetWithGroup]):
    pass


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
        #day = self.day.name

        return {"name": cadet, GROUP_STR_NAME: group}



class ListOfCadetsWithGroupOnDay(List[CadetWithGroupOnDay]):
    def as_df_of_cadet_names_and_groups_as_str(self, display_full_names: bool = True):
        list_of_dicts = [
            item.cadet_names_and_groups_as_str(display_full_names=display_full_names) for item in self
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

    @classmethod
    def from_list_of_cadets_and_list_of_cadet_ids_with_groups(
        cls,
        list_of_cadets: ListOfCadets,
        list_of_allocations: ListOfCadetIdsWithGroups,
        list_of_groups: ListOfGroups,
    ):
        list_of_cadets_with_group = [
            CadetWithGroupOnDay(
                cadet=list_of_cadets.cadet_with_id(allocation.cadet_id),
                group=list_of_groups.group_with_id(allocation.group_id),
                day=allocation.day,
            )
            for allocation in list_of_allocations
        ]

        return cls(list_of_cadets_with_group)

    def list_of_cadet_ids(self) -> List[str]:
        return [item.cadet.id for item in self]


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

    def remove_cadet_from_event_on_day(self, day):
        try:
            self.pop(day)
        except:
            pass

    @classmethod
    def from_list_of_cadets_with_group_by_day_for_specific_cadet(
        cls, cadet: Cadet, list_of_cadets_with_group_by_day: ListOfCadetsWithGroupOnDay
    ):
        list_of_cadets_with_group_by_day_for_specific_cadet = (
            list_of_cadets_with_group_by_day.items_with_cadet_id(cadet.id)
        )
        dict_of_days_and_groups = dict(
            [
                (cadet_with_groups_by_day.day, cadet_with_groups_by_day.group)
                for cadet_with_groups_by_day in list_of_cadets_with_group_by_day_for_specific_cadet
            ]
        )

        return cls(dict_of_days_and_groups)

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



class DaysAndGroupNames(Dict[Day, str]):
    def most_common(self) -> Group:
        return most_common(self.list_of_group_names, default=unallocated_group.name)

    @property
    def list_of_group_names(self):
        return list(self.values())

class DictOfCadetsWithDaysAndGroupsAtEvent(Dict[Cadet, DaysAndGroups]):
    def cadets_in_group_during_event(self, group: Group) -> ListOfCadets:
        return ListOfCadets(
            [
                cadet
                for cadet, days_and_groups in self.items()
                if group in days_and_groups.list_of_groups
            ]
        )

class DEPRECATE_DictOfCadetsWithDaysAndGroupsAtEvent(Dict[Cadet, DaysAndGroups]):
    def __init__(
        self,
        raw_dict: Dict[Cadet, DaysAndGroups],
        list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups,
        list_of_groups: ListOfGroups,
        event: Event,
    ):
        super().__init__(raw_dict)
        self._list_of_cadet_ids_with_groups = list_of_cadet_ids_with_groups
        self._event = event
        self._list_of_groups = list_of_groups

    def delete_cadet_from_event_and_return_messages(self, cadet):
        try:
            group_allocation_dict = self.pop(cadet)
            self.list_of_cadet_ids_with_groups.delete_cadet_with_id_from_event(cadet.id)
            return ["- removed group allocation %s" % str(group_allocation_dict)]
        except:
            return []

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

        self.list_of_cadet_ids_with_groups.update_group_for_cadet_on_day(
            cadet_id=cadet.id, day=day, chosen_group_id=group.id
        )

    def remove_cadet_from_event(self, cadet: Cadet):
        for day in self.event.days_in_event():
            self.remove_cadet_from_event_on_day(cadet=cadet, day=day)

        try:
            self.pop(cadet)
        except:
            pass

    def remove_cadet_from_event_on_day(self, cadet: Cadet, day: Day):
        current_allocation = self.get_days_and_groups_for_cadet(cadet=cadet)
        current_allocation.remove_cadet_from_event_on_day(day)
        self[cadet] = current_allocation

        self.list_of_cadet_ids_with_groups.remove_group_allocation_for_cadet_on_day(
            cadet_id=cadet.id, day=day
        )

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

    def cadets_in_group_during_event(self, group: Group) -> ListOfCadets:
        return ListOfCadets(
            [
                cadet
                for cadet, days_and_groups in self.items()
                if group in days_and_groups.list_of_groups
            ]
        )

    def all_groups_at_event(self) -> ListOfGroups:
        all_days_and_groups = self.days_and_groups()
        list_of_groups = [
            day_and_group.list_of_groups for day_and_group in all_days_and_groups
        ]
        list_of_groups = flatten(list_of_groups)

        unique_list = list(set(list_of_groups))
        all_groups = self.list_of_groups
        list_of_groups = [group for group in all_groups if group in unique_list]

        return ListOfGroups(list_of_groups)

    def days_and_groups(self) -> List[DaysAndGroups]:
        return list(self.values())

    def get_most_common_group_for_cadet(
        self, cadet: Cadet, default_group=missing_data
    ) -> Group:
        group_dict = self.get_days_and_groups_for_cadet(cadet, default=missing_data)
        if group_dict is missing_data:
            return default_group

        return group_dict.most_common()

    def subset_for_list_of_cadets(
        self, list_of_cadets: ListOfCadets
    ) -> "DEPRECATE_DictOfCadetsWithDaysAndGroupsAtEvent":
        raw_dict = dict(
            [
                (cadet, self.get_days_and_groups_for_cadet(cadet))
                for cadet in list_of_cadets
            ]
        )

        return DEPRECATE_DictOfCadetsWithDaysAndGroupsAtEvent(
            raw_dict=raw_dict,
            list_of_groups=self.list_of_groups,
            event=self.event,
            list_of_cadet_ids_with_groups=self.list_of_cadet_ids_with_groups,
        )

    def get_days_and_groups_for_cadet(
        self, cadet: Cadet, default=arg_not_passed
    ) -> DaysAndGroups:
        if default is arg_not_passed:
            default = DaysAndGroups()

        return self.get(cadet, default)

    @property
    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(self.keys()))

    @property
    def event(self) -> Event:
        return self._event

    @property
    def list_of_cadet_ids_with_groups(self) -> ListOfCadetIdsWithGroups:
        return self._list_of_cadet_ids_with_groups

    @property
    def list_of_groups(self) -> ListOfGroups:
        return self._list_of_groups


def compose_dict_of_cadets_with_days_and_groups_at_event(
    event_id: str,
    list_of_cadets: ListOfCadets,
    list_of_groups: ListOfGroups,
    list_of_events: ListOfEvents,
    list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups,
) -> DEPRECATE_DictOfCadetsWithDaysAndGroupsAtEvent:
    event = list_of_events.event_with_id(event_id)

    raw_dict = compose_raw_dict_of_cadets_with_days_and_groups_at_event(
        list_of_cadets=list_of_cadets,
        list_of_groups=list_of_groups,
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
    )

    return DEPRECATE_DictOfCadetsWithDaysAndGroupsAtEvent(
        raw_dict=raw_dict,
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
        list_of_groups=list_of_groups,
        event=event,
    )


def compose_raw_dict_of_cadets_with_days_and_groups_at_event(
    list_of_cadets: ListOfCadets,
    list_of_groups: ListOfGroups,
    list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups,
) -> Dict[Cadet, DaysAndGroups]:
    list_of_cadets_with_group_on_day = ListOfCadetsWithGroupOnDay.from_list_of_cadets_and_list_of_cadet_ids_with_groups(
        list_of_cadets=list_of_cadets,
        list_of_allocations=list_of_cadet_ids_with_groups,
        list_of_groups=list_of_groups,
    )
    list_of_cadets = list_of_cadets_with_group_on_day.unique_list_of_cadets()

    return dict(
        [
            (
                cadet,
                DaysAndGroups.from_list_of_cadets_with_group_by_day_for_specific_cadet(
                    cadet=cadet,
                    list_of_cadets_with_group_by_day=list_of_cadets_with_group_on_day,
                ),
            )
            for cadet in list_of_cadets
        ]
    )


GROUP_STR_NAME = "group"
