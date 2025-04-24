from app.backend.file_handling import load_spreadsheet_file_and_clear_nans
from app.backend.wild_apricot.load_wa_file import get_event_id_from_wa_df
from app.backend.events.list_of_events import get_event_from_id

from app.objects.events import Event
from app.objects.utilities.exceptions import FileError

from app.objects.wa_event_mapping import ListOfWAEventMaps

from app.data_access.store.object_definitions import (
    object_definition_for_wa_event_mapping,
)
from app.data_access.store.object_store import ObjectStore


def clear_wa_event_id_mapping(object_store: ObjectStore, event: Event):
    wa_mapping_data = get_event_id_mapping_for_wa_files(object_store)
    wa_mapping_data.clear_mapping_for_event(event.id)
    update_event_id_mapping_for_wa_files(
        list_of_wa_event_id_maps=wa_mapping_data, object_store=object_store
    )


def is_event_mapped_with_wa_id(object_store: ObjectStore, event: Event) -> bool:
    wa_mapping_data = get_event_id_mapping_for_wa_files(object_store)
    return wa_mapping_data.is_event_in_mapping_list(event_id=event.id)


def is_wa_id_in_mapping_list(object_store: ObjectStore, wa_id: str) -> bool:
    wa_mapping_data = get_event_id_mapping_for_wa_files(object_store)
    return wa_mapping_data.is_wa_id_in_mapping_list(wa_id)


def get_wa_id_for_event(object_store: ObjectStore, event: Event) -> str:
    wa_mapping_data = get_event_id_mapping_for_wa_files(object_store)
    return wa_mapping_data.get_wa_id_for_event(event.id)


def get_event_id_for_wa_id(object_store: ObjectStore, wa_id: str) -> str:
    wa_mapping_data = get_event_id_mapping_for_wa_files(object_store)
    return wa_mapping_data.get_event_id_for_wa(wa_id)


def verify_file_has_correct_wa_id(
    object_store: ObjectStore,
    filename: str,
    event: Event,
):
    wa_as_df = load_spreadsheet_file_and_clear_nans(filename)

    wa_id = get_event_id_from_wa_df(wa_as_df=wa_as_df)

    __is_new_event_not_used = confirm_correct_wa_mapping_and_return_true_if_new_event(
        object_store=object_store, wa_id=wa_id, event=event
    )


def verify_and_if_required_add_wa_mapping(
    object_store: ObjectStore, filename: str, event: Event
):
    wa_as_df = load_spreadsheet_file_and_clear_nans(filename)
    wa_id = get_event_id_from_wa_df(wa_as_df=wa_as_df)

    is_new_event = confirm_correct_wa_mapping_and_return_true_if_new_event(
        object_store=object_store, wa_id=wa_id, event=event
    )

    # Add the WA/Event id mapping to the relevant table unless we are updating an existing event
    if is_new_event:
        add_wa_to_event_mapping(object_store=object_store, event=event, wa_id=wa_id)


def confirm_correct_wa_mapping_and_return_true_if_new_event(
    object_store: ObjectStore, event: Event, wa_id: str
) -> bool:
    event_id = event.id
    print("WA %s event %s" % (event.id, wa_id))
    event_is_already_in_mapping_list = is_event_mapped_with_wa_id(
        object_store=object_store, event=event
    )
    print("event already in mapping list %s" % str(event_is_already_in_mapping_list))

    if event_is_already_in_mapping_list:
        existing_wa_id = get_wa_id_for_event(event=event, object_store=object_store)
        if existing_wa_id == wa_id:
            ## all fine as expected, and an existing event
            return False
        else:
            raise FileError(
                "Event %s is already mapped to a different existing WA id %s; but imported WA file has id %s - are you sure you have the right file? If you aure sure, then clear the WA ID before retrying."
                % (str(event), existing_wa_id, wa_id)
            )

    wa_event_is_already_in_mapping_list = is_wa_id_in_mapping_list(
        object_store=object_store, wa_id=wa_id
    )
    print(
        "wa event already in mapping list %s" % str(wa_event_is_already_in_mapping_list)
    )

    if wa_event_is_already_in_mapping_list:
        existing_event_id = get_event_id_for_wa_id(
            wa_id=wa_id, object_store=object_store
        )
        if existing_event_id == event_id:
            # existing event mapped correctly - shouldn't get here, but for good order:
            return False
        else:
            other_event = get_event_from_id(
                object_store=object_store, event_id=existing_event_id
            )
            raise FileError(
                "Can't upload file for %s, WA ID %s in file is already mapped to a different existing event %s - are you sure you have the right file?.  If you aure sure, then clear the WA ID for %s before retrying."
                % (event, wa_id, other_event, other_event)
            )

    ## not in eithier list, new mapping
    return True


def add_wa_to_event_mapping(object_store: ObjectStore, event: Event, wa_id: str):
    wa_mapping_data = get_event_id_mapping_for_wa_files(object_store)
    wa_mapping_data.add_event(event_id=event.id, wa_id=wa_id)
    update_event_id_mapping_for_wa_files(
        object_store=object_store, list_of_wa_event_id_maps=wa_mapping_data
    )


def get_event_id_mapping_for_wa_files(object_store: ObjectStore) -> ListOfWAEventMaps:
    return object_store.get(object_definition_for_wa_event_mapping)


def update_event_id_mapping_for_wa_files(
    object_store: ObjectStore, list_of_wa_event_id_maps: ListOfWAEventMaps
):
    object_store.update(
        new_object=list_of_wa_event_id_maps,
        object_definition=object_definition_for_wa_event_mapping,
    )
