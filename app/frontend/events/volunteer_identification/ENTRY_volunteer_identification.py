from typing import Union

from app.backend.events.event_warnings import (
    add_new_event_warning_checking_for_duplicate,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import (
    _______________,
    ListOfLines,
    ProgressBar,
    HorizontalLine,
)
from app.backend.volunteers.list_of_volunteers import (
    get_volunteer_with_matching_name,
    single_very_similar_volunteer_or_missing_data,
)
from app.backend.registration_data.identified_volunteers_at_event import (
    volunteer_for_this_row_and_index_already_identified_or_permanently_skipped,
    add_identified_volunteer,
    mark_volunteer_as_skipped_permanently,
    mark_volunteer_as_skipped_for_now,
)
from app.backend.registration_data.volunter_relevant_information import (
    get_volunteer_from_relevant_information,
)
from app.backend.registration_data.identified_cadets_at_event import (
    is_cadet_marked_as_skip_in_for_row_in_raw_registration_data,
)
from app.frontend.shared.add_or_select_volunteer import (
    ParametersForGetOrSelectVolunteerForm,
    get_add_or_select_existing_volunteer_form,
    generic_post_response_to_add_or_select_volunteer,
)

from app.frontend.shared.events_state import get_event_from_state
from app.frontend.events.import_data.shared_state_tracking_and_data import (
    get_and_save_next_row_id_in_raw_registration_data,
    clear_row_in_state,
    get_current_row_id,
    percentage_of_row_ids_done_in_registration_file,
)
from app.frontend.events.volunteer_identification.track_state_in_volunteer_allocation import (
    clear_volunteer_index,
    get_and_save_next_volunteer_index,
    get_relevant_information_for_current_volunteer,
    get_volunteer_index,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.objects.cadets import Cadet
from app.objects.event_warnings import (
    VOLUNTEER_IDENTITY,
)
from app.data_access.configuration.fixed import MEDIUM_PRIORITY, HIGH_PRIORITY

from app.objects.utilities.exceptions import NoMoreData, arg_not_passed, missing_data
from app.objects.relevant_information_for_volunteers import (
    missing_relevant_information,
)
from app.objects.volunteers import Volunteer


### First pass- loop over mapped data and identify volunteers
### Identified volunteer data object with row_id (include row data, volunteer index)


def display_form_volunteer_identification(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    ## this only happens once, the rest of the time is a post call
    print("Reset volunteer row ID")
    clear_row_in_state(interface)

    return process_volunteer_on_next_row_of_event_data(interface)


def process_volunteer_on_next_row_of_event_data(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    print("Looping through identifying master event data volunteers")
    try:
        get_and_save_next_row_id_in_raw_registration_data(interface)
    except NoMoreData:
        clear_row_in_state(interface)
        print("Finished looping - next stage is to add details")
        return interface.get_new_display_form_for_parent_of_function(
            display_form_volunteer_identification
        )

    return identify_volunteers_in_specific_row_initialise(interface=interface)


def identify_volunteers_in_specific_row_initialise(
    interface: abstractInterface,
) -> NewForm:
    print("Parsing row %s" % get_current_row_id(interface))
    cadet_skip = (
        is_cadet_marked_as_test_cadet_to_skip_in_for_current_row_in_mapped_data(
            interface
        )
    )
    if cadet_skip:
        return process_volunteer_on_next_row_of_event_data(interface)

    print("Clearing volunteer index within row")
    clear_volunteer_index(interface)

    return next_volunteer_in_current_row(interface)


def is_cadet_marked_as_test_cadet_to_skip_in_for_current_row_in_mapped_data(
    interface: abstractInterface,
):
    current_row_id = get_current_row_id(interface)
    event = get_event_from_state(interface)
    cadet_skip = is_cadet_marked_as_skip_in_for_row_in_raw_registration_data(
        object_store=interface.object_store, row_id=current_row_id, event=event
    )
    if cadet_skip:
        print(
            "Cadet registration marked as temporary or permanent skip - not processing volunteers for now in this row"
        )

    return cadet_skip


def next_volunteer_in_current_row(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        get_and_save_next_volunteer_index(interface)
    except NoMoreData:
        print("End of current row, on to next row")
        clear_volunteer_index(interface)
        return process_volunteer_on_next_row_of_event_data(interface)

    print(
        "Now on %s row, index %s"
        % (get_current_row_id(interface), get_volunteer_index(interface))
    )

    if current_volunteer_already_identified(interface):
        return next_volunteer_in_current_row(interface)
    else:
        print("Not identified - adding new volunteer")
        return add_specific_volunteer_at_event(interface=interface)


def current_volunteer_already_identified(interface: abstractInterface):
    current_row_id = get_current_row_id(interface)
    current_index = get_volunteer_index(interface)
    event = get_event_from_state(interface)

    already_identified = (
        volunteer_for_this_row_and_index_already_identified_or_permanently_skipped(
            object_store=interface.object_store,
            event=event,
            row_id=current_row_id,
            volunteer_index=current_index,
        )
    )
    if already_identified:
        print(
            "Row %s index %s is already identified (or permanently skipped)"
            % (current_row_id, current_index)
        )

    return already_identified


def add_specific_volunteer_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    relevant_information = get_relevant_information_for_current_volunteer(interface)
    volunteer = get_volunteer_from_relevant_information(relevant_information)
    if volunteer is missing_relevant_information:
        print(
            "Relevant information was missing - cannot identify - most probably blank second volunteer"
        )

        return next_volunteer_in_current_row(interface)

    print("Relevant information was %s" % str(relevant_information))

    return add_passed_volunteer_at_event(interface=interface, volunteer=volunteer)


def add_passed_volunteer_at_event(
    interface: abstractInterface, volunteer: Volunteer
) -> Union[Form, NewForm]:
    matched_volunteer_with_id = get_volunteer_with_matching_name(
        object_store=interface.object_store, volunteer=volunteer, default=missing_data
    )
    if matched_volunteer_with_id is missing_data:
        print("Volunteer %s not matched precisely" % str(volunteer))
        return add_passed_volunteer_if_very_similar_or_display_form_if_not(
            interface=interface, volunteer=volunteer
        )

    print(
        "Volunteer %s matched precisely with  %s"
        % (str(volunteer), matched_volunteer_with_id.id)
    )
    return process_identification_when_volunteer_matched(
        interface=interface, volunteer=matched_volunteer_with_id
    )


def add_passed_volunteer_if_very_similar_or_display_form_if_not(
    interface: abstractInterface, volunteer: Volunteer
) -> Union[Form, NewForm]:
    very_similar_volunteer = single_very_similar_volunteer_or_missing_data(
        interface.object_store, volunteer=volunteer
    )
    very_similar_volunteer_exists = not very_similar_volunteer is missing_data

    if very_similar_volunteer_exists:
        log_very_similar_volunteer(
            interface=interface,
            volunteer=volunteer,
            matching_volunteer=very_similar_volunteer,
        )
        return process_identification_when_volunteer_matched(
            interface=interface, volunteer=very_similar_volunteer
        )
    else:
        print(
            "Volunteer %s not matched with single similar volunteer, going to form"
            % str(volunteer)
        )
        return display_volunteer_selection_form(
            interface=interface, volunteer=volunteer
        )


def log_very_similar_volunteer(
    interface: abstractInterface, volunteer: Volunteer, matching_volunteer: Volunteer
):
    interface.log_error(
        "Volunteer %s is very similar to one in form %s, adding automatically. Go to rota to change if problematic."
        % (matching_volunteer, volunteer)
    )
    warning = (
        "Assumed volunteer %s was identical to volunteer %s in registration data"
        % (matching_volunteer, volunteer)
    )
    print(warning)
    add_new_event_warning_checking_for_duplicate(
        object_store=interface.object_store,
        event=get_event_from_state(interface),
        warning=warning,
        category=VOLUNTEER_IDENTITY,
        priority=HIGH_PRIORITY,
        auto_refreshed=False,
    )  ## warning will sit on system until cleared


def display_volunteer_selection_form(
    interface: abstractInterface, volunteer: Volunteer
):
    cadet_in_row = get_cadet_or_missing_data_for_current_row(interface)
    if cadet_in_row is missing_data:
        cadet_in_row = arg_not_passed
    parameters = get_form_parameters(interface)

    return get_add_or_select_existing_volunteer_form(
        interface=interface,
        volunteer=volunteer,
        cadet=cadet_in_row,
        parameters=parameters,
    )


def get_form_parameters(
    interface: abstractInterface,
) -> ParametersForGetOrSelectVolunteerForm:
    header_text = get_header_text_for_volunteer_selection_form(interface=interface)
    parameters_for_form = ParametersForGetOrSelectVolunteerForm(
        header_text=header_text,
        help_string="identify_volunteers_at_event_help",
        extra_buttons=[permanent_skip_button, temporary_skip_button],
    )
    return parameters_for_form


permanent_skip_button = Button(
    "Skip permanently- this isn't a volunteer or parent on site"
)
temporary_skip_button = Button("Skip for now and import later")


def get_cadet_or_missing_data_for_current_row(interface: abstractInterface) -> Cadet:
    relevant_information = get_relevant_information_for_current_volunteer(interface)

    return relevant_information.identify.cadet


def post_form_volunteer_identification(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    parameters = get_form_parameters(interface)

    result = generic_post_response_to_add_or_select_volunteer(
        interface=interface, parameters=parameters
    )
    if result.is_button:
        if result.button_pressed == temporary_skip_button:
            return action_when_temporarily_skipping_volunteer(interface)
        elif result.button_pressed == permanent_skip_button:
            return action_when_permanently_skipping_volunteer(interface)
        else:
            return button_error_and_back_to_initial_state_form(interface)
    elif result.is_form:
        return result.form
    elif result.is_volunteer:
        volunteer = result.volunteer
        return process_identification_when_volunteer_matched(
            interface=interface, volunteer=volunteer
        )
    else:
        raise Exception("Can't hanlde result %s" % str(result))


def action_when_permanently_skipping_volunteer(interface: abstractInterface) -> NewForm:
    event = get_event_from_state(interface)
    current_row_id = get_current_row_id(interface)
    current_index = get_volunteer_index(interface)

    print(
        "Permanently skipping volunteer row %s id %d as identified for event %s"
        % (str(current_row_id), current_index, str(event))
    )

    mark_volunteer_as_skipped_permanently(
        object_store=interface.object_store,
        event=event,
        row_id=current_row_id,
        volunteer_index=int(current_index),
    )

    return next_volunteer_in_current_row(interface)


def action_when_temporarily_skipping_volunteer(interface: abstractInterface) -> NewForm:
    event = get_event_from_state(interface)
    current_row_id = get_current_row_id(interface)
    current_index = get_volunteer_index(interface)

    print(
        "Temporarily skipping volunteer row %s id %d as identified for event %s"
        % (str(current_row_id), current_index, str(event))
    )

    mark_volunteer_as_skipped_for_now(
        object_store=interface.object_store,
        event=event,
        row_id=current_row_id,
        volunteer_index=int(current_index),
    )

    return next_volunteer_in_current_row(interface)


def process_identification_when_volunteer_matched(
    interface: abstractInterface, volunteer: Volunteer
) -> Union[Form, NewForm]:
    event = get_event_from_state(interface)

    current_row_id = get_current_row_id(interface)
    current_index = get_volunteer_index(interface)

    print(
        "Adding volunteer %s as identified for event %s, row_id %s, volunteer index %d"
        % (str(volunteer), str(event), current_row_id, current_index)
    )
    try:
        add_identified_volunteer(
            object_store=interface.object_store,
            volunteer=volunteer,
            event=event,
            row_id=current_row_id,
            volunteer_index=int(current_index),
        )
    except Exception as e:
        interface.log_error(
            "Error adding volunteer %s (code %s) to identified volunteers list; you might need to add them manually check the rota."
            % (volunteer.name, str(e))
        )

    interface.flush_cache_to_store()

    return next_volunteer_in_current_row(interface)


def get_header_text_for_volunteer_selection_form(
    interface: abstractInterface,
) -> ListOfLines:
    # Custom header text
    progress_bar = ProgressBar(
        "Identifying volunteers in registration data",
        percentage_of_row_ids_done_in_registration_file(interface),
    )
    relevant_information = get_relevant_information_for_current_volunteer(interface)
    relevant_information_for_identification = relevant_information.identify

    status_text = relevant_information_for_identification.self_declared_status
    other_information = "Other information in form: " + str(
        relevant_information_for_identification.any_other_information
    )
    if len(status_text) > 0:
        status_text = "Registration volunteer status in form: %s" % status_text

    volunteer_index = get_volunteer_index(interface)
    cadet = relevant_information_for_identification.cadet

    introduction = (
        "Looks like a potential new volunteer in the WA entry file for cadet: %s, volunteer number %d"
        % (str(cadet), volunteer_index + 1)
    )

    header_text = ListOfLines(
        [
            progress_bar,
            HorizontalLine(),
            _______________,
            introduction,
            _______________,
            status_text,
            other_information,
            _______________,
            "You can edit them, check their details and then add, or choose an existing volunteer instead. ",
            "(Avoid creating duplicates! If the existing volunteer details are wrong, select them for now and edit later).",
            "Skip . Skip an import later",
        ]
    )

    return header_text
