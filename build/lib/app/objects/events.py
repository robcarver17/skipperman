from dataclasses import dataclass
import datetime
from enum import Enum

from app.data_access.configuration.configuration import (
    SIMILARITY_LEVEL_TO_WARN_NAME,
    SIMILARITY_LEVEL_TO_WARN_DATE,
)

from app.objects.utils import transform_str_from_date, similar
from app.objects.generic import GenericSkipperManObject, GenericListOfObjects


EventType = Enum(
    "EventType", ["Training", "Racing", "TrainingAndRacing", "Social", "Merchandise"]
)
list_of_event_types = [e.name for e in EventType]

# WA_event_id: int  ## does this need to be here?


@dataclass(frozen=True)
class Event(GenericSkipperManObject):
    event_name: str  ## has to be preselected
    start_date: datetime.date
    end_date: datetime.date
    event_type: EventType

    def __repr__(self):
        return self.event_description

    @property
    def verbose_repr(self):
        return "%s from %s to %s, type %s" % (
            self.event_name,
            self._start_of_event_as_str,
            self._end_of_event_as_str,
            self.event_type_as_str,
        )

    @property
    def id(self) -> str:
        event_name_no_spaces = self.event_name.replace(" ", "")
        return "%s_%d" % (event_name_no_spaces, self.event_year)

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
        return transform_str_from_date(start_date)

    @property
    def _end_of_event_as_str(self) -> str:
        end_date = self.end_date
        return transform_str_from_date(end_date)

    @property
    def event_type_as_str(self) -> str:
        return self.event_type.name


default_event = Event(
    start_date=datetime.datetime.now(),
    end_date=datetime.datetime.now(),
    event_name="",
    event_type=EventType.Training,
)


class ListOfEvents(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return Event

    @property
    def list_of_event_names(self) -> list:
        return [event.event_name for event in self]

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