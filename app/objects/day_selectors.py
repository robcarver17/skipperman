import datetime
from enum import Enum
from typing import Dict, List

import pandas as pd

from app.objects.generic import from_bool_to_str, from_str_to_bool
Day = Enum("Day", [ "Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday", "Sunday"])

all_possible_days =list(Day.__members__.values())
## we keep the original format, but dynamically add this to data frames on import

def day_given_datetime(some_day: datetime.date) -> Day:
    return all_possible_days[some_day.weekday()]

class DaySelector(Dict[Day, bool]):
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        days = [day.name for day, selected in self.items() if selected]

        return ", ".join(days)

    def __eq__(self, other: 'DaySelector'):
        for day in all_possible_days:
            if other.get(day, False)!=self.get(day, False):
                return False

        return True

    def as_str(self)-> str:
        items_as_str = ["%s:%s" % (day.name, from_bool_to_str(selection)) for day,selection in self.items()]
        return ",".join(items_as_str)

    @classmethod
    def from_str(cls, string:str):
        if len(string)==0:
            return cls({})
        individual_items = string.split(",")
        key_value_pairs = [
            item.split(":") for item in individual_items
        ]
        dict_of_pairs = dict(
            [
                (Day[day_name], from_str_to_bool(bool_str))
                for day_name,bool_str in key_value_pairs
            ]
        )

        return cls(dict_of_pairs)

    def days_available(self) -> List[Day]:
        return [day
                    for day in all_possible_days
                if self.available_on_day(day)]

    def available_on_day(self, day: Day):
        return self.get(day, False)

    def make_unavailable_on_day(self, day: Day):
        self[day] = False

    def make_available_on_day(self, day: Day):
        self[day] = True


ALL_DAYS_SELECTED = dict([(day, True) for day in all_possible_days])
NO_DAYS_SELECTED = dict([(day, False) for day in all_possible_days])

def no_days_selected(day_selector: DaySelector, possible_days: list):
    return not any([day_selector.get(day, False) for day in possible_days])

def weekend_day_selector_from_text(text: str) -> DaySelector: ## we read WA files like this but don't write them internally
    if text=="Saturday only":
        return DaySelector({Day.Saturday: True, Day.Sunday: False})
    elif text=="Sunday only":
        return DaySelector({Day.Saturday: False, Day.Sunday: True})
    elif text == "Both days":
        return DaySelector({Day.Saturday: True, Day.Sunday: True})
    raise Exception("Day selection text %s not recognised" % text)

selection_dict = dict(Mon= Day.Monday, Tues=Day.Tuesday, Wed=Day.Wednesday, Thurs=Day.Thursday, Fri=Day.Friday, Sat = Day. Saturday, Sun=Day.Sunday)
inverse_selection_dict = {value: key for key, value in selection_dict.items()}

def any_day_selector_from_short_form_text(text: str) -> DaySelector:

    starting_dict = dict()
    for day_to_find, day_to_select in selection_dict.items():
        if day_to_find in text:
            starting_dict[day_to_select] = True
        else:
            starting_dict[day_to_select] = False


    return DaySelector(starting_dict)

day_selector_stored_format_from_text = any_day_selector_from_short_form_text ## could use alternative

def day_selector_to_text_in_stored_format(day_selector: DaySelector) -> str:
    ## internal format is as per any day selector
    day_text_as_list = [inverse_selection_dict[day_selected] for day_selected, attending in day_selector.items() if attending]
    return ",".join(day_text_as_list)

class ListOfDaySelectors(List[DaySelector]):

    def as_pd_data_frame(self) -> pd.DataFrame:
        list_of_dicts = [from_day_selector_to_dict_for_pd(day_selector) for day_selector in self]
        df = pd.DataFrame(list_of_dicts)
        df = df.fillna("N/A")

        return df

def from_day_selector_to_dict_for_pd(day_selector: DaySelector) -> dict:
    as_dict = {}
    for key in day_selector.keys():
        if day_selector[key]:
            as_dict[key.name] = "[  ]"

    return as_dict

