from dataclasses import dataclass
from typing import Dict, List

import pandas as pd
from app.objects.utils import flatten
from app.objects.exceptions import arg_not_passed, missing_data

from app.objects.utils import most_common

from app.objects.events import Event, ListOfEvents

from app.objects.cadet_with_id_with_group_at_event import (
    CADET_NAME,
    GROUP_STR_NAME,
    ListOfCadetIdsWithGroups,
)
from app.objects.cadets import Cadet, ListOfCadets

from app.objects.day_selectors import Day, DictOfDaySelectors, DaySelector
from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject
from app.objects.groups import Group, ListOfGroups


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

    def as_str_dict(self, display_full_names: bool = True) -> dict:
        if display_full_names:
            cadet_name = self.cadet_full_name
        else:
            cadet_name = self.cadet_name_initials_only

        group_name = str(self.group)

        return {CADET_NAME: cadet_name, GROUP_STR_NAME: group_name}

    @property
    def cadet_id(self):
        return self.cadet.id


class ListOfCadetsWithGroupOnDay(List[CadetWithGroupOnDay]):
    def items_with_cadet_id(self, cadet_id: str) -> List[CadetWithGroupOnDay]:
        return [item for item in self if item.cadet_id == cadet_id]

    def unique_list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(set(self.list_of_cadets())))

    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets([cadet_with_group.cadet for cadet_with_group in self])

    def remove_unallocated(self) -> 'ListOfCadetsWithGroupOnDay':
        new_list = [cadet_with_group_on_day for cadet_with_group_on_day in self if not cadet_with_group_on_day.group.is_unallocated]

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
                cadet=list_of_cadets.object_with_id(allocation.cadet_id),
                group=list_of_groups.object_with_id(allocation.group_id),
                day=allocation.day,
            )
            for allocation in list_of_allocations
        ]

        return cls(list_of_cadets_with_group)

    def list_of_cadet_ids(self) -> List[str]:
        return [item.cadet.id for item in self]


class DaysAndGroups(Dict[Day, Group]):
    def update_group_on_day(self, day: Day, group: Group):
        self[day] = group

    def group_on_day(self, day: Day, default=Group.create_unallocated()) -> Group:
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

    def day_selector_for_group(self, group: Group) -> DaySelector:
        return DaySelector(
            [(day, True) for day, group_on_day in self.items() if group_on_day == group]
        )

    def most_common(self) -> Group:
        return most_common(self.list_of_groups, default=Group.create_unallocated())

    @property
    def list_of_groups(self) -> List[Group]:
        return list(self.values())


    @classmethod
    def create_unallocated_for_all_event_days(cls, event: Event):
        return cls(
            dict(
                [(day, Group.create_unallocated()) for day in event.weekdays_in_event()]
            )
        )

    @classmethod
    def create_empty(cls):
        return cls()


empty_days_and_groups = DaysAndGroups.create_empty()


class DictOfCadetsWithDaysAndGroupsAtEvent(Dict[Cadet, DaysAndGroups]):
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

    def add_or_upate_group_for_cadet_on_day(
        self,
        cadet: Cadet,
        day: Day,
        group: Group,

        ):
        current_allocation = self.get_days_and_groups_for_cadet(cadet=cadet)
        current_allocation.update_group_on_day(day=day, group=group)
        self.list_of_cadet_ids_with_groups.update_group_for_cadet_on_day(cadet_id=cadet.id,
                                                                         day=day,
                                                                         chosen_group_id=group.id)


    def remove_cadet_from_event(self, cadet: Cadet):
        for day in self.event.weekdays_in_event():
            self.remove_cadet_from_event_on_day(cadet=cadet, day=day)

        try:
            self.pop(cadet)
        except:
            pass

    def remove_cadet_from_event_on_day(self, cadet: Cadet, day: Day):
        current_allocation = self.get_days_and_groups_for_cadet(cadet=cadet)
        current_allocation.remove_cadet_from_event_on_day(day)
        self.list_of_cadet_ids_with_groups.remove_group_allocation_for_cadet_on_day(cadet_id=cadet.id, day=day)

    def list_of_cadets_in_group_on_day(self, day: Day, group: Group):
        return ListOfCadets(
            [
                cadet
                for cadet, days_and_groups in self.items()
                if days_and_groups.group_on_day(day) == group
            ]
        )


    def get_list_of_cadets_with_group_for_specific_day(self, day: Day, include_unallocated_cadets: bool) -> ListOfCadetsWithGroupOnDay:
        list_of_cadets_by_group = []
        for cadet in self.list_of_cadets:
            days_and_groups_for_cadet = self.get_days_and_groups_for_cadet(cadet)
            group_on_day = days_and_groups_for_cadet.group_on_day(day)
            list_of_cadets_by_group.append(
                CadetWithGroupOnDay(
                    cadet=cadet,
                    group=group_on_day,
                    day=day
                )
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
        raw_dict = dict(
            [
                (cadet, group)
                for cadet, group in raw_dict.items()
                if not group.is_unallocated
            ]
        )

        return raw_dict

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

        return ListOfGroups(unique_list)

    def days_and_groups(self) -> List[DaysAndGroups]:
        return list(self.values())

    def get_most_common_group_for_cadet(
        self, cadet: Cadet, default_group=missing_data
    ) -> Group:
        group_dict = self.get_days_and_groups_for_cadet(cadet, default=None)
        if group_dict is None:
            return default_group

        return group_dict.most_common()

    def get_days_and_groups_for_cadet(
        self, cadet: Cadet, default = arg_not_passed
    ) -> DaysAndGroups:
        if default == arg_not_passed:
            default = empty_days_and_groups

        return self.get(cadet, default)

    def filter_for_list_of_cadets(
        self, list_of_cadets: ListOfCadets
    ) -> "DictOfCadetsWithDaysAndGroupsAtEvent":
        ## doesn't affect underlying

        return DictOfCadetsWithDaysAndGroupsAtEvent(
            dict(
                [
                    (cadet, days_and_groups)
                    for cadet, days_and_groups in self.items()
                    if cadet in list_of_cadets
                ]
            ),
            list_of_cadet_ids_with_groups=self.list_of_cadet_ids_with_groups,
            event=self.event,
            list_of_groups=self.list_of_groups
        )

    def add_unallocated_and_filter_for_list_of_cadets(
        self, list_of_cadets: ListOfCadets
    ) -> "DictOfCadetsWithDaysAndGroupsAtEvent":
        new_dict = {}
        unallocated_all_days = DaysAndGroups.create_unallocated_for_all_event_days(
            self.event
        )
        for cadet in list_of_cadets:
            existing_groups = self.get_days_and_groups_for_cadet(cadet)
            if len(existing_groups) == 0:
                existing_groups = unallocated_all_days

            new_dict[cadet] = existing_groups

        return DictOfCadetsWithDaysAndGroupsAtEvent(
            new_dict,
            list_of_cadet_ids_with_groups=self.list_of_cadet_ids_with_groups,
            event=self.event,
            list_of_groups=self.list_of_groups
        )


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
) -> DictOfCadetsWithDaysAndGroupsAtEvent:
    event = list_of_events.object_with_id(event_id)

    raw_dict = compose_raw_dict_of_cadets_with_days_and_groups_at_event(
        list_of_cadets=list_of_cadets,
        list_of_groups=list_of_groups,
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
    )

    return DictOfCadetsWithDaysAndGroupsAtEvent(
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
