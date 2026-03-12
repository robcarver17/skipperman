from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.cadets import Cadet

from app.objects.cadet_with_id_at_event import CadetWithIdAtEvent
from app.objects.events import Event


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
    elif old_status.is_cancelled_no_refund and new_status.is_active:
        status_message = (
            "Sailor %s was cancelled with no refund; WA doesn't know about cancellation and Skipperman does know. You should probably keep the status to Cancelled No Refund."
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
    interface: abstractInterface, event: Event, new_cadet_at_event: CadetWithIdAtEvent
):
    interface.update(
        interface.object_store.data_api.data_cadets_at_event.replace_existing_cadet_at_event_where_original_cadet_was_inactive,
        event_id=event.id,
        new_cadet_at_event=new_cadet_at_event,
    )


def update_notes_for_existing_cadet_at_event(
    interface: abstractInterface, event: Event, cadet: Cadet, new_notes: str
):
    interface.update(
        interface.object_store.data_api.data_cadets_at_event.update_notes_for_existing_cadet_at_event,
        event_id=event.id,
        cadet_id=cadet.id,
        new_notes=new_notes,
    )


def update_health_for_existing_cadet_at_event(
    interface: abstractInterface, event: Event, cadet: Cadet, new_health: str
):
    interface.update(
        interface.object_store.data_api.data_cadets_at_event.update_health_for_existing_cadet_at_event,
        event_id=event.id,
        cadet_id=cadet.id,
        new_health=new_health,
    )


def update_data_row_for_existing_cadet_at_event(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    column_name: str,
    new_value_for_column,
):
    interface.update(
        interface.object_store.data_api.data_cadets_at_event.update_row_in_registration_data_for_existing_cadet_at_event,
        event_id=event.id,
        cadet_id=cadet.id,
        column_name=column_name,
        new_value_for_column=new_value_for_column,
    )
