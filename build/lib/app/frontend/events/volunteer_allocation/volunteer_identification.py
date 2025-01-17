from typing import Union, Tuple

from app.backend.volunteers.list_of_volunteers import (
    get_volunteer_with_matching_name,
    get_volunteer_from_list_of_given_str_of_volunteer,
)
from app.backend.registration_data.identified_volunteers_at_event import (
    volunteer_for_this_row_and_index_already_identified,
    add_identified_volunteer,
    mark_volunteer_as_skipped,
)
from app.backend.volunteers.add_edit_volunteer import verify_volunteer_and_warn
from app.backend.registration_data.volunter_relevant_information import (
    get_volunteer_from_relevant_information,
)
from app.backend.registration_data.identified_cadets_at_event import (
    is_cadet_marked_as_test_cadet_to_skip_in_for_row_in_raw_registration_data,
)

from app.frontend.shared.events_state import get_event_from_state
from app.frontend.events.import_data.shared_state_tracking_and_data import (
    get_and_save_next_row_id_in_raw_registration_data,
    clear_row_in_state,
    get_current_row_id,
)
from app.frontend.events.volunteer_allocation.track_state_in_volunteer_allocation import (
    clear_volunteer_index,
    get_and_save_next_volunteer_index,
)
from app.frontend.events.volunteer_allocation.volunteer_selection_form_contents import *
from app.frontend.shared.add_edit_volunteer_forms import (
    add_volunteer_from_form_to_data,
    VolunteerAndVerificationText,
    get_add_volunteer_form_with_information_passed,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)

from app.objects.exceptions import NoMoreData, arg_not_passed, MissingData, missing_data
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
    test_row = is_cadet_marked_as_test_cadet_to_skip_in_for_current_row_in_mapped_data(
        interface
    )
    if test_row:
        return process_volunteer_on_next_row_of_event_data(interface)

    print("Clearing volunteer index within row")
    clear_volunteer_index(interface)

    return next_volunteer_in_current_row(interface)


def is_cadet_marked_as_test_cadet_to_skip_in_for_current_row_in_mapped_data(
    interface: abstractInterface,
):
    current_row_id = get_current_row_id(interface)
    event = get_event_from_state(interface)
    return is_cadet_marked_as_test_cadet_to_skip_in_for_row_in_raw_registration_data(
        object_store=interface.object_store, row_id=current_row_id, event=event
    )


