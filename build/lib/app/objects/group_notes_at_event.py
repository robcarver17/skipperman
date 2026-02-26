from dataclasses import dataclass
from typing import Dict

from app.objects.groups import Group

from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,

)


@dataclass
class GroupNotesAtEventWithIds(GenericSkipperManObject):
    event_id: str
    group_id: str
    notes: str


class ListOfGroupNotesAtEventWithIds(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return GroupNotesAtEventWithIds


class DictOfNotesForGroupsAtEvent(Dict[Group, str]):
    def notes_for_group(self, group: Group):
        return self.get(group, "")
