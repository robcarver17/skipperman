import datetime
from dataclasses import dataclass

from app.objects.utilities.exceptions import arg_not_passed
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjectsWithIds,
)
from app.objects.utilities.generic_objects import (
    GenericSkipperManObjectWithIds,
)
from app.data_access.configuration.fixed import (
    LOWEST_PRIORITY,
    LOW_PRIORITY,
    MEDIUM_PRIORITY,
    HIGH_PRIORITY,
)

LIST_OF_PRIORITIES = [LOWEST_PRIORITY, LOW_PRIORITY, MEDIUM_PRIORITY, HIGH_PRIORITY]


@dataclass
class Note(GenericSkipperManObjectWithIds):
    text: str
    author_volunteer_id: str
    created_datetime: datetime.datetime
    assigned_volunteer_id: str
    priority: str
    completed: bool
    id: str = arg_not_passed

    @classmethod
    def new_quick_note(cls, text: str, author_volunteer_id: str):
        return cls(
            text=text,
            author_volunteer_id=author_volunteer_id,
            created_datetime=datetime.datetime.now(),
            assigned_volunteer_id=author_volunteer_id,
            priority=MEDIUM_PRIORITY,
            completed=False,
        )



class ListOfNotes(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return Note
