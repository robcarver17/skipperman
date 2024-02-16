from typing import Union

from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.events.constants import (
    WA_UPDATE_CADETS_AT_EVENT_IN_VIEW_EVENT_STAGE,
    DOUBLE_CHECKED_OK_ADD_CADET_BUTTON_LABEL,
    FINAL_CADET_ADD_BUTTON_LABEL,
    SEE_ALL_CADETS_BUTTON_LABEL,
    SEE_SIMILAR_CADETS_ONLY_LABEL,
)

from app.logic.events.events_in_state import get_event_from_state
from app.backend.wa_import.add_cadet_ids_to_mapped_wa_event_data import (
    add_identified_cadet_and_row,
    get_cadet_data_from_row_of_mapped_data_no_checks,
)
from app.backend.data.mapped_events import load_existing_mapped_wa_event, get_row_in_mapped_event_data_given_id
from app.logic.events.cadets_at_event.get_or_select_cadet_forms import (
    get_add_or_select_existing_cadet_form,
)
from app.backend.cadets import confirm_cadet_exists, get_cadet_from_list_of_cadets, get_sorted_list_of_cadets
from app.logic.cadets.add_cadet import add_cadet_from_form_to_data
from app.objects.constants import NoMoreData
from app.objects.mapped_wa_event import RowInMappedWAEvent
from app.objects.cadets import Cadet


def display_form_iteratively_add_cadets_during_import(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    print("Looping through allocating IDs on WA file without IDs")

    try:
        next_row = get_row_in_mapped_event_data_given_id(event)
        print("On row %s" % str(next_row))
        return process_next_row(next_row=next_row, interface=interface)
    except NoMoreData:
        print("Finished looping through allocating IDs")
        print("%s" % str(load_existing_mapped_wa_event(event)))
        return NewForm(WA_UPDATE_CADETS_AT_EVENT_IN_VIEW_EVENT_STAGE)


def process_next_row(
    next_row: RowInMappedWAEvent, interface: abstractInterface
) -> Form:
    try:
        cadet = get_cadet_data_from_row_of_mapped_data_no_checks(next_row)
    except Exception as e:
        ## Mapping has gone badly wrong, or date field corrupted
        raise Exception(
            "Error code %s cannot identify cadet from row %s: file is probably corrupt re-upload"
            % (str(e), str(next_row)),
        )
    return process_next_row_with_cadet_from_row(cadet=cadet,
                                                interface=interface)

def process_next_row_with_cadet_from_row(
    interface: abstractInterface,
    cadet: Cadet
) -> Form:
    list_of_cadets = get_sorted_list_of_cadets()
    if cadet in list_of_cadets:
        matched_cadet_with_id = list_of_cadets.matching_cadet(cadet)
        print("Cadet %s matched id is %s" % (str(cadet), matched_cadet_with_id.id))
        return process_row_when_cadet_matched(
            interface=interface, cadet=matched_cadet_with_id
        )
    else:
        print("Cadet %s not matched" % str(cadet))
        return process_row_when_cadet_unmatched(interface=interface, cadet=cadet)


def process_row_when_cadet_matched(interface: abstractInterface, cadet: Cadet) -> Form:
    event = get_event_from_state(interface)
    next_row = get_row_in_mapped_event_data_given_id(event)
    print("adding matched row %s with id %s" % (str(next_row), cadet.id))
    add_identified_cadet_and_row(
        event=event, new_row=next_row, cadet_id=cadet.id
    )
    ## run recursively until no more data
    return display_form_iteratively_add_cadets_during_import(interface)


def process_row_when_cadet_unmatched(
    interface: abstractInterface, cadet: Cadet
) -> Form:
    ## Need to display a form with 'verification' text'

    return get_add_or_select_existing_cadet_form(
        cadet=cadet,
        interface=interface,
        see_all_cadets=False,
        include_final_button=False,
    )


def post_form_iteratively_add_cadets_during_import(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    last_button_pressed = interface.last_button_pressed()
    if (
        last_button_pressed == DOUBLE_CHECKED_OK_ADD_CADET_BUTTON_LABEL
        or last_button_pressed == SEE_SIMILAR_CADETS_ONLY_LABEL
    ):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface, include_final_button=True, see_all_cadets=False
        )

    elif last_button_pressed == SEE_ALL_CADETS_BUTTON_LABEL:
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface, include_final_button=True, see_all_cadets=True
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
