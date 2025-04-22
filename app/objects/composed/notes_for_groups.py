from typing import Dict

from app.objects.events import ListOfEvents, Event
from app.objects.group_notes_at_event import ListOfGroupNotesAtEventWithIds
from app.objects.groups import Group, ListOfGroups


class DictOfNotesForGroupsAtEvent(Dict[Group, str]):
    def __init__(self, raw_dict: dict, list_of_group_notes_with_ids: ListOfGroupNotesAtEventWithIds, event: Event):
        self._list_of_group_notes_with_ids = list_of_group_notes_with_ids
        self._event = event
        super().__init__(raw_dict)

    @property
    def event(self) -> Event:
        return self._event

    @property
    def list_of_group_notes_with_ids(self):
        return self._list_of_group_notes_with_ids

    def update_group_notes(self, group: Group, notes: str):
        self[group] = notes
        self.list_of_group_notes_with_ids.update_or_add_note_for_event_and_id(event_id=self.event.id,
                                                                              group_id=group.id,
                                                                              notes=notes)

    def notes_for_group(self, group: Group):
        return self.get(group, "")

def compose_dict_of_notes_for_groups_at_event(
    list_of_group_notes_with_ids: ListOfGroupNotesAtEventWithIds,
        list_of_groups: ListOfGroups,
        list_of_events: ListOfEvents,
        event_id:str
):
    raw_dict = {}
    for item in list_of_group_notes_with_ids:
        if not item.event_id == event_id:
            continue

        group = list_of_groups.group_with_id(item.group_id)
        raw_dict[group] = item.notes

    return DictOfNotesForGroupsAtEvent(raw_dict=raw_dict, list_of_group_notes_with_ids=list_of_group_notes_with_ids, event=list_of_events.event_with_id(event_id))