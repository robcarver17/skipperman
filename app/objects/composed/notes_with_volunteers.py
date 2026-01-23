from dataclasses import dataclass
from datetime import datetime
from typing import List

from app.objects.volunteers import Volunteer


@dataclass
class NoteWithVolunteer:
    text: str
    author_volunteer: Volunteer
    created_datetime: datetime
    priority: str
    completed: bool
    assigned_volunteer: Volunteer
    id: str



class ListOfNotesWithVolunteers(List[NoteWithVolunteer]):

    def sort_by(self, sort_label: str):
        if sort_label == SORT_BY_DATE:
            return self.sort_by_date()
        elif sort_label == SORT_BY_ASSIGNED:
            return self.sort_by_assigned()
        elif sort_label == SORT_BY_PRIORITY:
            return self.sort_by_priority()
        elif sort_label == SORT_BY_AUTHOR:
            return self.sort_by_author()
        else:
            raise Exception("%s not known" % sort_label)

    def sort_by_author(self) -> "ListOfNotesWithVolunteers":
        return self._generic_sort("author_volunteer", False)

    def sort_by_date(self) -> "ListOfNotesWithVolunteers":
        return self._generic_sort("created_datetime", True)

    def sort_by_assigned(self) -> "ListOfNotesWithVolunteers":
        return self._generic_sort("assigned_volunteer", False)

    def sort_by_priority(self) -> "ListOfNotesWithVolunteers":
        return self._generic_sort("priority", False)

    def _generic_sort(self, sort_by_attribute: str, reverse: bool = False):
        raw_list = sorted(
            self, key=lambda note: getattr(note, sort_by_attribute), reverse=reverse
        )
        return ListOfNotesWithVolunteers(
            raw_list
        )

    def completed_only(self) -> "ListOfNotesWithVolunteers":
        new_list = [note for note in self if note.completed]
        return ListOfNotesWithVolunteers(
            new_list
        )

    def uncompleted_only(self) -> "ListOfNotesWithVolunteers":
        new_list = [note for note in self if not note.completed]
        return ListOfNotesWithVolunteers(
            new_list,
        )




SORT_BY_AUTHOR = "sort by author"
SORT_BY_DATE = "sort by date"
SORT_BY_PRIORITY = "sort by priority"
SORT_BY_ASSIGNED = "sort by assigned"
