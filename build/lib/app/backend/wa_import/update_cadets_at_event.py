from app.backend.cadets import cadet_name_from_id
from app.backend.data.mapped_events import load_mapped_wa_event
from app.backend.data.cadets_at_event import load_cadets_at_event, save_cadets_at_event, load_identified_cadets_at_event
from app.backend.data.cadets_at_event import load_identified_cadets_at_event
from app.objects.cadet_at_event import CadetAtEvent, get_cadet_at_event_from_row_in_mapped_event
from app.objects.constants import DuplicateCadets, missing_data
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects.mapped_wa_event import RowInMappedWAEvent, MappedWAEvent, cancelled_status, active_status, \
    deleted_status, RegistrationStatus


def list_of_cadet_ids_in_mapped_event(event: Event):
    identified_cadets = load_identified_cadets_at_event(event)
    mapped_data = load_mapped_wa_event(event)

    list_of_cadets_ids = [identified_cadets.cadet_id_given_row_id(row_id) for row_id in mapped_data.list_of_row_ids()]

    return list_of_cadets_ids

def is_cadet_already_at_event(event: Event, cadet_id: str)-> bool:
    at_event = load_cadets_at_event(event)

    return cadet_id in at_event.list_of_cadet_ids()

def is_cadet_in_mapped_data(event: Event, cadet_id: str)-> bool:
    list_of_ids = list_of_cadet_ids_in_mapped_event(event)

    return cadet_id in list_of_ids

def get_row_in_mapped_event_for_cadet_id_active_registration_only(event: Event, cadet_id:str)-> RowInMappedWAEvent:
    all_rows = get_all_rows_in_mapped_event_for_cadet_id(event=event, cadet_id=cadet_id)
    all_rows_active_only = all_rows.active_registrations_only()
    if len(all_rows_active_only)==0:
        return missing_data
    if len(all_rows_active_only)>1:
        raise DuplicateCadets
    else:
        return all_rows_active_only[0]

def get_all_rows_in_mapped_event_for_cadet_id(event: Event, cadet_id:str)-> MappedWAEvent:
    identified_cadets = load_identified_cadets_at_event(event)
    mapped_data = load_mapped_wa_event(event)

    list_of_row_ids = identified_cadets.list_of_row_ids_matching_cadet_id(cadet_id)
    relevant_rows =mapped_data.subset_with_id(list_of_row_ids)
    return relevant_rows

def add_new_cadet_to_event(
        event: Event, row_in_mapped_wa_event: RowInMappedWAEvent,
        cadet_id: str
    ):
    cadet_at_event = get_cadet_at_event_from_row_in_mapped_event(event=event, cadet_id=cadet_id, row_in_mapped_wa_event=row_in_mapped_wa_event)

    existing_cadets_at_event = load_cadets_at_event(event)
    existing_cadets_at_event.add(cadet_at_event)
    save_cadets_at_event(event=event, list_of_cadets_at_event=existing_cadets_at_event)

def get_cadet_at_event_for_cadet_id(event: Event, cadet_id: str) -> CadetAtEvent:
    existing_cadets_at_event = load_cadets_at_event(event)
    return existing_cadets_at_event.cadet_at_event_or_missing_data(cadet_id)

def mark_cadet_at_event_as_deleted(event: Event, cadet_id: str):
    existing_cadets_at_event = load_cadets_at_event(event)
    existing_cadets_at_event.mark_cadet_as_deleted(cadet_id)
    existing_cadets_at_event.mark_cadet_as_changed(cadet_id)
    save_cadets_at_event(event=event, list_of_cadets_at_event=existing_cadets_at_event)

def get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(event: Event, cadet_id: str) -> RowInMappedWAEvent:
    all_rows = get_all_rows_in_mapped_event_for_cadet_id(event=event, cadet_id=cadet_id)
    all_rows_active_only = all_rows.active_registrations_only()

    ## ideally want an active row
    if len(all_rows_active_only)==1:
        return all_rows_active_only[0]
    if len(all_rows_active_only)>1:
        raise DuplicateCadets

    ## must have cancelled only
    ## if multiple cancellations (bit weird!) doesn't matter but return first

    return all_rows[0]


def replace_existing_cadet_at_event(event: Event, new_cadet_at_event:CadetAtEvent):
    existing_cadets_at_event = load_cadets_at_event(event)
    existing_cadets_at_event.replace_existing_cadet_at_event(new_cadet_at_event)
    save_cadets_at_event(event=event, list_of_cadets_at_event=existing_cadets_at_event)

