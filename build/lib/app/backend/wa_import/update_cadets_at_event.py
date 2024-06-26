from copy import copy
from typing import List

from app.backend.data.cadets import CadetData

from app.backend.data.group_allocations import GroupAllocationsData
from app.backend.data.dinghies import DinghiesData

from app.objects.utils import union_of_x_and_y

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.constants import NoMoreData, missing_data

from app.backend.cadets import cadet_name_from_id
from app.backend.data.cadets_at_event import  CadetsAtEventData
from app.objects.cadet_at_event import CadetAtEvent
from app.objects.constants import DuplicateCadets
from app.objects.day_selectors import DaySelector, Day
from app.objects.events import Event
from app.objects.mapped_wa_event import RowInMappedWAEvent, MappedWAEvent, R_cancelled_status, R_active_paid_status, \
    R_deleted_status, DEPRECATE_RegistrationStatus


def is_cadet_with_id_already_at_event(interface: abstractInterface, event: Event, cadet_id: str)-> bool:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    return cadets_at_event_data.is_cadet_with_id_already_at_event(cadet_id=cadet_id, event=event)

def is_cadet_with_id_in_identified_list_for_event_data(interface: abstractInterface, event: Event, cadet_id: str)-> bool:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    return cadets_at_event_data.is_cadet_with_id_in_identified_list_for_event(event=event, cadet_id=cadet_id)

def get_all_rows_in_mapped_event_for_cadet_id(interface: abstractInterface, event: Event, cadet_id:str)-> MappedWAEvent:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    relevant_rows = cadets_at_event_data.get_all_rows_in_mapped_event_for_cadet_id(event=event, cadet_id=cadet_id)
    return relevant_rows



def add_new_cadet_to_event(
        interface: abstractInterface,
        event: Event, row_in_mapped_wa_event: RowInMappedWAEvent,
        cadet_id: str
    ):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    cadets_at_event_data.add_new_cadet_to_event(event=event, row_in_mapped_wa_event=row_in_mapped_wa_event, cadet_id=cadet_id)


def get_cadet_at_event_for_cadet_id(interface: abstractInterface, event: Event, cadet_id: str) -> CadetAtEvent:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    return cadets_at_event_data.cadet_at_event_or_missing_data(event=event, cadet_id=cadet_id)



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

    ## Could be length one, or could be longer than one and we're happy with no duplicate

    return all_rows_active_only[0]




def replace_existing_cadet_at_event_where_original_cadet_was_inactive(interface: abstractInterface, event: Event, new_cadet_at_event:CadetAtEvent):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    cadets_at_event_data.replace_existing_cadet_at_event(new_cadet_at_event=new_cadet_at_event, event=event)



def update_status_of_existing_cadet_at_event_to_cancelled_or_deleted(interface: abstractInterface, event: Event, cadet_id:str, new_status: DEPRECATE_RegistrationStatus):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    dinghies_data = DinghiesData(interface.data)
    groups_data = GroupAllocationsData(interface.data)

    cadets_at_event_data.update_status_of_existing_cadet_at_event(event=event, cadet_id=cadet_id, new_status=new_status)


    for day in event.weekdays_in_event():
        remove_partner_and_log_if_present(interface=interface,
                                          event=event,
                                          cadet_id=cadet_id,
                                          day=day)

        dinghies_data.remove_club_boat_allocation_for_cadet_on_day(event =event, cadet_id=cadet_id, day=day)

    dinghies_data.remove_boat_and_partner_for_cadet_at_event(event=event, cadet_id=cadet_id)

    groups_data.remove_cadet_from_data(event=event, cadet_id=cadet_id)

def remove_partner_and_log_if_present(interface: abstractInterface, event: Event, cadet_id: str, day: Day):
    dinghies_data = DinghiesData(interface.data)
    cadets_data = CadetData(interface.data)
    cadet_with_boat_at_event = dinghies_data.get_list_of_cadets_at_event_with_dinghies(
        event).object_with_cadet_id_on_day(cadet_id=cadet_id,
                                           day=day)
    if cadet_with_boat_at_event is missing_data:
        return

    if cadet_with_boat_at_event.has_partner():
        partner_cadet_id = cadet_with_boat_at_event.partner_cadet_id
        partner_name = cadets_data.get_cadet_with_id_(partner_cadet_id).name
        cadet_name = cadets_data.get_cadet_with_id_(cadet_id).name
        dinghies_data.remove_two_handed_partner_link_from_existing_cadet_on_day(
            cadet_id=cadet_id, event=event, day=day
        )
        interface.log_error("Cadet %s was sailing with a partner; now they aren't sailing %s has no partner on %s" % (
            cadet_name, partner_name, day.name
        ))


def update_status_of_existing_cadet_at_event_to_active(interface: abstractInterface, event: Event, cadet_id:str):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    cadets_at_event_data.DEPRECATE_update_status_of_existing_cadet_at_event_to_active_and_paid(event=event, cadet_id=cadet_id)

def make_cadet_available_on_day(interface: abstractInterface, event: Event, cadet_id:str, day: Day):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    cadets_at_event_data.make_cadet_available_on_day(event=event, cadet_id=cadet_id, day=day)


