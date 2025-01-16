from typing import Tuple

from app.objects.cadets import Cadet

from app.frontend.forms.form_utils import (
    get_availablity_from_form,
    get_status_from_form,
)
from app.backend.registration_data.update_cadets_at_event import \
    replace_existing_cadet_at_event_where_original_cadet_was_inactive
from app.backend.cadets_at_event.update_status_and_availability_of_cadets_at_event import \
    update_status_of_existing_cadet_at_event_to_cancelled_or_deleted_and_return_messages, \
    update_availability_of_existing_cadet_at_event_and_return_messages, \
    update_status_of_existing_cadet_at_event_when_not_cancelling_or_deleting
from app.backend.registration_data.cadet_registration_data import get_cadet_at_event
from app.backend.registration_data.identified_cadets_at_event import \
    get_row_in_registration_data_for_cadet_both_cancelled_and_active
from app.frontend.events.constants import ROW_STATUS, ATTENDANCE
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.events.cadets_at_event.track_cadet_id_in_state_when_importing import (
    get_current_cadet_at_event
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadet_with_id_at_event import (
    CadetWithIdAtEvent,
    get_cadet_at_event_from_row_in_event_raw_registration_data,
)
from app.objects.day_selectors import DaySelector
from app.objects.events import Event
from app.objects.registration_status import RegistrationStatus, new_registration_replacing_deleted_or_cancelled, existing_registration_now_deleted_or_cancelled, status_unchanged, \
    status_still_active_but_has_changed
from app.frontend.events.cadets_at_event.update_existing_cadet_at_event_from_form_entries import interpret_status_change


def update_cadets_at_event_with_form_data(interface: abstractInterface):
    event = get_event_from_state(interface)
    cadet = get_current_cadet_at_event(interface)
    new_cadet_at_event = get_new_cadet_at_event_from_mapped_event_and_optionally_form(
        interface, event=event, cadet=cadet, use_form_data=True
    )
    update_cadets_at_event(interface=interface, event=event,cadet=cadet, new_cadet_at_event=new_cadet_at_event)


def update_cadets_at_event_with_new_data(interface: abstractInterface):
    event = get_event_from_state(interface)
    cadet = get_current_cadet_at_event(interface)
    new_cadet_at_event = get_new_cadet_at_event_from_mapped_event_and_optionally_form(
        interface, event=event, cadet=cadet, use_form_data=False
    )
    update_cadets_at_event(interface=interface, event=event,cadet=cadet, new_cadet_at_event=new_cadet_at_event)




def get_new_cadet_at_event_from_mapped_event_and_optionally_form(
    interface: abstractInterface, event: Event, cadet: Cadet, use_form_data: bool = False
) -> CadetWithIdAtEvent:
    row_in_mapped_wa_event = (
        get_row_in_registration_data_for_cadet_both_cancelled_and_active(
            object_store=interface.object_store,
            cadet=cadet,
            event=event,
            raise_error_on_duplicate=True, ## if a duplicate cadet wouldn't get here as we ignore them in the main loop
        )
    )
    new_cadet_at_event_from_mapped_event_data = (
        get_cadet_at_event_from_row_in_event_raw_registration_data(
            row_in_mapped_wa_event=row_in_mapped_wa_event,
            event=event,
            cadet=cadet
        )
    )

    if use_form_data:
        update_cadet_at_event_with_form_data(
            interface=interface,
            event=event,
            new_cadet_at_event=new_cadet_at_event_from_mapped_event_data,
        )

    return new_cadet_at_event_from_mapped_event_data


def update_cadet_at_event_with_form_data(
    interface: abstractInterface, event: Event, new_cadet_at_event: CadetWithIdAtEvent
):
    new_status, new_attendance = status_and_attendance_from_form_entries(
        interface=interface, cadet_at_event=new_cadet_at_event, event=event
    )

    new_cadet_at_event.status = new_status
    new_cadet_at_event.availability = new_attendance


def status_and_attendance_from_form_entries(
    interface: abstractInterface, cadet_at_event: CadetWithIdAtEvent, event: Event
) -> Tuple[RegistrationStatus, DaySelector]:
    try:
        attendance = get_availablity_from_form(
            interface=interface, event=event, input_name=ATTENDANCE
        )
    except:
        attendance = cadet_at_event.availability
        print("Attendance not included in form")

    try:
        status = get_status_from_form(interface=interface, input_name=ROW_STATUS)
    except:
        status = cadet_at_event.status
        print("Attendance not included in form")

    return (status, attendance)


def update_cadets_at_event(
    interface: abstractInterface, event: Event, cadet: Cadet, new_cadet_at_event: CadetWithIdAtEvent
):
    existing_cadet_at_event = get_existing_cadet_at_event_from_state(interface)
    update_comparing_new_and_existing_cadet_at_event(
        interface=interface,
        event=event,
        cadet=cadet,
        existing_cadet_at_event=existing_cadet_at_event,
        new_cadet_at_event=new_cadet_at_event
    )



def get_existing_cadet_at_event_from_state(
    interface: abstractInterface,
) -> CadetWithIdAtEvent:
    event = get_event_from_state(interface)
    cadet = get_current_cadet_at_event(interface)

    existing_cadet_at_event = get_cadet_at_event(
        object_store=interface.object_store, event=event, cadet=cadet
    )

    return existing_cadet_at_event


def update_comparing_new_and_existing_cadet_at_event(interface: abstractInterface,
                                                     event: Event,
                                                     cadet: Cadet,
                                                     existing_cadet_at_event: CadetWithIdAtEvent,
                                                     new_cadet_at_event: CadetWithIdAtEvent):

    reg_status_change  = interpret_status_change(
        existing_cadet_at_event=existing_cadet_at_event,
        new_cadet_at_event=new_cadet_at_event
    )

    if reg_status_change== status_unchanged:
        ## Must be an availability change
        update_cadet_at_event_when_status_unchanged_and_availability_has_probably_changed(
            interface=interface,
            event=event,
            cadet=cadet,
            new_cadet_at_event=new_cadet_at_event,
            existing_cadet_at_event=existing_cadet_at_event,
        )
    if reg_status_change== new_registration_replacing_deleted_or_cancelled:
        ## Replace entire original cadet, new registration
        replace_existing_cadet_at_event_where_original_cadet_was_inactive(
            object_store=interface.object_store, event=event, new_cadet_at_event=new_cadet_at_event
        )

    elif reg_status_change== existing_registration_now_deleted_or_cancelled:
        ## availability is a moot point
        new_status = new_cadet_at_event.status
        update_status_of_existing_cadet_at_event_to_cancelled_or_deleted_and_return_messages(
            object_store=interface.object_store,
            event=event,
            new_status=new_status,
            cadet=cadet,
        )

    elif reg_status_change== status_still_active_but_has_changed:
        new_status = new_cadet_at_event.status
        update_status_of_existing_cadet_at_event_when_not_cancelling_or_deleting(
            object_store=interface.object_store,
            event=event,
            cadet=cadet,
            new_status=new_status,
        )

    else:
        interface.log_error(
            "For existing cadet %s status change from %s to %s don't know how to handle"
                        % (str(new_cadet_at_event), existing_cadet_at_event.status.name, new_cadet_at_event.status.name))


    interface.flush_cache_to_store()


def update_cadet_at_event_when_status_unchanged_and_availability_has_probably_changed(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    new_cadet_at_event: CadetWithIdAtEvent,
    existing_cadet_at_event: CadetWithIdAtEvent,
):
    original_availability = existing_cadet_at_event.availability
    new_availability = new_cadet_at_event.availability

    availability_unchanged = new_availability == original_availability

    if availability_unchanged:
        ## Neithier status or availability has changed - shouldn't happen, but heigh ho
        print(
            "Code identified major change for cadet %s but nothing appears to have happened, probably user entering original values in form for some reason"
            % str(existing_cadet_at_event)
        )
        return

    days_available = event.days_in_event_overlap_with_selected_days(new_availability)
    if len(days_available) == 0:
        interface.log_error(
            "For existing cadet %s you haven't selected any days that they are attending - not making any changes, instead consider manually cancelling in registration data"
            % str(existing_cadet_at_event)
        )
        return

    list_of_messages = update_availability_of_existing_cadet_at_event_and_return_messages(
        object_store=interface.object_store,
        event=event,
        new_availabilty=new_availability,
        cadet=cadet,
    )

    for message in list_of_messages:
        interface.log_error(message)