def update_status_of_existing_cadet_at_event(event: Event, cadet_id:str, new_status: RegistrationStatus):
    existing_cadets_at_event = load_cadets_at_event(event)
    existing_cadets_at_event.update_status_of_existing_cadet_at_event(cadet_id=cadet_id, new_status=new_status)
    save_cadets_at_event(event=event, list_of_cadets_at_event=existing_cadets_at_event)

def update_availability_of_existing_cadet_at_event(event: Event, cadet_id:str, new_availabilty: DaySelector):
    existing_cadets_at_event = load_cadets_at_event(event)
    existing_cadets_at_event.update_availability_of_existing_cadet_at_event(cadet_id=cadet_id, new_availabilty=new_availabilty)
    save_cadets_at_event(event=event, list_of_cadets_at_event=existing_cadets_at_event)

def update_notes_for_existing_cadet_at_event(event: Event, cadet_id:str, new_notes: str):
    existing_cadets_at_event = load_cadets_at_event(event)
    existing_cadets_at_event.update_notes_for_existing_cadet_at_event(cadet_id=cadet_id, new_notes=new_notes)
    save_cadets_at_event(event=event, list_of_cadets_at_event=existing_cadets_at_event)

def update_data_row_for_existing_cadet_at_event(event: Event, cadet_id:str, new_data_in_row: RowInMappedWAEvent):
    existing_cadets_at_event = load_cadets_at_event(event)
    existing_cadets_at_event.update_data_row_for_existing_cadet_at_event(cadet_id=cadet_id, new_data_in_row=new_data_in_row)
    save_cadets_at_event(event=event, list_of_cadets_at_event=existing_cadets_at_event)


def any_important_difference_between_cadets_at_event(
        new_cadet_at_event: CadetAtEvent,
        existing_cadet_at_event: CadetAtEvent
    )-> bool:

    ## only compare availability and status, as that is all WA can update

    status_matches = new_cadet_at_event.status == existing_cadet_at_event.status
    available_matches = new_cadet_at_event.availability == existing_cadet_at_event.availability

    if status_matches and available_matches:
        return False
    else:
        return True


NO_STATUS_CHANGE = object()


def new_status_and_status_message(        new_cadet_at_event: CadetAtEvent,
        existing_cadet_at_event: CadetAtEvent,
                                              ) -> tuple:
    old_status = existing_cadet_at_event.status
    new_status = new_cadet_at_event.status

    if old_status == new_status:
        return new_status, NO_STATUS_CHANGE

    old_status_name = old_status.name
    new_status_name = new_status.name

    cadet = cadet_name_from_id(new_cadet_at_event.cadet_id)

    ## Don't need all shared as new_status can't be deleted
    if old_status == cancelled_status and new_status == active_status:
        status_message = (
                "Cadet %s was cancelled; now active so probably new registration"
                % str(cadet)
        )

    elif old_status == deleted_status and new_status == active_status:
        status_message = (
                "Existing cadet %s data was deleted (missing from event spreadsheet); now active so probably manual editing of WA file has occured"
                % str(cadet)
        )

    elif old_status == deleted_status and new_status == cancelled_status:
        status_message = (
                "Cadet %s was deleted (missing from event spreadsheet); now cancelled so probably manual editing of WA file has occured"
                % str(cadet)
        )

    elif old_status == active_status and new_status == cancelled_status:
        status_message = (
                "Cadet %s was active now cancelled, so probably cancelled on WA website"
                % str(cadet)
        )
    else:
        status_message = (
                "Cadet %s status change from %s to %s, shouldn't happen! Check very carefully"
                % (str(cadet), old_status_name, new_status_name)
        )

    return new_status, status_message

def has_cadet_at_event_changed(cadet_id: str, event: Event) -> bool:
    list_of_cadets_at_event = load_cadets_at_event(event)
    cadet = list_of_cadets_at_event.cadet_at_event(cadet_id)

    return cadet.changed

def mark_cadet_at_event_as_unchanged(cadet_id: str, event: Event):
    list_of_cadets_at_event = load_cadets_at_event(event)
    list_of_cadets_at_event.mark_cadet_as_unchanged(cadet_id)
    save_cadets_at_event(list_of_cadets_at_event=list_of_cadets_at_event, event=event)


def cadet_ids_in_mapped_data(event: Event) -> list:
    identified_cadets = load_identified_cadets_at_event(event)
    mapped_event = load_mapped_wa_event(event)

    row_ids = mapped_event.list_of_row_ids()
    list_of_cadet_ids = [identified_cadets.cadet_id_given_row_id(row_id) for row_id in row_ids]

    return list_of_cadet_ids
