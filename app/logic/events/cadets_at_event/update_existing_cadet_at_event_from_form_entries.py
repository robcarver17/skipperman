from typing import Tuple

from app.backend.forms.form_utils import get_availablity_from_form, get_status_from_form
from app.backend.wa_import.update_cadets_at_event import \
    replace_existing_cadet_at_event_where_original_cadet_was_inactive, \
    get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active, \
    update_status_of_existing_cadet_at_event_to_cancelled_or_deleted, update_availability_of_existing_cadet_at_event, \
    get_cadet_at_event_for_cadet_id
from app.logic.events.constants import ROW_STATUS, ATTENDANCE
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.cadets_at_event.track_cadet_id_in_state_when_importing import get_current_cadet_id_at_event
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadet_at_event import CadetAtEvent, get_cadet_at_event_from_row_in_mapped_event
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects.mapped_wa_event import RegistrationStatus, cancelled_status, active_status, deleted_status


def update_cadets_at_event_with_form_data(interface: abstractInterface):
    new_cadet_at_event = get_new_cadet_from_mapped_event_and_optionally_form(interface, use_form_data=True)
    update_cadets_at_event(interface=interface, new_cadet_at_event=new_cadet_at_event)

def update_cadets_at_event_with_new_data(interface: abstractInterface):
    new_cadet_at_event = get_new_cadet_from_mapped_event_and_optionally_form(interface, use_form_data=False)
    update_cadets_at_event(interface=interface, new_cadet_at_event=new_cadet_at_event)

def update_cadets_at_event(interface: abstractInterface, new_cadet_at_event: CadetAtEvent):
    event = get_event_from_state(interface)
    existing_cadet_at_event = get_existing_cadet_at_event_from_state(interface)

    original_status = existing_cadet_at_event.status

    new_status = new_cadet_at_event.status

    was_cancelled = original_status in [cancelled_status, deleted_status]

    new_registration_replacing_deleted_or_cancelled = was_cancelled and new_status == active_status
    existing_registration_now_deleted_or_cancelled = new_status in [deleted_status, cancelled_status]
    status_unchanged = new_status == original_status

    if new_registration_replacing_deleted_or_cancelled:
        ## Replace entire original cadet, new registration
        replace_existing_cadet_at_event_where_original_cadet_was_inactive(interface=interface, event=event, new_cadet_at_event = new_cadet_at_event)

    elif existing_registration_now_deleted_or_cancelled:
        ## availability is a moot point
        update_status_of_existing_cadet_at_event_to_cancelled_or_deleted(interface=interface, event=event, new_status = new_status,
                                                                         cadet_id=new_cadet_at_event.cadet_id)

    elif status_unchanged:
        ## Must be an availability change
        update_cadet_at_event_when_status_unchanged(interface=interface, event=event, new_cadet_at_event=new_cadet_at_event, existing_cadet_at_event=existing_cadet_at_event)

    else:
        interface.log_error("For existing cadet %s status change from %s to %s don't know how to handle" % (str(new_cadet_at_event),
                                                                                                       original_status.name, new_status.name))

    interface._DONT_CALL_DIRECTLY_USE_FLUSH_save_stored_items()
    interface._DONT_CALL_DIRECTLY_USE_FLUSH_clear_stored_items()

def update_cadet_at_event_when_status_unchanged(interface: abstractInterface,
                                         event: Event, new_cadet_at_event: CadetAtEvent,
                                         existing_cadet_at_event: CadetAtEvent):

    original_availability = existing_cadet_at_event.availability
    new_availability = new_cadet_at_event.availability

    availability_unchanged = new_availability == original_availability

    if availability_unchanged:
        ## Neithier status or availability has changed - shouldn't happen, but heigh ho
        print(
            "Code identified major change for cadet %s but nothing appears to have happened, probably user entering original values in form for some reason" % str(existing_cadet_at_event))
        return

    days_available = event.days_in_event_overlap_with_selected_days(new_availability)
    if len(days_available)==0:
        interface.log_error("For existing cadet %s you haven't selected any available days - not making any changes, instead consider manually cancelling in registration data" % str(existing_cadet_at_event))
        return

    update_availability_of_existing_cadet_at_event(interface=interface, event=event,
                                                   new_availabilty=new_availability,
                                                   cadet_id=existing_cadet_at_event.cadet_id)


def get_existing_cadet_at_event_from_state(interface: abstractInterface) -> CadetAtEvent:
    event = get_event_from_state(interface)
    cadet_id = get_current_cadet_id_at_event(interface)

    existing_cadet_at_event = get_cadet_at_event_for_cadet_id(
        interface=interface,
        event=event,
        cadet_id=cadet_id
    )

    return existing_cadet_at_event

def get_new_cadet_from_mapped_event_and_optionally_form(interface: abstractInterface, use_form_data: bool = False) -> CadetAtEvent:
    event = get_event_from_state(interface)
    cadet_id = get_current_cadet_id_at_event(interface)
    row_in_mapped_wa_event = get_row_in_mapped_event_for_cadet_id_both_cancelled_and_active(
        interface=interface,
        cadet_id=cadet_id, event=event,
        raise_error_on_duplicate=True
    )
    new_cadet_at_event_from_mapped_event_data = (
        get_cadet_at_event_from_row_in_mapped_event(
            row_in_mapped_wa_event=row_in_mapped_wa_event,
            event=event,
            cadet_id=cadet_id
        )
    )

    if use_form_data:
        update_cadet_at_event_with_form_data(interface=interface, new_cadet_at_event=new_cadet_at_event_from_mapped_event_data)

    return new_cadet_at_event_from_mapped_event_data

def update_cadet_at_event_with_form_data(interface: abstractInterface, new_cadet_at_event: CadetAtEvent):
    event = get_event_from_state(interface)
    new_status, new_attendance = status_and_attendance_from_form_entries(interface=interface,
                                                                         cadet_at_event=new_cadet_at_event,
                                                                         event=event)

    new_cadet_at_event.status = new_status
    new_cadet_at_event.availability = new_attendance


def status_and_attendance_from_form_entries(
    interface: abstractInterface,
    cadet_at_event: CadetAtEvent,
        event: Event
) -> Tuple[RegistrationStatus, DaySelector]:

    try:
        attendance = get_availablity_from_form(interface=interface, event=event, input_name=ATTENDANCE)
    except:
        attendance = cadet_at_event.availability
        print("Attendance not included in form")

    try:
        status = get_status_from_form(interface=interface, input_name=ROW_STATUS)
    except:
        status = cadet_at_event.status
        print("Attendance not included in form")

    return (status, attendance)