def update_availability_of_existing_cadet_at_event(interface: abstractInterface, event: Event, cadet_id:str, new_availabilty: DaySelector):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    dinghies_data = DinghiesData(interface.data)
    groups_data = GroupAllocationsData(interface.data)

    existing_cadet_at_event = get_cadet_at_event_for_cadet_id(
        interface=interface,
        event=event,
        cadet_id=cadet_id
    )

    existing_availability = copy(existing_cadet_at_event.availability)
    cadets_at_event_data.update_availability_of_existing_cadet_at_event(cadet_id=cadet_id, new_availabilty=new_availabilty, event=event)


    for day in existing_availability.days_available():
        if new_availabilty.available_on_day(day):
            ## Still available no changes
            continue
        print("Cadet_id %s no longer available on day %s" % (cadet_id, day.name))
        remove_partner_and_log_if_present(interface=interface,
                                          event=event,
                                          cadet_id=cadet_id,
                                          day=day)

        print("Removing all dinghies data")
        dinghies_data.remove_boat_and_partner_for_cadet_at_event_on_day(event=event,
                                                                        cadet_id=cadet_id,
                                                                        day=day
                                                                        )
        print("removing club dinghy alloc")
        dinghies_data.remove_club_boat_allocation_for_cadet_on_day(event=event, cadet_id=cadet_id, day=day)

        print("Removing all groups data")
        groups_data.remove_cadet_from_data_on_day(event=event, day=day, cadet_id=cadet_id)



def update_notes_for_existing_cadet_at_event(interface: abstractInterface, event: Event, cadet_id:str, new_notes: str):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    cadets_at_event_data.update_notes_for_existing_cadet_at_event(cadet_id=cadet_id, new_notes=new_notes, event=event)

def update_health_for_existing_cadet_at_event(interface: abstractInterface, event: Event, cadet_id:str, new_health: str):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    cadets_at_event_data.update_health_for_existing_cadet_with_id_at_event(cadet_id=cadet_id, new_health=new_health, event=event)


def update_data_row_for_existing_cadet_at_event(interface: abstractInterface, event: Event, cadet_id:str, new_data_in_row: RowInMappedWAEvent):
    cadets_at_event_data = CadetsAtEventData(interface.data)
    cadets_at_event_data.update_data_row_for_existing_cadet_at_event(event=event, cadet_id=cadet_id, new_data_in_row=new_data_in_row)



def no_important_difference_between_cadets_at_event(
        new_cadet_at_event: CadetAtEvent,
        existing_cadet_at_event: CadetAtEvent
    )-> bool:

    ## only compare availability and status, as that is all WA can update

    status_matches = new_cadet_at_event.status == existing_cadet_at_event.status
    available_matches = new_cadet_at_event.availability == existing_cadet_at_event.availability

    return status_matches and available_matches


NO_STATUS_CHANGE = object()


def new_status_and_status_message(interface: abstractInterface,
                                  new_cadet_at_event: CadetAtEvent,
        existing_cadet_at_event: CadetAtEvent,
                                              ) -> tuple:
    old_status = existing_cadet_at_event.status
    new_status = new_cadet_at_event.status

    if old_status == new_status:
        return new_status, NO_STATUS_CHANGE

    old_status_name = old_status.name
    new_status_name = new_status.name

    cadet = cadet_name_from_id(interface=interface, cadet_id=new_cadet_at_event.cadet_id)

    ## Don't need all shared as new_status can't be deleted
    if old_status == R_cancelled_status and new_status == R_active_paid_status:
        status_message = (
                "Cadet %s was cancelled; now active so probably new registration"
                % str(cadet)
        )

    elif old_status == R_deleted_status and new_status == R_active_paid_status:
        status_message = (
                "Existing cadet %s data was deleted (missing from event spreadsheet); now active so probably manual editing of WA file has occured"
                % str(cadet)
        )

    elif old_status == R_deleted_status and new_status == R_cancelled_status:
        status_message = (
                "Cadet %s was deleted (missing from event spreadsheet); now cancelled so probably manual editing of WA file has occured"
                % str(cadet)
        )

    elif old_status == R_active_paid_status and new_status == R_cancelled_status:
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

def has_cadet_at_event_changed(interface: abstractInterface, cadet_id: str, event: Event) -> bool:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    list_of_cadets_at_event = cadets_at_event_data.get_list_of_cadets_at_event(event)
    cadet = list_of_cadets_at_event.cadet_at_event(cadet_id)

    return cadet.changed


def mark_cadet_at_event_as_unchanged(interface:abstractInterface, cadet_id: str, event: Event):
    cadet_data = CadetsAtEventData(interface.data)
    cadet_data.mark_cadet_at_event_as_unchanged(cadet_id=cadet_id ,event=event)


def list_of_cadet_ids_at_event_and_in_mapped_data_for_event(interface:abstractInterface, event: Event, include_mapped_data: bool = True) -> list:
    cadets_event_data = CadetsAtEventData(interface.data)

    existing_ids = cadets_event_data.list_of_all_cadet_ids_at_event(event)
    if include_mapped_data:
        mapped_ids = cadets_event_data.identified_cadet_ids_in_mapped_data(event)
    else:
        mapped_ids = []

    all_ids = union_of_x_and_y(existing_ids, mapped_ids)

    all_ids.sort() ## MUST be sorted otherwise can go horribly wrong

    return all_ids
