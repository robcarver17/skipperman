from dataclasses import dataclass
from typing import Dict, List

import pandas as pd
from app.objects.utils import flatten
from app.objects.exceptions import arg_not_passed, missing_data

from app.objects.utils import most_common

from app.objects.events import Event, ListOfEvents

from app.objects.cadet_with_id_with_group_at_event import CADET_NAME, GROUP_STR_NAME, ListOfCadetIdsWithGroups
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


class ListOfCadetsWithGroupOnDay(GenericListOfObjects):
    def _object_class_contained(self):
        return CadetWithGroupOnDay

    def items_with_cadet_id(self, cadet_id: str) -> List[CadetWithGroupOnDay]:
        return [item for item in self if item.cadet_id == cadet_id]


    def unique_list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets(list(set(self.list_of_cadets())))

    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets([cadet_with_group.cadet for cadet_with_group in self])

    def attendance_matrix(self) -> DictOfDaySelectors:
        list_of_availability = DictOfDaySelectors(
            [DaySelector({item.day: True}) for item in self]
        )

        return list_of_availability

    @classmethod
    def from_list_of_cadets_and_list_of_cadet_ids_with_groups(
        cls, list_of_cadets: ListOfCadets, list_of_allocations: ListOfCadetIdsWithGroups,
            list_of_groups: ListOfGroups
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

    def as_df_of_str(self, display_full_names: bool = True) -> pd.DataFrame:
        list_of_dicts = [
            item.as_str_dict(display_full_names=display_full_names) for item in self
        ]

        return pd.DataFrame(list_of_dicts)

    def list_of_cadet_ids(self) -> List[str]:
        return [item.cadet.id for item in self]

class DaysAndGroups(Dict[Day, Group]):
    @classmethod
    def from_list_of_cadets_with_group_by_day_for_specific_cadet(cls, cadet: Cadet, list_of_cadets_with_group_by_day: ListOfCadetsWithGroupOnDay):
        list_of_cadets_with_group_by_day_for_specific_cadet = list_of_cadets_with_group_by_day.items_with_cadet_id(cadet.id)
        dict_of_days_and_groups = dict([(cadet_with_groups_by_day.day, cadet_with_groups_by_day.group)        for cadet_with_groups_by_day in list_of_cadets_with_group_by_day_for_specific_cadet])

        return cls(dict_of_days_and_groups)

    def day_selector_for_group(self, group: Group) -> DaySelector:
        return DaySelector([(day, True) for day, group_on_day in self.items() if group_on_day==group])

    def most_common(self) -> Group:
        return  most_common(self.list_of_groups, default=Group.create_unallocated())

    @property
    def list_of_groups(self) -> List[Group]:
        return list(self.values())

    @classmethod
    def create_unallocated_for_all_event_days(cls, event: Event):
        return cls(
            dict(
                [
                    (day, Group.create_unallocated()) for day in event.weekdays_in_event()
                ]
            )
        )

    @classmethod
    def create_empty(cls):
        return cls()

empty_days_and_groups = DaysAndGroups.create_empty()

class DictOfCadetsWithDaysAndGroupsAtEvent(Dict[Cadet, DaysAndGroups]):
    def __init__(self, raw_dict: Dict[Cadet, DaysAndGroups],
                 list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups, event: Event):

        super().__init__(raw_dict)
        self._list_of_cadet_ids_with_groups =list_of_cadet_ids_with_groups
        self._event = event

    def cadets_in_group_during_event(self, group: Group) -> ListOfCadets:
        return ListOfCadets([
            cadet for cadet, days_and_groups in self.items() if group in days_and_groups.list_of_groups
        ])

    def all_groups_at_event(self) -> ListOfGroups:
        all_days_and_groups = self.days_and_groups()
        list_of_groups = [day_and_group.list_of_groups for day_and_group in all_days_and_groups]
        list_of_groups = flatten(list_of_groups)

        unique_list = list(set(list_of_groups))

        return ListOfGroups(unique_list)

    def days_and_groups(self) -> List[DaysAndGroups]:
        return list(self.values())

    def get_most_common_group_for_cadet(self, cadet: Cadet, default_group = missing_data) -> Group:
        group_dict = self.get_days_and_groups_for_cadet(cadet, default=None)
        if group_dict is None:
            return default_group

        return group_dict.most_common()

    def get_days_and_groups_for_cadet(self, cadet: Cadet, default: DaysAndGroups =arg_not_passed) -> DaysAndGroups:
        if default ==arg_not_passed:
            default = empty_days_and_groups

        return self.get(cadet, default)

    def filter_for_list_of_cadets(self, list_of_cadets: ListOfCadets) -> 'DictOfCadetsWithDaysAndGroupsAtEvent':
        ## doesn't affect underlying

        return DictOfCadetsWithDaysAndGroupsAtEvent(dict([
            (cadet, days_and_groups) for cadet, days_and_groups in self.items() if cadet in list_of_cadets]),
        list_of_cadet_ids_with_groups=self.list_of_cadet_ids_with_groups,
        event=self.event)

    def add_unallocated_and_filter_for_list_of_cadets(self, list_of_cadets: ListOfCadets)-> 'DictOfCadetsWithDaysAndGroupsAtEvent':
        new_dict = {}
        unallocated_all_days = DaysAndGroups.create_unallocated_for_all_event_days(self.event)
        for cadet in list_of_cadets:
            existing_groups = self.get_days_and_groups_for_cadet(cadet)
            if len(existing_groups)==0:
                existing_groups = unallocated_all_days

            new_dict[cadet] = existing_groups

        return DictOfCadetsWithDaysAndGroupsAtEvent(new_dict,
        list_of_cadet_ids_with_groups=self.list_of_cadet_ids_with_groups,
        event=self.event)


    @property
    def event(self) -> Event:
        return self._event

    @property
    def list_of_cadet_ids_with_groups(self)-> ListOfCadetIdsWithGroups:
        return self._list_of_cadet_ids_with_groups

def compose_dict_of_cadets_with_days_and_groups_at_event(event_id: str,
                                                         list_of_cadets: ListOfCadets,
                                                         list_of_groups: ListOfGroups,
                                                         list_of_events: ListOfEvents,
                                                         list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups
                                                         ) -> DictOfCadetsWithDaysAndGroupsAtEvent:
    event = list_of_events.object_with_id(event_id)

    raw_dict = compose_raw_list_of_cadets_with_days_and_groups_at_event(
        list_of_cadets=list_of_cadets,
        list_of_groups=list_of_groups,
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups
    )

    return DictOfCadetsWithDaysAndGroupsAtEvent(
        raw_dict=raw_dict,
        list_of_cadet_ids_with_groups=list_of_cadet_ids_with_groups,
        event=event
    )

def compose_raw_list_of_cadets_with_days_and_groups_at_event(
                                                list_of_cadets: ListOfCadets,
                                                list_of_groups: ListOfGroups,
                                                             list_of_cadet_ids_with_groups: ListOfCadetIdsWithGroups
                                                         ) -> Dict[Cadet, DaysAndGroups]:

    list_of_cadets_with_group_on_day =  ListOfCadetsWithGroupOnDay.from_list_of_cadets_and_list_of_cadet_ids_with_groups(
        list_of_cadets=list_of_cadets,
        list_of_allocations=list_of_cadet_ids_with_groups,
        list_of_groups=list_of_groups
    )
    list_of_cadets = list_of_cadets_with_group_on_day.unique_list_of_cadets()

    return dict([
        (cadet, DaysAndGroups.from_list_of_cadets_with_group_by_day_for_specific_cadet(cadet=cadet,
                                                                                       list_of_cadets_with_group_by_day=list_of_cadets_with_group_on_day))
        for cadet in list_of_cadets
    ])