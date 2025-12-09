from app.backend.cadets_at_event.dict_of_all_cadet_at_event_data import (
    get_dict_of_all_event_info_for_cadets,
    update_dict_of_all_event_info_for_cadets,
)
from app.data_access.store.object_store import ObjectStore

from app.objects.cadets import Cadet

from app.objects.cadet_with_id_at_event import CadetWithIdAtEvent
from app.objects.events import Event
from app.objects.registration_data import RowInRegistrationData
from app.backend.registration_data.cadet_registration_data import (
    get_list_of_cadets_with_id_and_registration_data_at_event,
    update_list_of_cadets_with_id_and_registration_data_at_event,
)


def no_important_difference_between_cadets_at_event(
    new_cadet_at_event_data: CadetWithIdAtEvent,
    existing_cadet_at_event_data: CadetWithIdAtEvent,
) -> bool:
    ## only compare availability and status, as that is all WA can update

    status_matches = (
        new_cadet_at_event_data.status == existing_cadet_at_event_data.status
    )
    available_matches = (
        new_cadet_at_event_data.availability
        == existing_cadet_at_event_data.availability
    )

    return status_matches and available_matches


def registration_replacing_manual(
    new_cadet_at_event_data: CadetWithIdAtEvent,
    existing_cadet_at_event_data: CadetWithIdAtEvent,
) -> bool:
    status_matches = (
        new_cadet_at_event_data.status == existing_cadet_at_event_data.status
    )

    if status_matches:
        return False

    if new_cadet_at_event_data.status.is_active:
        if existing_cadet_at_event_data.status.is_manual:
            return True

    return False


NO_STATUS_CHANGE = object()


def new_status_and_status_message(
    cadet: Cadet,
    new_cadet_at_event_data: CadetWithIdAtEvent,
    existing_cadet_at_event_data: CadetWithIdAtEvent,
) -> tuple:
    old_status = existing_cadet_at_event_data.status
    new_status = new_cadet_at_event_data.status

    if old_status == new_status:
        return new_status, NO_STATUS_CHANGE

    old_status_name = old_status.name
    new_status_name = new_status.name

    ## Don't need all shared as new_status can't be deleted
    if old_status.is_cancelled and new_status.is_active:
        status_message = (
            "Sailor %s was cancelled; now active so probably new registration replacing the existing cancelled one"
            % str(cadet)
        )

    elif old_status.is_deleted and new_status.is_active:
        status_message = (
            "Existing sailor %s data was deleted (missing from event spreadsheet); now active so probably manual editing of import file has occured"
            % str(cadet)
        )

    elif old_status.is_deleted and new_status.is_cancelled:
        status_message = (
            "Sailor %s was deleted (missing from event spreadsheet); now cancelled so probably manual editing of import file has occured"
            % str(cadet)
        )

    elif old_status.is_active and new_status.is_cancelled:
        status_message = (
            "Sailor %s was active now cancelled, so probably cancelled in original data"
            % str(cadet)
        )
    elif old_status.is_active and new_status.is_active:
        status_message = (
            "Sailor %s is still active but status has changed from %s to %s"
            % (str(cadet), old_status_name, new_status_name)
        )
    else:
        status_message = (
            "Sailor %s status change from %s to %s, shouldn't happen! Check the registration very carefully!"
            % (str(cadet), old_status_name, new_status_name)
        )

    return new_status, status_message


def replace_existing_cadet_at_event_where_original_cadet_was_inactive(
    object_store: ObjectStore, event: Event, new_cadet_at_event: CadetWithIdAtEvent
):
    list_of_cadets_with_id_at_event = (
        get_list_of_cadets_with_id_and_registration_data_at_event(
            object_store=object_store, event=event
        )
    )
    list_of_cadets_with_id_at_event.replace_existing_cadet_at_event(
        new_cadet_at_event=new_cadet_at_event
    )
    update_list_of_cadets_with_id_and_registration_data_at_event(
        object_store=object_store,
        event=event,
        list_of_cadets_with_id_at_event=list_of_cadets_with_id_at_event,
    )


def update_notes_for_existing_cadet_at_event(
    object_store: ObjectStore, event: Event, cadet: Cadet, new_notes: str
):
    dict_of_all_event_data = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)
    dict_of_all_event_data.update_notes_for_existing_cadet_at_event(
        cadet=cadet, notes=new_notes
    )
    update_dict_of_all_event_info_for_cadets(
        object_store=object_store,
        dict_of_all_event_info_for_cadets=dict_of_all_event_data,
    )


def update_health_for_existing_cadet_at_event(
    object_store: ObjectStore, event: Event, cadet: Cadet, new_health: str
):
    dict_of_all_event_data = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)
    dict_of_all_event_data.update_health_for_existing_cadet_at_event(
        cadet=cadet, new_health=new_health
    )
    update_dict_of_all_event_info_for_cadets(
        object_store=object_store,
        dict_of_all_event_info_for_cadets=dict_of_all_event_data,
    )


def update_data_row_for_existing_cadet_at_event(
    object_store: ObjectStore,
    event: Event,
    cadet: Cadet,
    column_name: str,
    new_value_for_column,
):
    dict_of_all_event_data = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event)
    dict_of_all_event_data.update_data_row_for_existing_cadet_at_event(
        cadet=cadet, column_name=column_name, new_value_for_column=new_value_for_column
    )
    update_dict_of_all_event_info_for_cadets(
        object_store=object_store,
        dict_of_all_event_info_for_cadets=dict_of_all_event_data,
    )
