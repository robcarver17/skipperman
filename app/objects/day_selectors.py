import datetime
from copy import copy
from enum import Enum
from typing import Dict, List

from app.objects.exceptions import arg_not_passed

from app.objects.generic_objects import from_bool_to_str, from_str_to_bool

Day = Enum(
    "Day",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
)

all_possible_days = list(Day.__members__.values())
## we keep the original format, but dynamically add this to data frames on import


def day_given_datetime(some_day: datetime.date) -> Day:
    return all_possible_days[some_day.weekday()]

class ListOfDays(List[Day]):
    def __repr__(self):
        return ", ".join([day.name for day in self])

    def count_and_days_as_str(self):
        return "%d: %s" % (len(self), str(self))

class DaySelector(Dict[Day, bool]):
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        days = [day.name for day, selected in self.items() if selected]
        joined_days = ", ".join(days)

        return "days: %s " % joined_days

    def __eq__(self, other: "DaySelector"):
        for day in all_possible_days:
            if other.available_on_day(day) != self.available_on_day(day):
                return False

        return True

    def __hash__(self):
        return hash(
            "".join([day.name for day, selected in self.items() if selected])
        )

    def align_with_list_of_days(self, list_of_days: List[Day]) -> "DaySelector":
        return DaySelector([(day, self.available_on_day(day)) for day in list_of_days])

    def union(self, other: "DaySelector") -> "DaySelector":
        return DaySelector(
            [
                (day, True)
                for day in all_possible_days
                if other.available_on_day(day) or self.available_on_day(day)
            ]
        )

    def intersect(self, other: "DaySelector") -> "DaySelector":
        return DaySelector(
            [
                (day, True)
                for day in self.days_available()
                if other.available_on_day(day)
            ]
        )

    def days_that_intersect_with(self, other: "DaySelector") -> List[Day]:
        return [day for day in self.days_available() if other.available_on_day(day)]

    def as_str(self) -> str:
        items_as_str = [
            "%s:%s" % (day.name, from_bool_to_str(selection))
            for day, selection in self.items()
        ]
        return ",".join(items_as_str)

    @classmethod
    def from_str(cls, string: str):
        if len(string) == 0:
            return cls({})
        individual_items = string.split(",")
        key_value_pairs = [item.split(":") for item in individual_items]
        dict_of_pairs = dict(
            [
                (Day[day_name], from_str_to_bool(bool_str))
                for day_name, bool_str in key_value_pairs
            ]
        )

        return cls(dict_of_pairs)


    @classmethod
    def from_list_of_days(cls, list_of_days: List[Day]):
        return cls(
            dict(
                [
                    (day, True) for day in list_of_days
                ]
            )
        )

    @classmethod
    def create_empty(cls):
        return cls({})

    def is_empty(self):
        return len(self.days_available())==0

    def days_available(self) -> ListOfDays:
        return ListOfDays([day for day in self.all_days_in_selector if self.available_on_day(day)])

    def available_on_day(self, day: Day):
        return self.get(day, False)

    def make_unavailable_on_day(self, day: Day):
        self[day] = False

    def make_available_on_day(self, day: Day):
        self[day] = True

    @property
    def all_days_in_selector(self):
        return list(self.keys())

def union_across_day_selectors(list_of_day_selectors: List[DaySelector]) -> DaySelector:
    copied_list = copy(list_of_day_selectors)
    union_selector = copied_list.pop()
    while len(copied_list) > 0:
        next_selector = copied_list.pop()
        union_selector = union_selector.union(next_selector)

    return union_selector


empty_day_selector = DaySelector(dict([(day, False) for day in all_possible_days]))


def no_days_selected_from_available_days(day_selector: DaySelector, possible_days: list):
    return not any([day_selector.get(day, False) for day in possible_days])


dict_of_short_day_text_and_Days = dict(
    Mon=Day.Monday,
    Tues=Day.Tuesday,
    Wed=Day.Wednesday,
    Thurs=Day.Thursday,
    Fri=Day.Friday,
    Sat=Day.Saturday,
    Sun=Day.Sunday,
)
inverse_selection_dict = {value: key for key, value in dict_of_short_day_text_and_Days.items()}


def create_day_selector_from_short_form_text_with_passed_days(text: str, days_in_event: List[Day] = arg_not_passed) -> DaySelector:
    all_days = DaySelector.from_list_of_days(days_in_event)

    if len(text)==0:
        return all_days

    if "all days" in text.lower():
        return all_days

    if len(days_in_event)==2:
        if "both" in text.lower():
            return all_days

    starting_dict = dict()
    for day_to_find_text, day_to_select in dict_of_short_day_text_and_Days.items():
        if day_to_find_text in text:
            starting_dict[day_to_select] = True
        else:
            starting_dict[day_to_select] = False

    return DaySelector(starting_dict)

def day_selector_stored_format_from_text(text: str) -> DaySelector:
    starting_dict = dict()
    for day_to_find_text, day_to_select in dict_of_short_day_text_and_Days.items():
        if day_to_find_text in text:
            starting_dict[day_to_select] = True
        else:
            starting_dict[day_to_select] = False

    return DaySelector(starting_dict)


def day_selector_to_text_in_stored_format(day_selector: DaySelector) -> str:
    ## internal format is as per any day selector
    day_text_as_list = [
        inverse_selection_dict[day_selected]
        for day_selected, attending in day_selector.items()
        if attending
    ]
    return ",".join(day_text_as_list)


