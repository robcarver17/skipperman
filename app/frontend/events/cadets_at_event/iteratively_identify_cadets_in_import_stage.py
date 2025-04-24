from typing import Union

from app.backend.cadets.list_of_cadets import get_matching_cadet, get_list_of_very_similar_cadets_from_data

from app.objects.abstract_objects.abstract_lines import ListOfLines, ProgressBar, HorizontalLine

from app.backend.registration_data.raw_mapped_registration_data import (
    get_row_in_raw_registration_data_given_id,
    get_cadet_data_from_row_of_registration_data_no_checks,
)
from app.backend.registration_data.identified_cadets_at_event import (
    is_row_in_event_already_identified_with_cadet,
    add_identified_cadet_and_row,
    mark_row_as_skip_cadet,
)

from app.frontend.shared.events_state import get_event_from_state

from app.frontend.events.import_data.shared_state_tracking_and_data import (
    get_and_save_next_row_id_in_raw_registration_data,
    get_current_row_id,
    clear_row_in_state,
percentage_of_row_ids_done_in_registration_file
)

from app.frontend.shared.get_or_select_cadet_forms import (
    get_add_or_select_existing_cadet_form,
     ParametersForGetOrSelectCadetForm, generic_post_response_to_add_or_select_cadet,
)

from app.objects.utilities.exceptions import NoMoreData, MissingData, missing_data
from app.objects.registration_data import RowInRegistrationData
from app.objects.cadets import Cadet
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface


