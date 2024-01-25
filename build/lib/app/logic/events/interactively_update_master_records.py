from typing import Union

from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.logic.abstract_interface import abstractInterface, form_with_message_and_finished_button
from app.logic.events.constants import ROW_IN_EVENT_DATA, USE_ORIGINAL_DATA_BUTTON_LABEL, USE_DATA_IN_FORM_BUTTON_LABEL, USE_NEW_DATA_BUTTON_LABEL

from app.logic.events.events_in_state import get_event_from_state

from app.backend.load_and_save_wa_mapped_events import (
    load_master_event

)
from app.logic.events.update_existing_master_event_data_forms import display_form_for_update_to_existing_row_of_event_data,increment_and_save_id_in_event_data, update_mapped_wa_event_data_with_form_data, update_mapped_wa_event_data_with_new_data

from app.backend.update_master_event_data import \
    report_on_missing_data_from_mapped_wa_event_data_and_save_to_master_event, get_row_from_event_file_with_ids, add_new_row_to_master_event_data, get_row_of_master_event_from_mapped_row_with_idx_and_status
from app.objects.events import Event
from app.objects.mapped_wa_event_with_ids import RowInMappedWAEventWithId
from app.objects.constants import  NoMoreData, missing_data

def display_form_interactively_update_master_records(
    interface: abstractInterface
) -> Union[Form, NewForm]:
    input("Press enter to continue")

    event = get_event_from_state(interface)
    print("Now updating cadets which are missing")
    report_on_missing_data_from_mapped_wa_event_data_and_save_to_master_event(event=event, interface=interface)

    return process_updates_to_master_event_data(interface)


def process_updates_to_master_event_data(interface: abstractInterface) -> Union[Form, NewForm]:
    print("Looping through updating master event data")
    input("Press enter to continue")
    event = get_event_from_state(interface)
    row_idx = get_current_row_id_in_event_data(interface)

    try:
        row_in_mapped_wa_event_with_id = (
            get_row_from_event_file_with_ids(event, row_idx=row_idx)
        )
    except NoMoreData:
        print("Finished looping")
        return form_with_message_and_finished_button("Finished importing WA data")

    if row_in_mapped_wa_event_with_id.cancelled_or_deleted:
        return iterate_to_next_row_of_mapped_wa_data(interface)

    return process_update_to_next_row_of_event_data(
        interface=interface,
        event=event,
        row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
    )


def process_update_to_next_row_of_event_data(interface: abstractInterface,
                                             event: Event,
                                             row_in_mapped_wa_event_with_id: RowInMappedWAEventWithId) -> Form:
    cadet_already_present_in_master_data = is_cadet_already_in_master_data(
        event=event,
        row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
    )

    if cadet_already_present_in_master_data:
        print("Not a new cadet")
        return process_update_to_existing_row_of_event_data(interface=interface,
                                                            event=event,
                                                            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id)
    else:
        # new cadet
        ## updates wa_event_data_without_duplicates in memory no return required
        print("New cadet, adding to master event data %s" % str(row_in_mapped_wa_event_with_id))
        add_new_row_to_master_event_data(
            event, row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
        )
        return iterate_to_next_row_of_mapped_wa_data(interface)


def is_cadet_already_in_master_data(event: Event,
                                    row_in_mapped_wa_event_with_id: RowInMappedWAEventWithId) -> bool:
    master_event = load_master_event(
        event
    )
    ## confirm isn't a deleted or cancelled
    cadet_id = row_in_mapped_wa_event_with_id.cadet_id
    cadet_already_present_in_master_data = master_event.is_cadet_id_in_event(
        cadet_id
    )

    return cadet_already_present_in_master_data


def process_update_to_existing_row_of_event_data(
        interface: abstractInterface,
        row_in_mapped_wa_event_with_id: RowInMappedWAEventWithId,
        event: Event,
)-> Form:
    master_event = load_master_event(
        event
    )

    new_row_in_mapped_wa_event_with_status = (
        get_row_of_master_event_from_mapped_row_with_idx_and_status(
            row_in_mapped_wa_event_with_id=row_in_mapped_wa_event_with_id
        )
    )
    existing_row_in_master_event = (
        master_event.get_row_with_id(
            new_row_in_mapped_wa_event_with_status.cadet_id
        )
    )

    if new_row_in_mapped_wa_event_with_status == existing_row_in_master_event:
        ## nothing to do
        print("No change to %s" % (str(existing_row_in_master_event)))
        return iterate_to_next_row_of_mapped_wa_data(interface)
    else:
        print("Data has changed displaying form")
        return display_form_for_update_to_existing_row_of_event_data(interface =interface,
                                                                     existing_row_in_master_event=existing_row_in_master_event,
                                                                     new_row_in_mapped_wa_event_with_status=new_row_in_mapped_wa_event_with_status)



def post_form_interactively_update_master_records(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    last_button_pressed = interface.last_button_pressed()
    if last_button_pressed == USE_ORIGINAL_DATA_BUTTON_LABEL:
        ## nothing to do, no change to master file
        print("Using original data")
    elif last_button_pressed == USE_NEW_DATA_BUTTON_LABEL:
        print("using new data")
        update_mapped_wa_event_data_with_new_data(interface)
    elif last_button_pressed == USE_DATA_IN_FORM_BUTTON_LABEL:
        print("Updating from form data")
        update_mapped_wa_event_data_with_form_data(interface)

    return iterate_to_next_row_of_mapped_wa_data(interface)


def iterate_to_next_row_of_mapped_wa_data(interface: abstractInterface) -> Union[Form, NewForm]:
    ## we don't delete from the event data with ID, but increment a row marker
    increment_and_save_id_in_event_data(interface)
    ## next row until file finished
    return process_updates_to_master_event_data(interface)



def get_current_row_id_in_event_data(interface: abstractInterface) -> int:
    id = interface.get_persistent_value(ROW_IN_EVENT_DATA)
    if id is missing_data:
        return 0
    else:
        return id
