from dataclasses import dataclass
from typing import List

from app.objects.utilities.exceptions import missing_data
from app.objects.utilities.generic_objects import GenericSkipperManObjectWithIds
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
    get_idx_of_multiple_object_with_multiple_attr_in_list,
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


class ListOfEventWarnings(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return EventWarningLog

    def mark_all_active_event_warnings_with_priority_and_category_as_ignored(
        self, category: str, priority: str
    ):
        active_only = self.active_only()
        in_category = active_only.with_category(category)
        with_priority = in_category.with_priority(priority=priority)
        __ = [
            self.mark_event_warning_with_id_as_ignored(warning.id)
            for warning in with_priority
        ]

    def mark_all_ignored_event_warnings_with_priority_and_category_as_unignored(
        self, category: str, priority: str
    ):
        ignored_only = self.ignored_only()
        in_category = ignored_only.with_category(category)
        with_priority = in_category.with_priority(priority=priority)
        __ = [
            self.mark_event_warning_with_id_as_unignored(warning.id)
            for warning in with_priority
        ]

    def add_or_update_list_of_new_event_warnings_clearing_any_missing(
        self, list_of_warnings: List[str], category: str, priority: str
    ):

        self._update_list_of_new_event_warnings_clearing_any_missing(
            list_of_warnings=list_of_warnings, category=category, priority=priority
        )

        self._add_list_of_potentially_new_event_warnings(
            list_of_warnings=list_of_warnings, category=category, priority=priority
        )

    def _update_list_of_new_event_warnings_clearing_any_missing(
        self, list_of_warnings: List[str], category: str, priority: str
    ):

        all_existing_warnings_of_this_category_and_priority = (
            self.all_existing_warnings_of_this_category_and_priority(
                category=category, priority=priority
            )
        )

        ## mark missing as dealt with
        for existing_warning in all_existing_warnings_of_this_category_and_priority:
            if existing_warning.auto_refreshed:
                if existing_warning.warning not in list_of_warnings:
                    self.delete_event_warning_with_id_as_resolved(existing_warning.id)

    def _add_list_of_potentially_new_event_warnings(
        self, list_of_warnings: List[str], category: str, priority: str
    ):

        for potentially_new_warning in list_of_warnings:
            self.add_new_event_warning_checking_for_duplicate_from_components(  ## if duplicated will skip anyway
                warning=potentially_new_warning,
                category=category,
                priority=priority,
                auto_refreshed=True,  ## must be autorefreshed
            )

    def add_new_event_warning_checking_for_duplicate(
        self, event_warning: EventWarningLog
    ):
        if self.duplicate_warning_exists_in_data(
            warning=event_warning.warning,
            category=event_warning.category,
            priority=event_warning.priority,
        ):
            return

        event_warning.id = self.next_id()
        self.append(event_warning)

    def add_new_event_warning_checking_for_duplicate_from_components(
        self, warning: str, category: str, priority: str, auto_refreshed: bool
    ):
        if self.duplicate_warning_exists_in_data(
            warning=warning, category=category, priority=priority
        ):
            return

        self.append(
            EventWarningLog(
                id=self.next_id(),
                warning=warning,
                category=category,
                priority=priority,
                auto_refreshed=auto_refreshed,
                ignored=False,
            )
        )

    def duplicate_warning_exists_in_data(
        self, warning: str, category: str, priority: str
    ):
        matches = get_idx_of_multiple_object_with_multiple_attr_in_list(
            self,
            dict_of_attributes={
                "priority": priority,
                "category": category,
                "warning": warning,
            },
        )
        return len(matches) > 0

    def delete_event_warning_with_id_as_resolved(self, warning_id: str):
        idx = self.index_of_id(warning_id, missing_data)
        if idx is missing_data:
            return
        self.pop(idx)

    def mark_event_warning_with_id_as_ignored(self, warning_id: str):
        idx = self.index_of_id(warning_id, missing_data)
        if idx is missing_data:
            return

        item = self[idx]
        item.ignored = True

    def mark_event_warning_with_id_as_unignored(self, warning_id: str):
        idx = self.index_of_id(warning_id, missing_data)
        if idx is missing_data:
            return

        item = self[idx]
        item.ignored = False

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

    def with_priority(self, priority: str) -> "ListOfEventWarnings":
        return ListOfEventWarnings([item for item in self if item.priority == priority])

    def all_existing_warnings_of_this_category_and_priority(
        self, category: str, priority: str
    ) -> "ListOfEventWarnings":
        return ListOfEventWarnings(
            [
                item
                for item in self
                if item.category == category and item.priority == priority
            ]
        )
