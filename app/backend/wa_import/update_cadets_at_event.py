from typing import List

from app.objects.utils import union_of_x_and_y

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.constants import missing_data, NoMoreData

from app.backend.cadets import DEPRECATED_cadet_name_from_id
from app.backend.data.mapped_events import DEPRECATE_load_mapped_wa_event, MappedEventsData
from app.backend.data.cadets_at_event import DEPRECATED_load_cadets_at_event, save_cadets_at_event, CadetsAtEventData
from app.backend.data.cadets_at_event import DEPERCATE_load_identified_cadets_at_event
from app.objects.cadet_at_event import CadetAtEvent, get_cadet_at_event_from_row_in_mapped_event
from app.objects.constants import DuplicateCadets, missing_data
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects.mapped_wa_event import RowInMappedWAEvent, MappedWAEvent, cancelled_status, active_status, \
    deleted_status, RegistrationStatus


def list_of_cadet_ids_in_mapped_event(event: Event):
    identified_cadets = DEPERCATE_load_identified_cadets_at_event(event)
    mapped_data = DEPRECATE_load_mapped_wa_event(event)

    list_of_cadets_ids = [identified_cadets.cadet_id_given_row_id(row_id) for row_id in mapped_data.list_of_row_ids()]

    return list_of_cadets_ids

def is_cadet_with_id_already_at_event(interface: abstractInterface, event: Event, cadet_id: str)-> bool:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    return cadets_at_event_data.is_cadet_with_id_already_at_event(cadet_id=cadet_id, event=event)

def is_cadet_with_id_in_identified_list_for_event_data(interface: abstractInterface, event: Event, cadet_id: str)-> bool:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    return cadets_at_event_data.is_cadet_with_id_in_identified_list_for_event(event=event, cadet_id=cadet_id)

def get_row_in_mapped_event_for_cadet_id_active_registration_only(event: Event, cadet_id:str)-> RowInMappedWAEvent:
    all_rows = DEPRECATED_get_all_rows_in_mapped_event_for_cadet_id(event=event, cadet_id=cadet_id)
    all_rows_active_only = all_rows.active_registrations_only()
    if len(all_rows_active_only)==0:
        return missing_data
    if len(all_rows_active_only)>1:
        raise DuplicateCadets
    else:
        return all_rows_active_only[0]

def DEPRECATED_get_all_rows_in_mapped_event_for_cadet_id(event: Event, cadet_id:str)-> MappedWAEvent:
    identified_cadets = DEPERCATE_load_identified_cadets_at_event(event)
    mapped_data = DEPRECATE_load_mapped_wa_event(event)

    list_of_row_ids = identified_cadets.list_of_row_ids_given_cadet_id(cadet_id)
    relevant_rows =mapped_data.subset_with_id(list_of_row_ids)
    return relevant_rows

def get_all_rows_in_mapped_event_for_cadet_id(interface: abstractInterface, event: Event, cadet_id:str)-> MappedWAEvent:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    relevant_rows = cadets_at_event_data.get_all_rows_in_mapped_event_for_cadet_id(event=event, cadet_id=cadet_id)
    return relevant_rows


def DEPRECATE_add_new_cadet_to_event(
        event: Event, row_in_mapped_wa_event: RowInMappedWAEvent,
        cadet_id: str
    ):
    cadet_at_event = get_cadet_at_event_from_row_in_mapped_event(event=event, cadet_id=cadet_id, row_in_mapped_wa_event=row_in_mapped_wa_event)

    existing_cadets_at_event = DEPRECATED_load_cadets_at_event(event)
    existing_cadets_at_event.add(cadet_at_event)
    save_cadets_at_event(event=event, list_of_cadets_at_event=existing_cadets_at_event)


def add_new_cadet_to_event(
        interface: abstractInterface,
        event: Event, row_in_mapped_wa_event: RowInMappedWAEvent,
        cadet_id: str
    ):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    cadets_at_event_data.add_new_cadet_to_event(event=event, row_in_mapped_wa_event=row_in_mapped_wa_event, cadet_id=cadet_id)


def DEPRECATE_get_cadet_at_event_for_cadet_id(event: Event, cadet_id: str) -> CadetAtEvent:
    existing_cadets_at_event = DEPRECATED_load_cadets_at_event(event)
    return existing_cadets_at_event.cadet_at_event_or_missing_data(cadet_id)

def get_cadet_at_event_for_cadet_id(interface: abstractInterface, event: Event, cadet_id: str) -> CadetAtEvent:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    return cadets_at_event_data.cadet_at_event_or_missing_data(event=event, cadet_id=cadet_id)


