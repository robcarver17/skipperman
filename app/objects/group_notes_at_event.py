from dataclasses import dataclass

from app.objects.utilities.exceptions import missing_data
from app.objects.utilities.generic_objects import GenericSkipperManObject
from app.objects.utilities.generic_list_of_objects import GenericListOfObjects, get_unique_object_with_multiple_attr_in_list,get_idx_of_unique_object_with_multiple_attr_in_list

@dataclass
class GroupNotesAtEventWithIds(GenericSkipperManObject):
    event_id:str
    group_id: str
    notes: str


class ListOfGroupNotesAtEventWithIds(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return GroupNotesAtEventWithIds

    def note_for_event_and_id(self, event_id: str, group_id:str):
        note = get_unique_object_with_multiple_attr_in_list(
            some_list=self,
            dict_of_attributes={
                'event_id': event_id,
                'group_id': group_id
            },
            default=""
        )
        return note

    def update_or_add_note_for_event_and_id(self, event_id: str, group_id:str, notes: str):
        existing_note_idx = get_idx_of_unique_object_with_multiple_attr_in_list(
            some_list=self,
            dict_of_attributes={
                'event_id': event_id,
                'group_id': group_id
            },
            default=missing_data
        )
        if existing_note_idx is missing_data:
            self.append(GroupNotesAtEventWithIds(group_id=group_id,
                                                 event_id=event_id,
                                                 notes=notes))
        else:
            self[existing_note_idx] = GroupNotesAtEventWithIds(group_id=group_id,
                                                 event_id=event_id,
                                                 notes=notes)

