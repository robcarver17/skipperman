from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_notes_for_groups_at_event,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.group_notes_at_event import DictOfNotesForGroupsAtEvent
from app.objects.events import Event
from app.objects.groups import Group


def update_group_notes_at_event_for_group(
    interface: abstractInterface, event: Event, group: Group, notes: str
):
    interface.update(
        interface.object_store.data_api.data_list_of_group_notes_at_event. update_group_notes_at_event_for_group,
        event_id=event.id,
        group_id=group.id,
        notes=notes
    )


def get_dict_of_group_notes_at_event(
    object_store: ObjectStore, event: Event
) -> DictOfNotesForGroupsAtEvent:
    return object_store.get(
        object_store.data_api.data_list_of_group_notes_at_event.get_dict_of_group_notes_at_event, event_id=event.id)

