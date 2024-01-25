from app.backend.update_master_event_data import update_row_in_master_event_data, \
    get_row_in_mapped_event_for_cadet_id, get_row_in_master_event_for_cadet_id, \
    get_dict_of_diffs_where_significant_values_changed, get_list_of_field_names_from_dict_of_dict_diffs
from app.logic.events.constants import ROW_STATUS
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.update_master.track_cadet_id_in_master_file_update import get_current_cadet_id
from app.logic.abstract_interface import abstractInterface
from app.objects.events import Event
from app.objects.master_event import RowInMasterEvent, get_row_of_master_event_from_mapped_row_with_idx_and_status


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
    cadet_id = get_current_cadet_id(interface)

    row_in_mapped_wa_event_with_id = get_row_in_mapped_event_for_cadet_id(
        event, cadet_id=cadet_id
    )

    new_row_in_mapped_wa_event_with_status = (
        get_row_of_master_event_from_mapped_row_with_idx_and_status(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
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
    )

    return new_row_in_mapped_wa_event_with_status


def replace_row_values_from_form_values_in_mapped_wa_event(
    interface: abstractInterface,
    new_row_in_mapped_wa_event_with_status: RowInMasterEvent,
) -> RowInMasterEvent:
    field_names = get_field_names_for_recently_posted_event_diff_form(
        interface=interface,
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
    )
    for field in field_names:
        try:
            new_row_in_mapped_wa_event_with_status.data_in_row[
                field
            ] = interface.value_from_form(field) ### WON'T WORK FOR DATES
        except:
            raise Exception("Value for field %s not found in form" % field)

    return new_row_in_mapped_wa_event_with_status


def get_field_names_for_recently_posted_event_diff_form(
    interface: abstractInterface,
    new_row_in_mapped_wa_event_with_status: RowInMasterEvent,
):
    event = get_event_from_state(interface)
    cadet_id = get_current_cadet_id(interface)
    existing_row_in_master_event = get_row_in_master_event_for_cadet_id(
        cadet_id=cadet_id, event=event
    )
    dict_of_dict_diffs = get_dict_of_diffs_where_significant_values_changed(
        new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status,
        existing_row_in_master_event=existing_row_in_master_event,
    )

    field_names = get_list_of_field_names_from_dict_of_dict_diffs(dict_of_dict_diffs)

    return [ROW_STATUS] + field_names
