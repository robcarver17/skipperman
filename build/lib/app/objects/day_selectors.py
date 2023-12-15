import datetime
from enum import Enum
from typing import Dict
from dataclasses import dataclass

Day = Enum("Day", [ "Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday", "Sunday"])

all_possible_days =list(Day.__members__.values())
## we keep the original format, but dynamically add this to data frames on import

def day_given_datetime(some_day: datetime.date):
    return all_possible_days[some_day.weekday()]

class DaySelector(Dict[Day, bool]):
    pass

ALL_DAYS_SELECTED = dict([(day, True) for day in all_possible_days])


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

def any_day_selector_from_text(text: str) -> DaySelector:
    starting_dict = dict()
    for day_to_find, day_to_select in selection_dict.items():
        if day_to_find in text:
            starting_dict[day_to_select] = True
        else:
            starting_dict[day_to_select] = False


    return DaySelector(starting_dict)

day_selector_stored_format_from_text = any_day_selector_from_text ## could use alternative

def day_selector_to_text_in_stored_format(day_selector: DaySelector) -> str:
    ## internal format is as per any day selector
    day_text_as_list = [inverse_selection_dict[day_selected] for day_selected, attending in day_selector.items() if attending]
    return ",".join(day_text_as_list)



