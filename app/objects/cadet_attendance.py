from typing import Dict, List

import pandas as pd

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.day_selectors import DaySelector, Day, all_possible_days


class DictOfDaySelectors(Dict[Cadet, DaySelector]):
    def align_with_list_of_days(self, list_of_days: List[Day]) -> "DictOfDaySelectors":
        return DictOfDaySelectors(
            dict(
                [
                    (cadet, day_selector.align_with_list_of_days(list_of_days))
                    for cadet, day_selector in self.items()
                ]
            )
        )

    def intersect(self, other: "DictOfDaySelectors"):
        return DictOfDaySelectors(
            dict(
                [
                    (cadet, self[cadet].intersect(other[cadet]))
                    for cadet in self.list_of_cadets
                ]
            )
        )

    def as_pd_data_frame(self) -> pd.DataFrame:
        list_of_dicts = [
            from_day_selector_to_dict_for_pd(day_selector)
            for day_selector in self.values()
        ]
        df = pd.DataFrame(list_of_dicts)
        df = df.fillna("N/A")

        return df

    @property
    def list_of_cadets(self):
        return ListOfCadets(list(self.keys()))


def from_day_selector_to_dict_for_pd(day_selector: DaySelector) -> dict:
    as_dict = {}
    for day in all_possible_days:
        if day_selector.available_on_day(day):
            as_dict[day.name] = "[  ]"

    return as_dict
