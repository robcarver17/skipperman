from app.backend.form_utils import get_availablity_from_form, get_status_from_form
from app.backend.wa_import.update_cadets_at_event import update_row_in_master_event_data, \
    get_row_in_mapped_event_for_cadet_id
from app.logic.events.constants import ROW_STATUS, ATTENDANCE
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.cadets_at_event.track_cadet_id_in_state_when_importing import get_current_cadet_id_at_event
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event
from app.objects.OLDmaster_event import RowInMasterEvent, get_row_of_master_event_from_mapped_row_with_idx_and_status


def update_mapped_wa_event_data_with_new_data(interface: abstractInterface):
    event = get_event_from_state(interface)
    new_row_in_mapped_wa_event_with_status = (
        get_new_row_in_mapped_wa_event_from_state_data(event=event, interface=interface)
    )
    update_row_in_master_event_data(
        event=event,
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
    )


def update_mapped_wa_event_data_with_form_data(interface: abstractInterface):
    event = get_event_from_state(interface)
    new_row_in_mapped_wa_event_with_status = (
        get_new_row_merged_with_form_data_in_mapped_wa_event(
            interface=interface, event=event
        )
    )
    update_row_in_master_event_data(
        event=event,
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
    )


def get_new_row_in_mapped_wa_event_from_state_data(
    interface: abstractInterface, event: Event
) -> RowInMasterEvent:
    cadet_id = get_current_cadet_id_at_event(interface)

    row_in_mapped_wa_event_with_id = get_row_in_mapped_event_for_cadet_id(
        event, cadet_id=cadet_id
    )

    new_row_in_mapped_wa_event_with_status = (
        get_row_of_master_event_from_mapped_row_with_idx_and_status(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id,
            event=event
        )
    )
    return new_row_in_mapped_wa_event_with_status


def get_new_row_merged_with_form_data_in_mapped_wa_event(
    interface: abstractInterface, event: Event
) -> RowInMasterEvent:
    new_row_in_mapped_wa_event_with_status = (
        get_new_row_in_mapped_wa_event_from_state_data(interface=interface, event=event)
    )
    new_row_in_mapped_wa_event_with_status = replace_row_values_from_form_values_in_mapped_wa_event(
        interface=interface,
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
        event = event
    )

    return new_row_in_mapped_wa_event_with_status


def replace_row_values_from_form_values_in_mapped_wa_event(
    interface: abstractInterface,
    new_row_in_mapped_wa_event_with_status: RowInMasterEvent,
        event: Event
) -> RowInMasterEvent:

    attendance = get_availablity_from_form(interface=interface, event=event, input_name=ATTENDANCE)
    status = get_status_from_form(interface=interface, input_name=ROW_STATUS)

    new_row_in_mapped_wa_event_with_status.status = status
    new_row_in_mapped_wa_event_with_status.attendance = attendance

    return new_row_in_mapped_wa_event_with_status