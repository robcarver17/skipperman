from typing import Union


from app.backend.data.mapped_events import get_row_in_mapped_event_data_given_id
from app.backend.data.cadets_at_event import  load_identified_cadets_at_event
from app.backend.cadets import confirm_cadet_exists, get_cadet_from_list_of_cadets, load_list_of_all_cadets
from app.logic.events.cadets_at_event.interactively_update_records_of_cadets_at_event import \
    display_form_interactively_update_cadets_at_event

from app.logic.events.constants import *
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.import_wa.shared_state_tracking_and_data import get_and_save_next_row_id_in_mapped_event_data, \
    get_current_row_id, clear_row_in_state
from app.backend.wa_import.add_cadet_ids_to_mapped_wa_event_data import (
    add_identified_cadet_and_row,
    get_cadet_data_from_row_of_mapped_data_no_checks,
)
from app.logic.events.cadets_at_event.get_or_select_cadet_forms import (
    get_add_or_select_existing_cadet_form,
)
from app.logic.cadets.add_cadet import add_cadet_from_form_to_data

from app.objects.constants import NoMoreData, missing_data
from app.objects.mapped_wa_event import RowInMappedWAEvent
from app.objects.cadets import Cadet
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface


def display_form_add_cadet_ids_during_import(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## rest of the time is post

    clear_row_in_state(interface)
    return add_cadet_ids_on_next_row(interface)


def add_cadet_ids_on_next_row(
            interface: abstractInterface,
    ) -> Union[Form, NewForm]:

    event = get_event_from_state(interface)
    print("Looping through allocating IDs on WA file without IDs")

    try:
        row_id = get_and_save_next_row_id_in_mapped_event_data(interface)
        next_row = get_row_in_mapped_event_data_given_id(event=event, row_id=row_id)
        print("On row %s" % str(next_row))
        return process_next_row(next_row=next_row, interface=interface)
    except NoMoreData:
        print("Finished looping through allocating Cadet IDs")
        clear_row_in_state(interface)
        ## don't return to controller as need to update cadet data now
        return go_to_update_cadet_data_form(interface)


def process_next_row(
    next_row: RowInMappedWAEvent, interface: abstractInterface
) -> Form:
    ### NOTE: In theory we only need to deal with new rows, but no harm in doing all of them
    ##
    row_id_has_identified_cadet = is_row_already_identified_with_cadet(next_row=next_row, interface=interface)
    if row_id_has_identified_cadet:
        print("Row id %s already identified with a cadet")
        return add_cadet_ids_on_next_row(interface)

    try:
        cadet = get_cadet_data_from_row_of_mapped_data_no_checks(next_row)
        return process_next_row_with_cadet_from_row(cadet=cadet,
                                                    interface=interface,
                                                    next_row=next_row)
    except Exception as e:
        ## Mapping has gone badly wrong, or date field corrupted
        raise Exception(
            "Error code %s cannot identify cadet from row %s: file maybe corrupt or does not actually contain cadets - re-upload or change event configuration"
            % (str(e), str(next_row)),
        )

def is_row_already_identified_with_cadet(next_row: RowInMappedWAEvent, interface: abstractInterface)-> bool:
    event = get_event_from_state(interface)
    identified_cadets = load_identified_cadets_at_event(event)
    row_id_has_identified_cadet =  next_row.row_id in identified_cadets.list_of_row_ids()

    return row_id_has_identified_cadet


def process_next_row_with_cadet_from_row(
    interface: abstractInterface,
    cadet: Cadet,
    next_row: RowInMappedWAEvent
) -> Form:
    list_of_cadets = load_list_of_all_cadets()
    matched_cadet_with_id = list_of_cadets.matching_cadet(cadet)

    if matched_cadet_with_id is missing_data:
        print("Cadet %s not matched" % str(cadet))
        return process_row_when_cadet_unmatched(interface=interface, cadet=cadet)
    else:
        print("Cadet %s matched id is %s" % (str(cadet), matched_cadet_with_id.id))
        return process_row_when_cadet_matched(
            interface=interface, cadet=matched_cadet_with_id
        )


def process_row_when_cadet_matched(interface: abstractInterface, cadet: Cadet) -> Form:
    event = get_event_from_state(interface)
    row_id = get_current_row_id(interface)
    print("adding matched row %s with id %s" % (row_id, cadet.id))
    add_identified_cadet_and_row(
        event=event, row_id=row_id, cadet_id=cadet.id
    )
    ## run recursively until no more data
    return add_cadet_ids_on_next_row(interface)


def process_row_when_cadet_unmatched(
    interface: abstractInterface, cadet: Cadet,
) -> Form:
    ## Need to display a form with 'verification' text'

    return get_add_or_select_existing_cadet_form(
        cadet=cadet,
        interface=interface,
        see_all_cadets=False,
        include_final_button=False,
        header_text=header_text_for_form(interface)
    )

def header_text_for_form(interface: abstractInterface)-> str:
    row_id = get_current_row_id(interface)
    event =get_event_from_state(interface)
    next_row = get_row_in_mapped_event_data_given_id(event=event, row_id=row_id)
    default_header_text = "Looks like a new cadet in the WA entry file. You can edit them, check their details and then add, or choose an existing cadet instead (avoid creating duplicates! If the existing cadet details are wrong, select them for now and edit later) \n\n Row details are: \n%s"

    return default_header_text % next_row


def post_form_add_cadet_ids_during_import(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    header_text = header_text_for_form(interface)
    last_button_pressed = interface.last_button_pressed()
    if (
        last_button_pressed == DOUBLE_CHECKED_OK_ADD_CADET_BUTTON_LABEL
        or last_button_pressed == SEE_SIMILAR_CADETS_ONLY_LABEL
        or last_button_pressed == CHECK_CADET_FOR_ME_BUTTON_LABEL
    ):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface, include_final_button=True, see_all_cadets=False,
            header_text=header_text
        )

    elif last_button_pressed == SEE_ALL_CADETS_BUTTON_LABEL:
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface, include_final_button=True, see_all_cadets=True,
            header_text = header_text
        )

    elif last_button_pressed == FINAL_CADET_ADD_BUTTON_LABEL:
        # no need to reset stage
        return process_form_when_verified_cadet_to_be_added(interface)

    else:
        ## must be an existing cadet that has been selected
        # no need to reset stage
        return process_form_when_existing_cadet_chosen(interface)


def process_form_when_verified_cadet_to_be_added(interface: abstractInterface) -> Form:
    try:
        cadet = add_cadet_from_form_to_data(interface)
    except Exception as e:
        raise Exception(
            "Problem adding cadet to data code %s CONTACT SUPPORT" % str(e),
        )

    return process_row_when_cadet_matched(interface=interface, cadet=cadet)


def process_form_when_existing_cadet_chosen(interface: abstractInterface) -> Form:
    cadet_selected = interface.last_button_pressed()

    try:
        confirm_cadet_exists(cadet_selected)
    except:
        raise Exception(
            "Cadet selected no longer exists - file corruption or someone deleted?",
        )

    cadet = get_cadet_from_list_of_cadets(cadet_selected)

    return process_row_when_cadet_matched(interface=interface, cadet=cadet)

def go_to_update_cadet_data_form(interface: abstractInterface):
    return interface.get_new_form_given_function(display_form_interactively_update_cadets_at_event)
