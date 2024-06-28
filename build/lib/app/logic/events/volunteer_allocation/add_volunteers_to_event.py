from typing import Union

from app.objects.relevant_information_for_volunteers import (
    ListOfRelevantInformationForVolunteer,
)

from app.backend.volunteers.volunteer_allocation import (
    update_cadet_connections_when_volunteer_already_at_event,
    are_all_connected_cadets_cancelled_or_deleted,
    get_list_of_relevant_information,
    relevant_information_requires_clarification_or_cadets_not_permanently_connected,
    add_volunteer_at_event,
    get_volunteer_at_event_from_list_of_relevant_information_with_no_conflicts,
    NO_ISSUES_WITH_VOLUNTEER,
    get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet,
)
from app.backend.volunteers.volunteers import get_volunteer_from_id
from app.backend.volunteers.volunteer_rota import is_volunteer_already_at_event
from app.logic.events.events_in_state import get_event_from_state
from app.logic.events.volunteer_allocation.add_volunteers_process_form import (
    add_volunteer_at_event_with_form_contents,
)
from app.logic.events.volunteer_allocation.track_state_in_volunteer_allocation import (
    clear_volunteer_id_at_event_in_state,
    get_and_save_next_volunteer_id_in_mapped_event_data,
    get_current_volunteer_id_at_event,
)
from app.logic.events.volunteer_allocation.add_volunteer_to_event_form_contents import (
    get_header_text,
    get_connection_checkbox,
    get_availablity_text,
    get_availability_checkbox_for_volunteer_at_event_based_on_relevant_information,
    get_any_other_information_text,
    get_preferred_duties_text,
    get_preferred_duties_input,
    get_same_or_different_text,
    get_same_or_different_input,
    get_notes_input_for_volunteer_at_event,
    get_any_self_declared_status_text,
)
from app.logic.events.constants import *
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.constants import NoMoreData
from app.objects.events import Event


def display_add_volunteers_to_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    clear_volunteer_id_at_event_in_state(interface)

    return next_volunteer_in_event(interface)


def next_volunteer_in_event(interface: abstractInterface) -> Union[Form, NewForm]:
    try:
        get_and_save_next_volunteer_id_in_mapped_event_data(interface)
    except NoMoreData:
        clear_volunteer_id_at_event_in_state(interface)
        return return_to_controller(interface)

    return process_identified_volunteer_at_event(interface)


def process_identified_volunteer_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    volunteer_id = get_current_volunteer_id_at_event(interface)
    event = get_event_from_state(interface)
    already_added = is_volunteer_already_at_event(
        interface=interface, volunteer_id=volunteer_id, event=event
    )
    all_cancelled = are_all_connected_cadets_cancelled_or_deleted(
        interface=interface, volunteer_id=volunteer_id, event=event
    )

    if all_cancelled:
        ### We don't add a volunteer here
        ### But we also don't auto delete, in case the volunteer staying on has other associated cadets. If a volunteer does already exist, then the cancellation will be picked up when we next look at the volunteer rota
        return next_volunteer_in_event(interface)
    elif already_added:
        update_cadet_connections_when_volunteer_already_at_event(
            interface=interface, event=event, volunteer_id=volunteer_id
        )
        interface._DONT_CALL_DIRECTLY_USE_FLUSH_save_stored_items()

        return next_volunteer_in_event(interface)
    else:
        return process_new_volunteer_at_event_with_active_cadets(
            interface=interface, event=event, volunteer_id=volunteer_id
        )


def process_new_volunteer_at_event_with_active_cadets(
    interface: abstractInterface, volunteer_id: str, event: Event
) -> Union[Form, NewForm]:
    ## New volunteer with cadets
    list_of_relevant_information = get_list_of_relevant_information(
        volunteer_id=volunteer_id, event=event, interface=interface
    )
    issues_with_volunteer = (
        relevant_information_requires_clarification_or_cadets_not_permanently_connected(
            interface=interface,
            list_of_relevant_information=list_of_relevant_information,
            event=event,
            volunteer_id=volunteer_id,
        )
    )

    if issues_with_volunteer == NO_ISSUES_WITH_VOLUNTEER:
        print(
            "Volunteer %s has no issues, adding automatically"
            % get_volunteer_from_id(interface=interface, volunteer_id=volunteer_id)
        )
        return process_new_volunteer_at_event_with_active_cadets_and_where_no_manual_intervention_required(
            interface=interface,
            event=event,
            list_of_relevant_information=list_of_relevant_information,
            volunteer_id=volunteer_id,
        )
    else:
        interface.log_error(issues_with_volunteer)
        return display_form_for_volunteer_details(
            interface=interface, volunteer_id=volunteer_id, event=event
        )


