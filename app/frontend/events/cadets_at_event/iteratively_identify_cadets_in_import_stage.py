from typing import Union

from app.backend.cadets.list_of_cadets import (
    get_matching_cadet,
    get_list_of_very_similar_cadets_from_data,
)
from app.backend.events.event_warnings import (
    add_new_event_warning_checking_for_duplicate,
)
from app.objects.abstract_objects.abstract_buttons import Button

from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    ProgressBar,
    HorizontalLine,
    DetailListOfLines,
    Line,
)

from app.backend.registration_data.raw_mapped_registration_data import (
    get_row_in_raw_registration_data_given_id,
    get_cadet_data_from_row_of_registration_data_no_checks,
)
from app.backend.registration_data.identified_cadets_at_event import (
    is_row_in_event_already_identified_with_cadet_or_permanently_skipped,
    add_identified_cadet_and_row,
    mark_row_as_permanently_skip_cadet,
    mark_row_as_temporarily_skip_cadet,
)

from app.frontend.shared.events_state import get_event_from_state

from app.frontend.events.import_data.shared_state_tracking_and_data import (
    get_and_save_next_row_id_in_raw_registration_data,
    get_current_row_id,
    clear_row_in_state,
    percentage_of_row_ids_done_in_registration_file,
)

from app.frontend.shared.get_or_select_cadet_forms import (
    get_add_or_select_existing_cadet_form,
    ParametersForGetOrSelectCadetForm,
    generic_post_response_to_add_or_select_cadet,
)
from app.objects.event_warnings import (
    CADET_IDENTITY,
    HIGH_PRIORITY,
    CADET_REGISTRATION,
    LOW_PRIORITY,
)
from app.objects.events import Event
from app.objects.utilities.cadet_matching_and_sorting import SORT_BY_SIMILARITY_BOTH

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
    row_id_has_identified_cadet = (
        is_row_already_identified_with_cadet_including_permanent_skips(
            row=row, interface=interface
        )
    )
    if row_id_has_identified_cadet:
        print(
            "Row id %s already identified with a cadet or permanently skipped"
            % row.row_id
        )
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


