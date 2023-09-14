from dataclasses import dataclass
import datetime
from enum import Enum

from objects.utils import (
    similar,
    transform_str_from_date,
)
from objects.generic import GenericSkipperManObject, GenericListOfObjects


EventType = Enum(
    "EventType", ["Training", "Racing", "TrainingAndRacing", "Social", "Merchandise"]
)

# WA_event_id: int  ## does this need to be here?


@dataclass
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
            self._event_type_as_str
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

    @property
    def _start_of_event_as_str(self) -> str:
        start_date = self.start_date
        return transform_str_from_date(start_date)

    @property
    def _end_of_event_as_str(self) -> str:
        end_date = self.end_date
        return transform_str_from_date(end_date)

    @property
    def _event_type_as_str(self) -> str:
        return self.event_type.name

class ListOfEvents(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return Event

    @property
    def list_of_event_names(self)-> list:
        return [event.event_name for event in self]