def process_new_volunteer_at_event_with_active_cadets_and_where_no_manual_intervention_required(
    interface: abstractInterface,
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer_id: str,
    event: Event,
) -> Union[Form, NewForm]:
    list_of_cadet_ids = get_list_of_active_associated_cadet_id_in_mapped_event_data_given_identified_volunteer_and_cadet(
        interface=interface, volunteer_id=volunteer_id, event=event
    )
    volunteer_at_event = (
        get_volunteer_at_event_from_list_of_relevant_information_with_no_conflicts(
            list_of_relevant_information=list_of_relevant_information,
            volunteer_id=volunteer_id,
            list_of_associated_cadet_id=list_of_cadet_ids,
        )
    )

    add_volunteer_at_event(
        interface=interface, event=event, volunteer_at_event=volunteer_at_event
    )

    interface._DONT_CALL_DIRECTLY_USE_FLUSH_save_stored_items()
    return next_volunteer_in_event(interface)


def display_form_for_volunteer_details(
    interface: abstractInterface, volunteer_id: str, event: Event
) -> Form:
    volunteer = get_volunteer_from_id(interface=interface, volunteer_id=volunteer_id)

    list_of_relevant_information = get_list_of_relevant_information(
        volunteer_id=volunteer_id, event=event, interface=interface
    )

    header_text = get_header_text(event=event, volunteer=volunteer, interface=interface)

    connection_checkbox = get_connection_checkbox(
        interface=interface, volunteer=volunteer, event=event
    )

    any_other_information_text = get_any_other_information_text(
        list_of_relevant_information=list_of_relevant_information
    )
    status_text = get_any_self_declared_status_text(
        list_of_relevant_information=list_of_relevant_information
    )

    preferred_duties_text = get_preferred_duties_text(
        list_of_relevant_information=list_of_relevant_information
    )
    preferred_duties_input = get_preferred_duties_input(
        list_of_relevant_information=list_of_relevant_information
    )

    same_or_different_text = get_same_or_different_text(
        list_of_relevant_information=list_of_relevant_information
    )
    same_or_different_input = get_same_or_different_input(
        list_of_relevant_information=list_of_relevant_information
    )

    available_text = get_availablity_text(
        interface=interface, list_of_relevant_information=list_of_relevant_information
    )
    available_checkbox = (
        get_availability_checkbox_for_volunteer_at_event_based_on_relevant_information(
            list_of_relevant_information=list_of_relevant_information, event=event
        )
    )

    notes_input = get_notes_input_for_volunteer_at_event(list_of_relevant_information)

    return Form(
        ListOfLines(
            [
                header_text,
                _______________,
                connection_checkbox,
                _______________,
                status_text,
                _______________,
                available_text.add_Lines(),
                available_checkbox,
                _______________,
                any_other_information_text,
                _______________,
                preferred_duties_text.add_Lines(),
                preferred_duties_input,
                _______________,
                same_or_different_text.add_Lines(),
                same_or_different_input,
                _______________,
                notes_input,
                _______________,
                Line([Button(SAVE_CHANGES), Button(DO_NOT_ADD_VOLUNTEER_LABEL)]),
            ]
        )
    )


DO_NOT_ADD_VOLUNTEER_LABEL = "This volunteer is not available at this event"


def post_form_add_volunteers_to_event(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    if last_button == SAVE_CHANGES:
        add_volunteer_at_event_with_form_contents(interface)
    else:
        pass

    return next_volunteer_in_event(interface)


def return_to_controller(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_add_volunteers_to_event
    )
