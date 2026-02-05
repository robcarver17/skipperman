import os
from typing import List

from app.backend.events.list_of_events import get_sorted_list_of_events
from app.data_access.init_directories import (
    temp_file_name_in_download_directory,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.events import Event, ListOfEvents, SORT_BY_START_DSC
from app.objects.wa_field_mapping import ListOfWAFieldMappings

def get_field_mapping_for_event(
    object_store: ObjectStore, event: Event
) -> ListOfWAFieldMappings:
    return object_store.get(
        object_store.data_api.data_wa_field_mapping.read,
        event_id=event.id
    )


def does_event_already_have_mapping(object_store: ObjectStore, event: Event):
    mapping = get_field_mapping_for_event(object_store=object_store, event=event)

    return len(mapping) > 0


def get_list_of_field_mapping_template_names(object_store: ObjectStore) -> List[str]:
    return object_store.get(object_store.data_api.data_wa_field_mapping_templates.list_of_template_names)


def get_field_mapping_template(
    object_store: ObjectStore, template_name: str
) -> ListOfWAFieldMappings:
    return object_store.get(object_store.data_api.data_wa_field_mapping_templates.read, template_name=template_name)


def save_field_mapping_for_event(
    interface: abstractInterface, event: Event, mapping: ListOfWAFieldMappings
):
    interface.update(
        interface.object_store.data_api.data_wa_field_mapping.write,
        event_id=event.id,
        wa_field_mapping=mapping
    )


def delete_mapping_given_skipperman_field(
    interface: abstractInterface, event: Event, skipperman_field: str
):
    interface.update(
        interface.object_store.data_api.data_wa_field_mapping.delete_mapping_given_skipperman_field,
        event_id=event.id,
        skipperman_field=skipperman_field
    )


def save_new_mapping_pairing(
    interface: abstractInterface, event: Event, skipperman_field: str, wa_field: str
):
    interface.update(
        interface.object_store.data_api.data_wa_field_mapping.save_new_mapping_pairing,
        event_id=event.id,
        skipperman_field=skipperman_field,
        wa_field=wa_field
    )


def save_field_mapping_template(
    interface: abstractInterface, template_name: str, template: ListOfWAFieldMappings
):
    interface.update(
        interface.object_store.data_api.data_wa_field_mapping_templates.write,
        template_name=template_name,
        wa_field_mapping=template
    )



def get_list_of_events_with_field_mapping(
    object_store: ObjectStore, exclude_event: Event
) -> ListOfEvents:
    list_of_events = get_sorted_list_of_events(
        object_store=object_store, sort_by=SORT_BY_START_DSC
    )
    list_of_events = [
        event
        for event in list_of_events
        if does_event_already_have_mapping(
            object_store=object_store, event=event
        )
    ]
    list_of_events = [
        event for event in list_of_events if not event.id == exclude_event.id
    ]

    return ListOfEvents(list_of_events)


def write_mapping_to_temp_csv_file_and_return_filename(
    mapping: ListOfWAFieldMappings, filename: str = "temp_mapping_file"
) -> str:
    df = mapping.as_df_of_str()
    filename = temp_file_name_in_download_directory(filename, extension=".csv")

    df.to_csv(filename, index=False)

    return filename

