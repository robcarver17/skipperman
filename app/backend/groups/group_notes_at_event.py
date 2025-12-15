from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_notes_for_groups_at_event,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.composed.notes_for_groups import DictOfNotesForGroupsAtEvent
from app.objects.events import Event
from app.objects.groups import Group


def update_group_notes_at_event_for_group(
    object_store: ObjectStore, event: Event, group: Group, notes: str
):
    dict_of_notes = get_dict_of_group_notes_at_event(
        object_store=object_store, event=event
    )
    dict_of_notes.update_group_notes(group=group, notes=notes)
    update_dict_of_group_notes_at_event(
        object_store=object_store, event=event, dict_of_notes=dict_of_notes
    )


def get_dict_of_group_notes_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfNotesForGroupsAtEvent:
    return object_store.DEPRECATE_get(
        object_definition_for_dict_of_notes_for_groups_at_event, event_id=event.id
    )


def update_dict_of_group_notes_at_event(
    object_store: ObjectStore, event: Event, dict_of_notes: DictOfNotesForGroupsAtEvent
):
    object_store.DEPRECATE_update(
        dict_of_notes,
        object_definition=object_definition_for_dict_of_notes_for_groups_at_event,
        event_id=event.id,
    )
