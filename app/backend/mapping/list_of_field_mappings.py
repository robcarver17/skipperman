import os
from typing import List

from app.backend.events.list_of_events import get_sorted_list_of_events
from app.data_access.init_directories import download_directory
from app.data_access.store.object_definitions import (
    object_definition_for_field_mappings_at_event,
    object_definition_for_list_of_field_mapping_templates,
    object_definition_for_field_mapping_templates,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.events import Event, ListOfEvents, SORT_BY_START_DSC
from app.objects.wa_field_mapping import ListOfWAFieldMappings


def is_wa_field_mapping_setup_for_event(
    object_store: ObjectStore, event: Event
) -> bool:
    mapping = get_field_mapping_for_event(object_store=object_store, event=event)

    return len(mapping) > 0


def save_field_mapping_for_event(
    object_store: ObjectStore, event: Event, mapping: ListOfWAFieldMappings
):
    return object_store.update(
        object_definition=object_definition_for_field_mappings_at_event,
        event_id=event.id,
        new_object=mapping,
    )


def get_field_mapping_for_event(
    object_store: ObjectStore, event: Event
) -> ListOfWAFieldMappings:
    return object_store.get(
        object_definition_for_field_mappings_at_event, event_id=event.id
    )


def does_event_already_have_mapping(object_store: ObjectStore, event: Event):
    try:
        mapping = get_field_mapping_for_event(object_store=object_store, event=event)
        assert len(mapping) > 0
        return True
    except:
        return False


def get_list_of_field_mapping_template_names(object_store: ObjectStore) -> List[str]:
    return object_store.get(
        object_definition=object_definition_for_list_of_field_mapping_templates
    )


def get_field_mapping_template(
    object_store: ObjectStore, template_name: str
) -> ListOfWAFieldMappings:
    return object_store.get(
        object_definition=object_definition_for_field_mapping_templates,
        template_name=template_name,
    )


def save_field_mapping_template(
    object_store: ObjectStore, template_name: str, template: ListOfWAFieldMappings
):
    return object_store.update(
        object_definition=object_definition_for_field_mapping_templates,
        template_name=template_name,
        new_object=template,
    )


def get_list_of_events_with_field_mapping(
    interface: abstractInterface, exclude_event: Event
) -> ListOfEvents:
    list_of_events = get_sorted_list_of_events(
        object_store=interface.object_store, sort_by=SORT_BY_START_DSC
    )
    list_of_events = [
        event
        for event in list_of_events
        if is_wa_field_mapping_setup_for_event(
            object_store=interface.object_store, event=event
        )
    ]
    list_of_events = [
        event for event in list_of_events if not event.id == exclude_event.id
    ]

    return ListOfEvents(list_of_events)


def write_mapping_to_temp_csv_file_and_return_filename(
    mapping: ListOfWAFieldMappings,
) -> str:
    df = mapping.as_df_of_str()
    filename = temp_mapping_file_name()

    df.to_csv(filename, index=False)

    return filename


def temp_mapping_file_name() -> str:
    return os.path.join(download_directory, "temp_mapping_file.csv")


def delete_mapping_given_skipperman_field(object_store: ObjectStore, event: Event, skipperman_field:str):

    mapping = get_field_mapping_for_event(object_store=object_store, event=event)
    mapping.delete_mapping(skipperman_field)
    save_field_mapping_for_event(object_store=object_store, event=event, mapping=mapping)

def save_new_mapping_pairing(object_store: ObjectStore, event: Event, skipperman_field: str,
                             wa_field: str):
    mapping = get_field_mapping_for_event(object_store=object_store, event=event)
    mapping.add_new_mapping(skipperman_field=skipperman_field, wa_field=wa_field)
    save_field_mapping_for_event(object_store=object_store, event=event, mapping=mapping)