from typing import List

from app.data_access.store.object_definitions import (
    object_definition_for_field_mappings_at_event, object_definition_for_list_of_field_mapping_templates,
    object_definition_for_field_mapping_templates,
)
from app.data_access.store.object_store import ObjectStore
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.events import Event
from app.objects.wa_field_mapping import ListOfWAFieldMappings


def save_field_mapping_for_event(
    object_store: ObjectStore, event: Event, mapping: ListOfWAFieldMappings):
    return object_store.update(
        object_definition_for_field_mappings_at_event, event_id=event.id,
        new_object=mapping
    )

def get_field_mapping_for_event(
    object_store: ObjectStore, event: Event
) -> ListOfWAFieldMappings:
    return object_store.get(
        object_definition_for_field_mappings_at_event, event_id=event.id
    )


def does_event_already_have_mapping(object_store: ObjectStore, event: Event):
    try:
        mapping = get_field_mapping_for_event(
            object_store=object_store, event=event
        )
        assert len(mapping) > 0
        return True
    except:
        return False


def get_list_of_field_mapping_template_names(object_store: ObjectStore) -> List[str]:
    return object_store.get(object_definition = object_definition_for_list_of_field_mapping_templates)

def get_field_mapping_template(object_store: ObjectStore, template_name: str) -> ListOfWAFieldMappings:
    return object_store.get(object_definition = object_definition_for_field_mapping_templates, template_name=template_name)

def save_field_mapping_template(object_store: ObjectStore, template_name: str, template: ListOfWAFieldMappings):
    return object_store.update(object_definition = object_definition_for_field_mapping_templates, template_name=template_name,
                            new_object=template)
