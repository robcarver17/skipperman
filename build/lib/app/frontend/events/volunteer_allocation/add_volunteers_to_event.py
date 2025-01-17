from typing import Union

from app.objects.volunteers import Volunteer

from app.objects.relevant_information_for_volunteers import (
    ListOfRelevantInformationForVolunteer,
    relevant_information_requires_clarification,
    NO_ISSUES_WITH_VOLUNTEER,
)

from app.backend.registration_data.identified_volunteers_at_event import (
    get_list_of_relevant_information_for_volunteer_in_registration_data,
)
from app.backend.registration_data.cadet_and_volunteer_connections_at_event import (
    update_cadet_connections_when_volunteer_already_at_event,
    are_all_cadets_associated_with_volunteer_in_registration_data_cancelled_or_deleted,
    get_list_of_active_associated_cadets_in_mapped_event_data_given_identified_volunteer,
)
from app.backend.volunteers.volunteers_at_event import (
    get_volunteer_at_event_from_list_of_relevant_information_with_no_conflicts,
    add_volunteer_at_event,
)
from app.backend.registration_data.volunteer_registration_data import (
    is_volunteer_already_at_event,
)
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.events.volunteer_allocation.add_volunteers_process_form import (
    add_volunteer_at_event_with_form_contents,
)
from app.frontend.events.volunteer_allocation.track_state_in_volunteer_allocation import (
    clear_volunteer_id_at_event_in_state,
    get_and_save_next_volunteer_id_in_mapped_event_data,
    get_current_volunteer_at_event,
)
from app.frontend.events.volunteer_allocation.add_volunteer_to_event_form_contents import (
    display_form_to_confirm_volunteer_details,
    save_button,
    do_not_add_volunteer,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.exceptions import NoMoreData
from app.objects.events import Event
from app.frontend.form_handler import button_error_and_back_to_initial_state_form


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


def return_to_controller(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(
        display_add_volunteers_to_event
    )


def process_identified_volunteer_at_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:

    volunteer = get_current_volunteer_at_event(interface)
    event = get_event_from_state(interface)
    all_cancelled = are_all_cadets_associated_with_volunteer_in_registration_data_cancelled_or_deleted(
        object_store=interface.object_store, event=event, volunteer=volunteer
    )

    if all_cancelled:
        ### We don't add a volunteer here
        ### But we also don't auto delete an existing volunteer, in case the volunteer staying on has other associated cadets. If a volunteer does already exist, then the cancellation will be picked up when we next look at the volunteer rota
        return next_volunteer_in_event(interface)
    else:
        return process_identified_volunteer_at_event_with_valid_registered_cadets(
            interface=interface, event=event, volunteer=volunteer
        )


def process_identified_volunteer_at_event_with_valid_registered_cadets(
    interface: abstractInterface, event: Event, volunteer: Volunteer
) -> Union[Form, NewForm]:

    already_added = is_volunteer_already_at_event(
        object_store=interface.object_store, event=event, volunteer=volunteer
    )
    if already_added:
        update_cadet_connections_when_volunteer_already_at_event(
            object_store=interface.object_store, event=event, volunteer=volunteer
        )
        interface.flush_cache_to_store()
        return next_volunteer_in_event(interface)

    else:
        return process_new_volunteer_at_event_with_active_cadets(
            interface=interface, event=event, volunteer=volunteer
        )


def process_new_volunteer_at_event_with_active_cadets(
    interface: abstractInterface, event: Event, volunteer: Volunteer
) -> Union[Form, NewForm]:
    ## New volunteer with cadets
    list_of_relevant_information = (
        get_list_of_relevant_information_for_volunteer_in_registration_data(
            object_store=interface.object_store, event=event, volunteer=volunteer
        )
    )
    issues_with_volunteer = relevant_information_requires_clarification(
        list_of_relevant_information=list_of_relevant_information,
        volunteer=volunteer,
    )

    if issues_with_volunteer == NO_ISSUES_WITH_VOLUNTEER:
        print("Volunteer %s has no issues, adding automatically" % volunteer)
        return process_new_volunteer_at_event_with_active_cadets_and_where_no_manual_intervention_required(
            interface=interface,
            event=event,
            list_of_relevant_information=list_of_relevant_information,
            volunteer=volunteer,
        )
    else:
        interface.log_error(issues_with_volunteer)
        return display_form_to_confirm_volunteer_details(
            interface=interface, volunteer=volunteer, event=event
        )


def process_new_volunteer_at_event_with_active_cadets_and_where_no_manual_intervention_required(
    interface: abstractInterface,
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer: Volunteer,
    event: Event,
) -> Union[Form, NewForm]:
    list_of_associated_cadets = get_list_of_active_associated_cadets_in_mapped_event_data_given_identified_volunteer(
        object_store=interface.object_store, volunteer=volunteer, event=event
    )
    volunteer_at_event = (
        get_volunteer_at_event_from_list_of_relevant_information_with_no_conflicts(
            list_of_relevant_information=list_of_relevant_information,
            volunteer=volunteer,
            list_of_associated_cadets=list_of_associated_cadets,
        )
    )

    add_volunteer_at_event(
        object_store=interface.object_store,
        event=event,
        volunteer_at_event=volunteer_at_event,
    )
    update_cadet_connections_when_volunteer_already_at_event(
        object_store=interface.object_store, event=event, volunteer=volunteer
    )

    interface.flush_cache_to_store()
    return next_volunteer_in_event(interface)


def post_form_add_volunteers_to_event(interface: abstractInterface):
    last_button = interface.last_button_pressed()
    if save_button.pressed(last_button):
        add_volunteer_at_event_with_form_contents(interface)
        interface.flush_cache_to_store()
    elif do_not_add_volunteer.pressed(last_button):
        pass
    else:
        return button_error_and_back_to_initial_state_form(interface)

    return next_volunteer_in_event(interface)
