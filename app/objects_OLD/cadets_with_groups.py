from typing import List

from app.objects.composed.cadets_at_event_with_groups import DaysAndGroups
from app.objects.composed.cadets_at_event_with_registration_data import (
    CadetRegistrationData,
)

from app.objects.cadets import Cadet
from dataclasses import dataclass
from app.objects.exceptions import MissingData, MultipleMatches


@dataclass
class CadetAtEventWithGroupsByDay:
    cadet: Cadet
    event_data: CadetRegistrationData
    days_and_groups: DaysAndGroups


class ListOfCadetsAtEventWithGroupsByDay(List[CadetAtEventWithGroupsByDay]):
    def cadet_at_event_with_groups_by_day_given_id(self, cadet_id: str):
        list_of_results = [
            cadet_at_event_with_groups_by_day
            for cadet_at_event_with_groups_by_day in self
            if cadet_at_event_with_groups_by_day.cadet.id == cadet_id
        ]
        if len(list_of_results) > 1:
            raise MultipleMatches
        elif len(list_of_results) == 0:
            raise MissingData

        return list_of_results[0]
