from typing import List, Dict
import pandas as pd

from app.objects_OLD.cadet_at_event import CadetEventData
from app.objects_OLD.day_selectors import Day, ListOfDaySelectors, DaySelector
from app.objects_OLD.primtive_with_id.groups import Group, ListOfCadetIdsWithGroups, CADET_NAME, GROUP_STR_NAME

from app.objects_OLD.cadets import Cadet, ListOfCadets
from dataclasses import dataclass
from app.objects_OLD.generic_list_of_objects import (
    GenericListOfObjects,
)
from app.objects_OLD.generic_objects import GenericSkipperManObject


class DaysAndGroups(Dict[Day, Group]):
    pass



@dataclass
class CadetAtEventWithGroupsByDay:
    cadet: Cadet
    event_data: CadetEventData
    days_and_groups: DaysAndGroups

from app.objects_OLD.exceptions import MissingData, MultipleMatches

class ListOfCadetsAtEventWithGroupsByDay(List[CadetAtEventWithGroupsByDay]):
    def cadet_at_event_with_groups_by_day_given_id(self, cadet_id: str):
        list_of_results = [cadet_at_event_with_groups_by_day for cadet_at_event_with_groups_by_day in self if cadet_at_event_with_groups_by_day.cadet.id == cadet_id]
        if len(list_of_results)>1:
            raise MultipleMatches
        elif len(list_of_results)==0:
            raise MissingData

        return list_of_results[0]

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

class ListOfCadetsWithGroup(GenericListOfObjects):
    def _object_class_contained(self):
        return CadetWithGroupOnDay

    def items_with_cadet_id(self, cadet_id: str) -> List[CadetWithGroupOnDay]:
        return [item for item in self if item.cadet_id == cadet_id]

    def list_of_cadets(self) -> ListOfCadets:
        return ListOfCadets([cadet_with_group.cadet for cadet_with_group in self])

    def attendance_matrix(self) -> ListOfDaySelectors:
        list_of_availability = ListOfDaySelectors(
            [DaySelector({item.day: True}) for item in self]
        )

        return list_of_availability

    @classmethod
    def from_list_of_cadets_and_list_of_allocations(
        cls, list_of_cadets: ListOfCadets, list_of_allocations: ListOfCadetIdsWithGroups
    ):
        list_of_cadets_with_group = [
            CadetWithGroupOnDay(
                cadet=list_of_cadets.object_with_id(allocation.cadet_id),
                group=allocation.group,
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
