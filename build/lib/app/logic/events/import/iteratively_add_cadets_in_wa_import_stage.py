from typing import Union

from app.logic.abstract_form import Form, NewForm
from app.logic.abstract_interface import abstractInterface
from app.logic.events.constants import WA_INTERACTIVELY_REMOVE_SPECIFIC_DUPLICATES_FROM_WA_FILE,     CHECK_CADET_BUTTON_LABEL,    FINAL_CADET_ADD_BUTTON_LABEL,    SEE_ALL_CADETS_BUTTON_LABEL,SEE_SIMILAR_CADETS_ONLY_LABEL

from app.logic.events.utilities import get_event_from_state
from app.logic.events.backend.add_cadet_ids_to_mapped_wa_event_data import (
    get_first_unmapped_row_for_event,
    add_row_data_with_id_included_and_delete_from_unmapped_data,
    get_cadet_data_from_row_of_mapped_data_no_checks,
)

from app.logic.events.get_or_select_cadet_forms import get_add_or_select_existing_cadet_form
from app.logic.cadets.view_cadets import get_list_of_cadets
from app.logic.cadets.view_individual_cadets import confirm_cadet_exists, get_cadet_from_list_of_cadets
from app.logic.cadets.add_cadet import add_cadet_from_form_to_data
from app.objects.constants import NoMoreData
from app.objects.mapped_wa_event_no_ids import RowInMappedWAEventNoId
from app.objects.cadets import Cadet

def display_form_iteratively_add_cadets_during_import(
    interface: abstractInterface
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    print("Looping through allocating IDs on WA file without IDs")
    input("Press enter to continue")

    try:
        next_row = get_first_unmapped_row_for_event(event)
        print("On row %s" % str(next_row))
        return process_next_row(next_row=next_row, interface=interface)
    except NoMoreData:
        print("Finished looping through allocating IDs")
        return NewForm(WA_INTERACTIVELY_REMOVE_SPECIFIC_DUPLICATES_FROM_WA_FILE)


def process_next_row(
        next_row: RowInMappedWAEventNoId, interface: abstractInterface
) -> Form:
    try:
        cadet = get_cadet_data_from_row_of_mapped_data_no_checks(next_row)
    except Exception as e:
        ## Mapping has gone badly wrong, or date field corrupted
        raise Exception("Error code %s cannot identify cadet from row %s: file is probably corrupt re-upload"
                        % (str(e), str(next_row)),
                        )

    list_of_cadets = get_list_of_cadets()
    if cadet in list_of_cadets:
        ## MATCHED
        print("Cadet %s matched" % str(cadet))
        return process_row_when_cadet_matched(interface=interface, cadet=cadet)
    else:
        ## NOT MATCHED
        print("Cadet %s not matched" % str(cadet))
        return process_row_when_cadet_unmatched(interface=interface, cadet=cadet)


def process_row_when_cadet_matched(
        interface: abstractInterface, cadet: Cadet
)-> Form:
    event = get_event_from_state(interface)
    next_row = get_first_unmapped_row_for_event(event)
    print("adding matched row %s with id %s" % (str(next_row), cadet.id))
    add_row_data_with_id_included_and_delete_from_unmapped_data(event=event, new_row=next_row, cadet_id=cadet.id)
    ## run recursively until no more data
    return display_form_iteratively_add_cadets_during_import(interface)


def process_row_when_cadet_unmatched(
        interface: abstractInterface, cadet: Cadet
)-> Form:
    ## Need to display a form with 'verification' text'

    return get_add_or_select_existing_cadet_form(
        cadet=cadet,
        interface=interface,
        see_all_cadets=False,
        include_final_button=False
    )


def post_form_iteratively_add_cadets_during_import(interface: abstractInterface) -> Union[Form, NewForm]:
    ## Called by post on view events form, so both stage and event name are set
    ## don't need to check for post as will always be one
    last_button_pressed = interface.last_button_pressed()
    if (
            last_button_pressed == CHECK_CADET_BUTTON_LABEL
            or last_button_pressed == SEE_SIMILAR_CADETS_ONLY_LABEL
    ):
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface,
            include_final_button=True,
            see_all_cadets=False
        )

    elif last_button_pressed == SEE_ALL_CADETS_BUTTON_LABEL:
        ## verify results already in form, display form again, allow final this time
        return get_add_or_select_existing_cadet_form(
            interface=interface,
            include_final_button=True,
            see_all_cadets=True
        )

    elif last_button_pressed == FINAL_CADET_ADD_BUTTON_LABEL:
        # no need to reset stage
        return process_form_when_verified_cadet_to_be_added(interface)

    else:
        ## must be an existing cadet that has been selected
        # no need to reset stage
        return process_form_when_existing_cadet_chosen(interface)


def process_form_when_verified_cadet_to_be_added(
        interface: abstractInterface
)-> Form:
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
        raise Exception("Cadet selected no longer exists - file corruption or someone deleted?",
                        )

    cadet = get_cadet_from_list_of_cadets(cadet_selected)

    return process_row_when_cadet_matched(interface=interface, cadet=cadet)





