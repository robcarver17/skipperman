from typing import List
from dataclasses import dataclass
import datetime


from app.objects.utilities.utils import similar
from app.objects.utilities.transform_data import transform_date_into_str
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    get_unique_object_with_attr_in_list,
)
from app.objects.utilities.generic_objects import GenericSkipperManObjectWithIds
from app.objects.utilities.exceptions import arg_not_passed
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

    @property
    def name(self):
        return self.event_name

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
        if duration > 7:
            raise Exception("Events cannot be more than one week long")

        if duration < 1:
            end_date = start_date
        else:
            end_date = add_days(start_date, duration - 1)

        return cls(event_name=event_name, start_date=start_date, end_date=end_date)

    def details_as_list_of_str(self):
        return [
            self.event_description,
            "From %s to %s, %d days: %s"
            % (
                str(self.start_date),
                str(self.end_date),
                self.duration,
                self.days_in_event_as_single_string(),
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
        my_day_selector = self.day_selector_for_days_in_event()
        return day_selector.days_that_intersect_with(my_day_selector)

    def day_selector_for_days_in_event(self) -> DaySelector:
        weekdays_covered = self.days_in_event()
        return DaySelector(
            dict([(day, day in weekdays_covered) for day in all_possible_days])
        )

    def days_in_event_as_single_string(self) -> str:
        names_of_days = self.days_in_event_as_list_of_string()

        return ", ".join(names_of_days)

    def days_in_event_as_list_of_string(self) -> List[str]:
        weekdays_in_event = self.days_in_event()
        names_of_days = [day.name for day in weekdays_in_event]

        return names_of_days

    def days_in_event(self) -> List[Day]:
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
        date_diff = datetime.date.today() - self.end_date
        return date_diff.days > 0


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

    def event_with_id(self, event_id: str, default=arg_not_passed):
        return self.object_with_id(event_id, default=default)

    def add(self, event: Event):
        self.confirm_event_does_not_already_exist(event)
        event.id = self.next_id()
        self.append(event)

    def confirm_event_does_not_already_exist(self, event: Event):
        exists = event.event_description in self.list_of_event_descriptions

        if exists:
            raise Exception("Event %s already in data" % str(event))

    def event_with_description(
        self, event_description: str, default=arg_not_passed
    ) -> Event:
        return get_unique_object_with_attr_in_list(
            some_list=self,
            attr_name="event_description",
            attr_value=event_description,
            default=default,
        )

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
        name_threshold: float = 0.8,
        date_threshold: float = 0.9,
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


def list_of_events_excluding_one_event_and_past_events(
    list_of_events: ListOfEvents,
    event_to_exclude: Event,
    sort_by: str = SORT_BY_START_ASC,
) -> ListOfEvents:
    list_of_events = ListOfEvents(
        [
            event
            for event in list_of_events
            if event.start_date < datetime.date.today()
            and not event.event_description == event_to_exclude.event_description
        ]
    )
    list_of_events = list_of_events.sort_by(sort_by)

    return list_of_events