def DEPRECATED_get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(event: Event, cadet_id: str) -> RowInMappedWAEvent:
    all_rows = DEPRECATED_get_all_rows_in_mapped_event_for_cadet_id(event=event, cadet_id=cadet_id)
    all_rows_active_only = all_rows.active_registrations_only()

    ## ideally want an active row
    if len(all_rows_active_only)==1:
        return all_rows_active_only[0]
    if len(all_rows_active_only)>1:
        raise DuplicateCadets

    ## must have cancelled only
    ## if multiple cancellations (bit weird!) doesn't matter but return first

    return all_rows[0]


def get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(
        interface: abstractInterface,
        event: Event, cadet_id: str,
        raise_error_on_duplicate: bool = True) -> RowInMappedWAEvent:

    all_rows = get_all_rows_in_mapped_event_for_cadet_id(event=event, cadet_id=cadet_id, interface=interface)
    if len(all_rows)==0:
        raise NoMoreData("No cadets with ID %s in mapped event data" % cadet_id)

    all_rows_active_only = all_rows.active_registrations_only()
    if len(all_rows_active_only)==0:
        ## must have cancelled only
        ## if multiple cancellations (bit weird!) doesn't matter but return first
        return all_rows[0]

    ## ideally want an active row, just one
    if len(all_rows_active_only)>1 and raise_error_on_duplicate:
        raise DuplicateCadets

    return all_rows_active_only[0]




def replace_existing_cadet_at_event(interface: abstractInterface, event: Event, new_cadet_at_event:CadetAtEvent):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    cadets_at_event_data.replace_existing_cadet_at_event(new_cadet_at_event=new_cadet_at_event, event=event)

def DEPRECATED_update_status_of_existing_cadet_at_event(event: Event, cadet_id:str, new_status: RegistrationStatus):
    existing_cadets_at_event = DEPRECATED_load_cadets_at_event(event)
    existing_cadets_at_event.update_status_of_existing_cadet_at_event(cadet_id=cadet_id, new_status=new_status)
    save_cadets_at_event(event=event, list_of_cadets_at_event=existing_cadets_at_event)

def update_status_of_existing_cadet_at_event_to_cancelled_or_deleted(interface: abstractInterface, event: Event, cadet_id:str, new_status: RegistrationStatus):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    cadets_at_event_data.update_status_of_existing_cadet_at_event_to_cancelled_or_deleted(event=event, cadet_id=cadet_id, new_status=new_status)

def DEPRECATED_update_availability_of_existing_cadet_at_event(event: Event, cadet_id:str, new_availabilty: DaySelector):
    existing_cadets_at_event = DEPRECATED_load_cadets_at_event(event)
    existing_cadets_at_event.update_availability_of_existing_cadet_at_event(cadet_id=cadet_id, new_availabilty=new_availabilty)
    save_cadets_at_event(event=event, list_of_cadets_at_event=existing_cadets_at_event)


def update_availability_of_existing_cadet_at_event(interface: abstractInterface, event: Event, cadet_id:str, new_availabilty: DaySelector):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    cadets_at_event_data.update_availability_of_existing_cadet_at_event(cadet_id=cadet_id, new_availabilty=new_availabilty, event=event)

def update_notes_for_existing_cadet_at_event(event: Event, cadet_id:str, new_notes: str):
    existing_cadets_at_event = DEPRECATED_load_cadets_at_event(event)
    existing_cadets_at_event.update_notes_for_existing_cadet_at_event(cadet_id=cadet_id, new_notes=new_notes)
    save_cadets_at_event(event=event, list_of_cadets_at_event=existing_cadets_at_event)

def update_data_row_for_existing_cadet_at_event(event: Event, cadet_id:str, new_data_in_row: RowInMappedWAEvent):
    existing_cadets_at_event = DEPRECATED_load_cadets_at_event(event)
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

    cadet = DEPRECATED_cadet_name_from_id(new_cadet_at_event.cadet_id)

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
    list_of_cadets_at_event = DEPRECATED_load_cadets_at_event(event)
    cadet = list_of_cadets_at_event.cadet_at_event(cadet_id)

    return cadet.changed

def mark_cadet_at_event_as_unchanged(cadet_id: str, event: Event):
    list_of_cadets_at_event = DEPRECATED_load_cadets_at_event(event)
    list_of_cadets_at_event.mark_cadet_as_unchanged(cadet_id)
    save_cadets_at_event(list_of_cadets_at_event=list_of_cadets_at_event, event=event)



def list_of_cadet_ids_at_event_and_in_mapped_data_for_event(interface:abstractInterface, event: Event) -> list:
    cadets_event_data = CadetsAtEventData(interface.data)

    existing_ids = cadets_event_data.identified_cadet_ids_in_mapped_data(event)
    mapped_ids = cadets_event_data.identified_cadet_ids_in_mapped_data(event)

    all_ids = union_of_x_and_y(existing_ids, mapped_ids)
    all_ids.sort() ## MUST be sorted otherwise can go horribly wrong

    return all_ids