def display_form_identify_cadets_during_import(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## rest of the time is post

    clear_row_in_state(interface)
    return identify_cadets_on_next_row(interface)


def identify_cadets_on_next_row(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)
    print("Looping through allocating IDs on WA file without IDs")

    try:
        row_id = get_and_save_next_row_id_in_raw_registration_data(interface)
    except NoMoreData:
        print("Finished looping through allocating Cadet IDs")
        clear_row_in_state(interface)
        return finished_looping_return_to_controller(interface)

    next_row = get_row_in_raw_registration_data_given_id(
        object_store=interface.object_store, event=event, row_id=row_id
    )
    print("On row %s" % str(next_row))
    return process_current_row(row=next_row, interface=interface)


def finished_looping_return_to_controller(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_form_identify_cadets_during_import
    )


def process_current_row(
    row: RowInRegistrationData, interface: abstractInterface
) -> Form:
    ### NOTE: In theory we only need to deal with new rows, but no harm in doing all of them
    ##
    row_id_has_identified_cadet = is_row_already_identified_with_cadet(
        row=row, interface=interface
    )
    if row_id_has_identified_cadet:
        print("Row id %s already identified with a cadet")
        return identify_cadets_on_next_row(interface)

    try:
        cadet = get_cadet_data_from_row_of_registration_data_no_checks(row)

    except Exception as e:
        ## Mapping has gone badly wrong, or date field corrupted
        raise Exception(
            "Error code %s cannot identify cadet from row %s: file maybe corrupt or does not actually contain cadets - re-upload or change event configuration"
            % (str(e), str(row)),
        )

    return process_next_row_with_cadet_from_row(cadet=cadet, interface=interface)


def is_row_already_identified_with_cadet(
    row: RowInRegistrationData, interface: abstractInterface
) -> bool:
    event = get_event_from_state(interface)
    row_id_has_identified_cadet = is_row_in_event_already_identified_with_cadet(
        object_store=interface.object_store, row=row, event=event
    )

    return row_id_has_identified_cadet


def process_next_row_with_cadet_from_row(
    interface: abstractInterface,
    cadet: Cadet,
) -> Form:
    try:
        matched_cadet_with_id = get_matching_cadet(
            object_store=interface.object_store, cadet=cadet
        )
    except MissingData:
        ## New cadet
        print("Cadet %s not matched" % str(cadet))
        return process_row_when_cadet_unmatched(interface=interface, cadet=cadet)
    except Exception as e:
        ## can happen in corner case
        interface.log_error(
            "Error %s when trying to match cadet %s automatically - have to do it manually"
            % (str(e), str(cadet))
        )
        return process_row_when_cadet_unmatched(interface=interface, cadet=cadet)

    print("Cadet %s matched id is %s" % (str(cadet), matched_cadet_with_id.id))
    return process_row_when_cadet_matched(
        interface=interface, cadet=matched_cadet_with_id
    )


def process_row_when_cadet_matched(interface: abstractInterface, cadet: Cadet) -> Form:
    event = get_event_from_state(interface)
    row_id = get_current_row_id(interface)
    print("adding matched row %s with id %s" % (row_id, cadet.id))
    add_identified_cadet_and_row(
        object_store=interface.object_store, event=event, row_id=row_id, cadet=cadet
    )
    interface.flush_cache_to_store()
    ## run recursively until no more data
    return identify_cadets_on_next_row(interface)


def process_row_when_cadet_unmatched(
    interface: abstractInterface,
    cadet: Cadet,
) -> Form:
    very_similar_cadet = does_a_very_similar_cadet_exist_if_not_return_missing_data(interface, cadet=cadet)
    if very_similar_cadet is missing_data:
        return process_row_when_cadet_completely_unmatched(interface=interface, cadet=cadet)
    else:
        interface.log_error("Found cadet %s, looks a very close match for %s in registration data. If not correct, replace in edit registration page."
                             % (very_similar_cadet, cadet))
        return process_row_when_cadet_matched(interface=interface, cadet=very_similar_cadet)


def does_a_very_similar_cadet_exist_if_not_return_missing_data(interface: abstractInterface, cadet:Cadet) -> Cadet:
    similar_cadets = get_list_of_very_similar_cadets_from_data(object_store=interface.object_store, cadet=cadet)
    if len(similar_cadets)==1:
        return similar_cadets[0]

    return missing_data

def process_row_when_cadet_completely_unmatched(
    interface: abstractInterface,
    cadet: Cadet,
) -> Form:
    parameters_to_get_or_select_cadet = get_parameters_for_form(interface)

    return get_add_or_select_existing_cadet_form(
        cadet=cadet,
        interface=interface,
        parameters=parameters_to_get_or_select_cadet
    )



def get_parameters_for_form(interface: abstractInterface):
    parameters_to_get_or_select_cadet = ParametersForGetOrSelectCadetForm(
        header_text=header_text_for_form(interface),
        help_string="identify_cadets_at_event_help",
        skip_button=True
    )

    return parameters_to_get_or_select_cadet

def header_text_for_form(interface: abstractInterface) -> ListOfLines:

    default_header_text = [
        ProgressBar('Identifying cadets in registration data', percentage_of_row_ids_done_in_registration_file(interface)),
        HorizontalLine(),
        "Looks like a new cadet in the WA entry file. ",
        "You can edit them, check their details and then add, or choose an existing cadet instead (avoid creating duplicates! If the existing cadet details are wrong, select them for now and edit later) \n\n ",
        "If this is a test entry, then click SKIP"
    ]

    return ListOfLines(default_header_text).add_Lines()




def post_form_add_cadet_ids_during_import(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    parameters_to_get_or_select_cadet = get_parameters_for_form(interface)

    result = generic_post_response_to_add_or_select_cadet(
        interface=interface,
        parameters=parameters_to_get_or_select_cadet
    )
    if result.is_form:
        return result.form

    elif result.skip:
        return process_form_when_skipping_cadet(interface)


    elif result.is_cadet:
        cadet = result.cadet
        assert type(cadet) is Cadet
        return process_row_when_cadet_matched(interface=interface, cadet=cadet)
    else:
        raise Exception("Can't handle result %s" % str(result))



def process_form_when_skipping_cadet(interface: abstractInterface) -> Form:
    event = get_event_from_state(interface)
    row_id = get_current_row_id(interface)
    print("adding skip row %s" % (row_id))

    mark_row_as_skip_cadet(
        event=event, row_id=row_id, object_store=interface.object_store
    )

    interface.flush_cache_to_store()
    ## run recursively until no more data
    return identify_cadets_on_next_row(interface)



