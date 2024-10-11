from typing import List
from dataclasses import dataclass
import datetime

from app.data_access.configuration.configuration import (
    SIMILARITY_LEVEL_TO_WARN_NAME,
    SIMILARITY_LEVEL_TO_WARN_DATE,
)

from app.objects.utils import transform_date_into_str, similar
from app.objects.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
)
from app.objects.generic_objects import GenericSkipperManObjectWithIds
from app.objects.exceptions import arg_not_passed
from app.objects.day_selectors import (
    day_given_datetime,
    all_possible_days,
    Day,
    DaySelector,
)



@dataclass
class Event(GenericSkipperManObjectWithIds):
    event_name: str  ## has to be preselected
    start_date: datetime.date
    end_date: datetime.date
    id: str = arg_not_passed

    def __repr__(self):
        return self.event_description

    def __eq__(self, other):
        return self.event_description == other.event_description

    def __hash__(self):
        return hash(self.event_description)

    def __len__(self):
        return self.duration

    @classmethod
    def from_date_length_and_name_only(
        cls, event_name: str, start_date: datetime.date, duration: int
    ):
        if duration < 1:
            end_date = start_date
        else:
            end_date = add_days(start_date, duration - 1)

        return cls(event_name=event_name, start_date=start_date, end_date=end_date)

    def details_as_list_of_str(self):

        return [
            self.event_description,
            "From %s to %s, %d days, covering %s"
            % (
                str(self.start_date),
                str(self.end_date),
                self.duration,
                self.weekdays_in_event_as_single_string(),
            ),
        ]

    @property
    def invalid(self) -> bool:
        invalid_reason = self.invalid_reason()

        return len(invalid_reason) > 0

    def invalid_reason(self) -> str:
        try:
            assert self.duration < 8
        except:
            return "Length of event greater than 7 days"

        return ""

    @property
    def event_description(self) -> str:
        return "%s %d" % (self.event_name, self.event_year)

    @property
    def event_year(self) -> int:
        return self.start_date.year

    @property
    def duration(self) -> int:
        timediff = self.end_date - self.start_date
        return timediff.days + 1

    def similarity_event_name(self, other_event: "Event") -> float:
        return similar(self.event_name, other_event.event_name)

    def similarity_start_date(self, other_event: "Event") -> float:
        return similar(self._start_of_event_as_str, other_event._start_of_event_as_str)

    def similarity_end_date(self, other_event: "Event") -> float:
        return similar(self._end_of_event_as_str, other_event._end_of_event_as_str)

    @property
    def _start_of_event_as_str(self) -> str:
        start_date = self.start_date
        return transform_date_into_str(start_date)

    @property
    def _end_of_event_as_str(self) -> str:
        end_date = self.end_date
        return transform_date_into_str(end_date)

    def days_in_event_overlap_with_selected_days(
        self, day_selector: DaySelector
    ) -> List[Day]:
        my_day_selector = self.day_selector_with_covered_days()
        return day_selector.days_that_intersect_with(my_day_selector)

    def day_selector_with_covered_days(self) -> DaySelector:
        weekdays_covered = self.weekdays_in_event()
        return DaySelector(
            dict([(day, day in weekdays_covered) for day in all_possible_days])
        )

    def first_day(self):
        ## relies on ordering
        return self.weekdays_in_event()[0]

    def weekdays_in_event_as_single_string(self) -> str:
        names_of_days = self.weekdays_in_event_as_list_of_string()

        return ", ".join(names_of_days)

    def weekdays_in_event_as_list_of_string(self) -> List[str]:
        weekdays_in_event = self.weekdays_in_event()
        names_of_days = [day.name for day in weekdays_in_event]

        return names_of_days

    def weekdays_in_event(self) -> List[Day]:
        date_list = self.dates_in_event()
        weekdays = [day_given_datetime(some_day) for some_day in date_list]

        return weekdays

    def dates_in_event(self) -> list:
        some_date = self.start_date
        date_list = []
        while some_date <= self.end_date:
            date_list.append(some_date)
            some_date += datetime.timedelta(days=1)
        return date_list

    def in_the_past(self) -> bool:
        days = datetime.date.today() - self.end_date
        return days.days > 0


def add_days(some_date: datetime.date, duration: int) -> datetime.date:
    return some_date + datetime.timedelta(days=duration)


today = datetime.datetime.today().date()

default_event = Event(start_date=today, end_date=add_days(today, 1), event_name="")


class ListOfEvents(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return Event

    @property
    def list_of_event_descriptions(self) -> list:
        return [event.event_description for event in self]

    def add(self, event: Event):
        event.id = self.next_id()
        self.append(event)

    def event_with_description(self, event_description: str) -> Event:
        list_of_descriptions = self.list_of_event_descriptions
        idx = list_of_descriptions.index(event_description)

        return self[idx]

    def sort_by(self, sort_by: str):
        if sort_by == SORT_BY_START_DSC:
            return self.sort_by_start_date_desc()
        elif sort_by == SORT_BY_START_ASC:
            return self.sort_by_start_date_asc()
        elif sort_by == SORT_BY_NAME:
            return self.sort_by_name()
        else:
            raise Exception("can't sort event list by %s" % sort_by)

    def sort_by_start_date_asc(self):
        return ListOfEvents(sorted(self, key=lambda x: x.start_date))

    def sort_by_start_date_desc(self):
        return ListOfEvents(sorted(self, key=lambda x: x.start_date, reverse=True))

    def sort_by_name(self):
        return ListOfEvents(sorted(self, key=lambda x: x.event_name))

    def similar_events(
        self,
        event: Event,
        name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME,
        date_threshold: float = SIMILARITY_LEVEL_TO_WARN_DATE,
    ) -> "ListOfEvents":
        similar_start_date = [
            other_event
            for other_event in self
            if event.similarity_start_date(other_event) > date_threshold
        ]
        similar_end_date = [
            other_event
            for other_event in self
            if event.similarity_end_date(other_event) > date_threshold
        ]

        similar_names = [
            other_event
            for other_event in self
            if event.similarity_event_name(other_event) > name_threshold
        ]

        joint_list_of_similar_events = list(
            set(similar_end_date + similar_start_date + similar_names)
        )

        return ListOfEvents(joint_list_of_similar_events)


SORT_BY_START_ASC = "Sort by start date, ascending"
SORT_BY_NAME = "Sort by event name"
SORT_BY_START_DSC = "Sort by start date, descending"


def list_of_events_excluding_one_event(
    list_of_events: ListOfEvents,
    event_to_exclude: Event,
    sort_by: str = SORT_BY_START_ASC,
    only_past: bool = True,
) -> ListOfEvents:
    if only_past:
        list_of_events = ListOfEvents(
            [
                event
                for event in list_of_events
                if event.start_date < event_to_exclude.start_date
            ]
        )
    else:
        list_of_events.pop_with_id(event_to_exclude.id)

    list_of_events = list_of_events.sort_by(sort_by)

    return list_of_events

