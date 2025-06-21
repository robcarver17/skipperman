from dataclasses import dataclass
from datetime import datetime
from typing import List

from app.objects.notes import Note, LIST_OF_PRIORITIES, ListOfNotes
from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.utilities.generic_list_of_objects import (
    get_unique_object_with_attr_in_list,
)


@dataclass
class NoteWithVolunteer:
    text: str
    author_volunteer: Volunteer
    created_datetime: datetime
    priority: str
    completed: bool
    assigned_volunteer: Volunteer
    id: str

    @classmethod
    def from_note(cls, note: Note, list_of_volunteers: ListOfVolunteers):
        volunteer_assigned = list_of_volunteers.volunteer_with_id(
            note.assigned_volunteer_id
        )
        volunteer_author = list_of_volunteers.volunteer_with_id(
            note.author_volunteer_id
        )

        return cls(
            text=note.text,
            created_datetime=note.created_datetime,
            priority=note.priority,
            assigned_volunteer=volunteer_assigned,
            author_volunteer=volunteer_author,
            completed=note.completed,
            id=note.id,
        )

    @classmethod
    def from_new_quick_note_and_volunteer_author(
        cls, note: Note, author_volunteer: Volunteer
    ):
        return cls(
            text=note.text,
            created_datetime=note.created_datetime,
            priority=note.priority,
            author_volunteer=author_volunteer,
            assigned_volunteer=author_volunteer,
            completed=note.completed,
            id=note.id,
        )

    def mark_complete(self):
        self.completed = True

    def update_attributes(
        self, text: str, priority: str, assigned_volunteer: Volunteer, completed: bool
    ):
        assert priority in LIST_OF_PRIORITIES
        self.text = text
        self.priority = priority
        self.assigned_volunteer = assigned_volunteer
        self.completed = completed


class ListOfNotesWithVolunteers(List[NoteWithVolunteer]):
    def __init__(
        self,
        raw_list: List[NoteWithVolunteer],
        list_of_notes: ListOfNotes,
        list_of_volunteers: ListOfVolunteers,
    ):
        super().__init__(raw_list)
        self._list_of_notes = list_of_notes
        self._list_of_volunteers = list_of_volunteers

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
            raw_list=raw_list,
            list_of_notes=self.list_of_notes,
            list_of_volunteers=self.list_of_volunteers,
        )

    def completed_only(self) -> "ListOfNotesWithVolunteers":
        new_list = [note for note in self if note.completed]
        return ListOfNotesWithVolunteers(
            new_list,
            list_of_notes=self.list_of_notes.completed_only(),
            list_of_volunteers=self.list_of_volunteers,
        )

    def uncompleted_only(self) -> "ListOfNotesWithVolunteers":
        new_list = [note for note in self if not note.completed]
        return ListOfNotesWithVolunteers(
            new_list,
            list_of_notes=self.list_of_notes.uncompleted_only(),
            list_of_volunteers=self.list_of_volunteers,
        )

    def add_quick_note(self, text: str, author_volunteer: Volunteer):
        note = self.list_of_notes.add_quick_note(
            text=text, author_volunteer_id=author_volunteer.id
        )
        note_with_volunteer = (
            NoteWithVolunteer.from_new_quick_note_and_volunteer_author(
                note=note, author_volunteer=author_volunteer
            )
        )
        self.append(note_with_volunteer)

    def update_attributes(
        self,
        note_id: str,
        priority: str,
        completed: bool,
        assigned_volunteer: Volunteer,
        text: str,
    ):
        existing_note = self.note_with_id(note_id)
        existing_note.update_attributes(
            priority=priority,
            completed=completed,
            assigned_volunteer=assigned_volunteer,
            text=text,
        )

        self.list_of_notes.update_attributes(
            note_id=note_id,
            priority=priority,
            completed=completed,
            assigned_volunteer_id=assigned_volunteer.id,
            text=text,
        )

    def note_with_id(self, note_id: str) -> NoteWithVolunteer:
        return get_unique_object_with_attr_in_list(
            self, attr_name="id", attr_value=note_id
        )

    @property
    def list_of_notes(self) -> ListOfNotes:
        return self._list_of_notes

    @property
    def list_of_volunteers(self) -> ListOfVolunteers:
        return self._list_of_volunteers


def compose_list_of_notes_with_volunteers_from_list_of_notes(
    list_of_notes: ListOfNotes, list_of_volunteers: ListOfVolunteers
) -> ListOfNotesWithVolunteers:
    raw_list = [
        NoteWithVolunteer.from_note(note=note, list_of_volunteers=list_of_volunteers)
        for note in list_of_notes
    ]

    return ListOfNotesWithVolunteers(
        raw_list=raw_list,
        list_of_volunteers=list_of_volunteers,
        list_of_notes=list_of_notes,
    )


SORT_BY_AUTHOR = "sort by author"
SORT_BY_DATE = "sort by date"
SORT_BY_PRIORITY = "sort by priority"
SORT_BY_ASSIGNED = "sort by assigned"