def is_row_already_identified_with_cadet_including_permanent_skips(
    row: RowInRegistrationData, interface: abstractInterface
) -> bool:
    event = get_event_from_state(interface)
    row_id_has_identified_cadet = (
        is_row_in_event_already_identified_with_cadet_or_permanently_skipped(
            object_store=interface.object_store, row=row, event=event
        )
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
        print("Cadet %s not perfectly matched" % str(cadet))
        return process_row_when_cadet_unmatched(interface=interface, cadet=cadet)
    except Exception as e:
        ## can happen in corner case
        interface.log_error(
            "Error %s when trying to match cadet %s automatically - have to do it manually"
            % (str(e), str(cadet))
        )
        return process_row_when_cadet_unmatched(interface=interface, cadet=cadet)

    print(
        "Cadet %s perfectly matched id is %s" % (str(cadet), matched_cadet_with_id.id)
    )
    return process_row_when_cadet_matched(
        interface=interface, cadet=matched_cadet_with_id
    )


def process_row_when_cadet_matched(interface: abstractInterface, cadet: Cadet) -> Form:
    event = get_event_from_state(interface)
    row_id = get_current_row_id(interface)
    print(
        "adding matched row %s with cadet id %s for cadet %s"
        % (row_id, cadet.id, str(cadet))
    )
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
    very_similar_cadet = does_a_very_similar_cadet_exist_if_not_return_missing_data(
        interface, cadet=cadet
    )
    matched_with_similar = not very_similar_cadet is missing_data
    if matched_with_similar:
        log_when_cadet_matched_with_similar(
            interface=interface, cadet=cadet, very_similar_cadet=very_similar_cadet
        )
        return process_row_when_cadet_matched(
            interface=interface, cadet=very_similar_cadet
        )
    else:
        print("Completely unmatched going to form")
        return process_row_when_cadet_completely_unmatched(
            interface=interface, cadet=cadet
        )


def does_a_very_similar_cadet_exist_if_not_return_missing_data(
    interface: abstractInterface, cadet: Cadet
) -> Cadet:
    similar_cadets = get_list_of_very_similar_cadets_from_data(
        object_store=interface.object_store, cadet=cadet
    )
    if len(similar_cadets) == 1:
        return similar_cadets[0]

    return missing_data


def log_when_cadet_matched_with_similar(
    interface: abstractInterface, cadet: Cadet, very_similar_cadet: Cadet
):
    message = (
        "Found cadet %s, looks a very close match for %s in registration data. If not correct, replace in edit registration page; otherwise click ignore in warnings there"
        % (very_similar_cadet, cadet)
    )
    interface.log_error(message)
    print(message)
    warning = "Assumed cadet %s was identical to cadet %s in registration data." % (
        very_similar_cadet,
        cadet,
    )
    add_new_event_warning_checking_for_duplicate(
        object_store=interface.object_store,
        event=get_event_from_state(interface),
        warning=warning,
        category=CADET_IDENTITY,
        priority=HIGH_PRIORITY,
        auto_refreshed=False,
    )  ## warning will sit on system until cleared


def process_row_when_cadet_completely_unmatched(
    interface: abstractInterface,
    cadet: Cadet,
) -> Form:
    parameters_to_get_or_select_cadet = get_parameters_for_form(interface)

    return get_add_or_select_existing_cadet_form(
        cadet=cadet, interface=interface, parameters=parameters_to_get_or_select_cadet
    )


def get_parameters_for_form(interface: abstractInterface):
    parameters_to_get_or_select_cadet = ParametersForGetOrSelectCadetForm(
        header_text=header_text_for_form(interface),
        help_string="identify_cadets_at_event_help",
        extra_buttons=[permanent_skip_button, temporary_skip_button],
        sort_by=SORT_BY_SIMILARITY_BOTH,
    )

    return parameters_to_get_or_select_cadet


temporary_skip_button = Button("Skip for now and import later")
permanent_skip_button = Button(
    "Skip permanently - this is a test row and not a registration"
)


def header_text_for_form(interface: abstractInterface) -> ListOfLines:
    event = get_event_from_state(interface)
    row_id = get_current_row_id(interface)
    row = get_row_in_raw_registration_data_given_id(
        object_store=interface.object_store, event=event, row_id=row_id
    )
    reg_details = DetailListOfLines(
        ListOfLines(["Registration details: %s" % str(row)]),
        name="Click to see full registration details",
    )
    default_header_text = ListOfLines(
        [
            ProgressBar(
                "Identifying cadets in registration data",
                percentage_of_row_ids_done_in_registration_file(interface),
            ),
            HorizontalLine(),
            Line("Looks like a new cadet in the WA entry file. "),
            Line(
                "You can edit them, check their details and then add, or choose an existing cadet instead (avoid creating duplicates! If the existing cadet details are wrong, select them for now and edit later)"
            ),
            Line(
                "If this is a test entry, then click 'Skip permanently'- you won't be asked to identify this cadet again. If you want to import this cadet later, click 'Skip for now'"
            ),
            reg_details,
        ]
    )

    return default_header_text


def post_form_add_cadet_ids_during_import(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    parameters_to_get_or_select_cadet = get_parameters_for_form(interface)

    result = generic_post_response_to_add_or_select_cadet(
        interface=interface, parameters=parameters_to_get_or_select_cadet
    )
    if result.is_form:
        return result.form

    elif result.is_button:
        if result.button_pressed == temporary_skip_button:
            return process_form_when_skipping_cadet_temporarily(interface)
        elif result.button_pressed == permanent_skip_button:
            return process_form_when_skipping_cadet_permanently(interface)

    elif result.is_cadet:
        cadet = result.cadet
        assert type(cadet) is Cadet

        return process_row_when_cadet_matched(interface=interface, cadet=cadet)
    else:
        raise Exception("Can't handle result %s" % str(result))


def process_form_when_skipping_cadet_permanently(interface: abstractInterface) -> Form:
    event = get_event_from_state(interface)
    row_id = get_current_row_id(interface)

    mark_row_as_permanently_skip_cadet(
        event=event, row_id=row_id, object_store=interface.object_store
    )
    log_warning_when_skipping_permanently(interface, row_id=row_id, event=event)
    interface.flush_cache_to_store()
    ## run recursively until no more data
    return identify_cadets_on_next_row(interface)


def log_warning_when_skipping_permanently(
    interface: abstractInterface, row_id: str, event: Event
):
    row = get_row_in_raw_registration_data_given_id(
        object_store=interface.object_store, event=event, row_id=row_id
    )
    cadet = get_cadet_data_from_row_of_registration_data_no_checks(row)

    warning = "Permanently skipping cadet %s row id %s" % (cadet.name, row_id)

    add_new_event_warning_checking_for_duplicate(
        object_store=interface.object_store,
        event=get_event_from_state(interface),
        warning=warning,
        category=CADET_REGISTRATION,
        priority=LOW_PRIORITY,
        auto_refreshed=False,
    )  ## warning will sit on system until cleared
    print(warning)
    interface.log_error(warning)


def process_form_when_skipping_cadet_temporarily(interface: abstractInterface) -> Form:
    event = get_event_from_state(interface)
    row_id = get_current_row_id(interface)
    print("temporary skip of cadet at row id %s" % row_id)
    ## no warning as picked up
    mark_row_as_temporarily_skip_cadet(
        event=event, row_id=row_id, object_store=interface.object_store
    )

    return identify_cadets_on_next_row(interface)
