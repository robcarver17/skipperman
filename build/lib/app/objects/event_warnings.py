from dataclasses import dataclass
from typing import List

from app.objects.utilities.generic_objects import GenericSkipperManObjectWithIds
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
)


@dataclass
class EventWarningLog(GenericSkipperManObjectWithIds):
    priority: str
    category: str
    warning: str
    auto_refreshed: bool
    ignored: bool = False
    id: str = ""

    @property
    def active(self):
        return not self.ignored


CADET_IDENTITY = "Cadet identity"
CADET_DOB = "Cadet DOB"
CADET_REGISTRATION = "Cadet registration"
CADET_MANUALLY_ADDED = "Cadet manual registration"
CADET_SKIPPED_TEMPORARY = "Cadet skipped in registration"
VOLUNTEER_IDENTITY = "Volunteer identity"
VOLUNTEER_QUALIFICATION = "Volunteer qualification"
CADET_WITHOUT_ADULT = "Cadet without appropriate adult"
VOLUNTEER_AVAILABILITY = "Volunteer availability"
VOLUNTEER_PREFERENCE = "Volunteer preference"
VOLUNTEER_GROUP = "Volunteer / Cadet group overlap"
VOLUNTEER_UNCONNECTED = "Unconnected volunteer"
MISSING_DRIVER = "Missing driver"
DOUBLE_BOOKED = "On two boats at same time"


class ListOfEventWarnings(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return EventWarningLog

    def get_list_of_warnings_at_event_for_categories_sorted_by_priority_and_category(
        self, list_of_categories: List[str]
    ) -> "ListOfEventWarnings":
        in_categories = self.in_categories(list_of_categories)
        in_categories.sort(key=lambda item: item.category)
        in_categories.sort(key=lambda item: item.priority)

        return in_categories

    def active_only(self) -> "ListOfEventWarnings":
        return ListOfEventWarnings([item for item in self if item.active])

    def ignored_only(self) -> "ListOfEventWarnings":
        return ListOfEventWarnings([item for item in self if item.ignored])

    def in_categories(self, list_of_categories: List[str]) -> "ListOfEventWarnings":
        new_list = []
        for category in list_of_categories:
            new_list += self.with_category(category)

        return ListOfEventWarnings(new_list)

    def with_category(self, category: str) -> "ListOfEventWarnings":
        return ListOfEventWarnings([item for item in self if item.category == category])
