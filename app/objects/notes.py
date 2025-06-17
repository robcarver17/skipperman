import datetime
from dataclasses import dataclass

from app.objects.utilities.exceptions import arg_not_passed
from app.objects.utilities.generic_list_of_objects import (
   GenericListOfObjectsWithIds,
)
from app.objects.utilities.generic_objects import (
   GenericSkipperManObjectWithIds,
)
from app.data_access.configuration.fixed import LOWEST_PRIORITY, LOW_PRIORITY, MEDIUM_PRIORITY, HIGH_PRIORITY

NOT_ASSIGNED_TO_VOLUNTEER_ID = -999
LIST_OF_PRIORITIES = [LOWEST_PRIORITY, LOW_PRIORITY, MEDIUM_PRIORITY, HIGH_PRIORITY]

@dataclass
class Note(GenericSkipperManObjectWithIds):
    text: str
    author_volunteer_id: str
    created_datetime: datetime.datetime
    id: str = arg_not_passed
    priority: str = MEDIUM_PRIORITY
    completed: bool = False
    assigned_volunteer_id: str = NOT_ASSIGNED_TO_VOLUNTEER_ID

    @classmethod
    def new_quick_note(cls, text: str, author_volunteer_id: str):
        return cls(text=text, author_volunteer_id=author_volunteer_id, created_datetime=datetime.datetime.now())

    def mark_complete(self):
        self.completed = True

    def update_attributes(self, text: str, priority: str, assigned_volunteer_id: str, completed: bool):
        assert priority in LIST_OF_PRIORITIES
        self.text= text
        self.priority = priority
        self.assigned_volunteer_id =assigned_volunteer_id
        self.completed = completed

class ListOfNotes(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return Note

    def update_attributes(self,
                          note_id: str,
                          priority: str,
                          completed: bool,
                          assigned_volunteer_id:str,
                          text: str,

                          ):
        note = self.note_with_id(note_id)
        note.update_attributes(text=text, priority=priority, assigned_volunteer_id=assigned_volunteer_id,
                               completed=completed)

    def note_with_id(self, note_id: str) -> Note:
        return self.object_with_id(note_id)

    def completed_only(self) -> 'ListOfNotes':
        new_list = [note for note in self if note.completed]
        return ListOfNotes(new_list)

    def uncompleted_only(self) -> 'ListOfNotes':
        new_list = [note for note in self if not note.completed]
        return ListOfNotes(new_list)

    def add_quick_note(self, text: str, author_volunteer_id: str)-> Note:

        note = Note.new_quick_note(
            text=text,
            author_volunteer_id=author_volunteer_id,
        )
        note.id = self.next_id()
        self.append(note)
        print(note)
        return note