def next_volunteer_in_current_row(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        print("next volunteer index")
        get_and_save_next_volunteer_index(interface)
    except NoMoreData:
        clear_volunteer_index(interface)
        return process_volunteer_on_next_row_of_event_data(interface)

    if current_volunteer_already_identified(interface):
        return next_volunteer_in_current_row(interface)
    else:
        return add_specific_volunteer_at_event(interface=interface)


def current_volunteer_already_identified(interface: abstractInterface):
    current_row_id = get_current_row_id(interface)
    current_index = get_volunteer_index(interface)
    event = get_event_from_state(interface)

    return volunteer_for_this_row_and_index_already_identified(
        object_store=interface.object_store,
        event=event,
        row_id=current_row_id,
        volunteer_index=current_index,
    )


def add_specific_volunteer_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    relevant_information = get_relevant_information_for_current_volunteer(interface)
    volunteer = get_volunteer_from_relevant_information(relevant_information)
    if volunteer is missing_relevant_information:
        return next_volunteer_in_current_row(interface)

    return add_passed_volunteer_at_event(interface=interface, volunteer=volunteer)


def add_passed_volunteer_at_event(
    interface: abstractInterface, volunteer: Volunteer
) -> Union[Form, NewForm]:
    try:
        matched_volunteer_with_id = get_volunteer_with_matching_name(
            object_store=interface.object_store, volunteer=volunteer
        )
        if matched_volunteer_with_id is missing_data:
            raise
    except MissingData:
        print("Volunteer %s not matched going to form to identify" % str(volunteer))
        return display_volunteer_selection_form(
            interface=interface, volunteer=volunteer
        )

    print(
        "Volunteer %s matched id is %s" % (str(volunteer), matched_volunteer_with_id.id)
    )
    return process_identification_when_volunteer_matched(
        interface=interface, volunteer=matched_volunteer_with_id
    )


def display_volunteer_selection_form(
    interface: abstractInterface, volunteer: Volunteer
):
    return get_add_or_select_existing_volunteers_form(
        interface=interface,
        see_all_volunteers=False,
        first_time=True,
        volunteer=volunteer,
    )


def get_add_or_select_existing_volunteers_form(
    interface: abstractInterface,
    see_all_volunteers: bool,
    first_time: bool,
    volunteer: Volunteer = arg_not_passed,
) -> Form:
    print("Generating add/select volunteer form")
    print("Passed volunteer %s" % str(volunteer))

    cadet_in_row = get_cadet_or_missing_data_for_current_row(interface)

    volunteer_and_text, include_final_button = get_volunteer_text_and_final_button(
        volunteer=volunteer,
        interface=interface,
        first_time=first_time,
        cadet_in_row=cadet_in_row,
    )
    volunteer = volunteer_and_text.volunteer

    footer_buttons = get_footer_buttons_add_or_select_existing_volunteer_form(
        interface=interface,
        volunteer=volunteer,
        see_all_volunteers=see_all_volunteers,
        include_final_button=include_final_button,
        cadet_in_row=cadet_in_row,
    )
    header_text = get_header_text_for_volunteer_selection_form(interface=interface)

    return get_add_volunteer_form_with_information_passed(
        volunteer_and_text=volunteer_and_text,
        footer_buttons=footer_buttons,
        header_text=header_text,
    )


def get_volunteer_text_and_final_button(
    interface: abstractInterface,
    first_time: bool,
    cadet_in_row: Cadet,  ## could be missing data
    volunteer: Volunteer = arg_not_passed,
) -> Tuple[VolunteerAndVerificationText, bool]:
    verification_text = verify_volunteer_and_warn(
        object_store=interface.object_store, volunteer=volunteer
    )
    could_be_cadet_not_volunteer = volunteer_name_is_similar_to_cadet_name(
        volunteer=volunteer, cadet=cadet_in_row
    )
    if could_be_cadet_not_volunteer:
        verification_text += "Volunteer name is similar to cadet name - are you sure this is actually a volunteer and not a cadet?"

    verification_issues = len(verification_text) > 0

    if verification_issues and first_time:
        include_final_button = False
    else:
        include_final_button = True

    volunteer_and_text = VolunteerAndVerificationText(
        volunteer=volunteer, verification_text=verification_text
    )

    return volunteer_and_text, include_final_button


def get_cadet_or_missing_data_for_current_row(interface: abstractInterface) -> Cadet:
    relevant_information = get_relevant_information_for_current_volunteer(interface)

    return relevant_information.identify.cadet


def post_form_volunteer_identification(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if (
        check_for_me_volunteer_button.pressed(button_pressed)
        or check_confirm_volunteer_button.pressed(button_pressed)
        or see_similar_volunteers_button.pressed(button_pressed)
    ):
        return get_add_or_select_existing_volunteers_form(
            interface=interface, see_all_volunteers=False, first_time=False
        )
    elif add_volunteer_button.pressed(button_pressed):
        return action_when_new_volunteer_to_be_added(interface)

    elif skip_volunteer_button.pressed(button_pressed):
        ## next volunteer
        return action_when_skipping_volunteer(interface)

    elif see_all_volunteers_button.pressed(button_pressed):
        return get_add_or_select_existing_volunteers_form(
            interface=interface, see_all_volunteers=True, first_time=False
        )
    else:
        name_of_volunteer = button_pressed
        return action_when_specific_volunteer_selected(
            name_of_volunteer=name_of_volunteer, interface=interface
        )


def action_when_new_volunteer_to_be_added(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    volunteer = add_volunteer_from_form_to_data(interface)

    return process_identification_when_volunteer_matched(
        interface=interface, volunteer=volunteer
    )


def action_when_skipping_volunteer(interface: abstractInterface) -> NewForm:
    event = get_event_from_state(interface)
    current_row_id = get_current_row_id(interface)
    current_index = get_volunteer_index(interface)

    print(
        "Skipping volunteer row %s id %d as identified for event %s"
        % (str(current_row_id), current_index, str(event))
    )

    mark_volunteer_as_skipped(
        object_store=interface.object_store,
        event=event,
        row_id=current_row_id,
        volunteer_index=int(current_index),
    )

    return next_volunteer_in_current_row(interface)


def action_when_specific_volunteer_selected(
    name_of_volunteer: str, interface: abstractInterface
) -> Union[Form, NewForm]:

    volunteer = get_volunteer_from_list_of_given_str_of_volunteer(
        object_store=interface.object_store,
        volunteer_as_str=name_of_volunteer,
        default=None,
    )
    if volunteer is None:
        raise Exception("Volunteer %s has gone missing!" % name_of_volunteer)

    return process_identification_when_volunteer_matched(
        interface=interface, volunteer=volunteer
    )


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
    add_identified_volunteer(
        object_store=interface.object_store,
        volunteer=volunteer,
        event=event,
        row_id=current_row_id,
        volunteer_index=int(current_index),
    )
    interface.flush_cache_to_store()

    return next_volunteer_in_current_row(interface)
