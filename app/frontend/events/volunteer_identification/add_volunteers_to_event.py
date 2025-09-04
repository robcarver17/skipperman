from typing import Union

from app.backend.events.event_warnings import add_list_of_event_warnings
from app.objects.volunteers import Volunteer

from app.objects.relevant_information_for_volunteers import (
    ListOfRelevantInformationForVolunteer,
)
from app.backend.volunteers.relevant_information_for_volunteer import (
    relevant_information_requires_clarification,
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
    get_volunteer_registration_data_from_list_of_relevant_information,
    add_volunteer_at_event,
)
from app.backend.registration_data.volunteer_registration_data import (
    is_volunteer_already_at_event,
)
from app.frontend.shared.events_state import get_event_from_state
from app.frontend.events.volunteer_identification.track_state_in_volunteer_allocation import (
    clear_volunteer_id_at_event_in_state,
    get_and_save_next_volunteer_id_in_mapped_event_data,
    get_current_volunteer_at_event,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import NoMoreData
from app.objects.events import Event


def display_add_volunteers_to_event(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    clear_volunteer_id_at_event_in_state(interface)

    return next_volunteer_in_event(interface)


def post_add_volunteers_to_event(interface: abstractInterface):
    raise Exception("Should never be reached post_add_volunteers_to_event")


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
        print("All cadets cancelled for %s, not adding" % volunteer)
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
        print("Already added %s to event, updating connections" % volunteer)
        
        update_cadet_connections_when_volunteer_already_at_event(
            object_store=interface.object_store, event=event, volunteer=volunteer
        )
        interface.flush_and_clear()
        return next_volunteer_in_event(interface)

    else:
        return process_new_volunteer_at_event_with_active_cadets(
            interface=interface, event=event, volunteer=volunteer
        )


def process_new_volunteer_at_event_with_active_cadets(
    interface: abstractInterface, event: Event, volunteer: Volunteer
) -> Union[Form, NewForm]:
    ## New volunteer with cadets
    print("New volunteer %s to event with active cadets" % volunteer)

    list_of_relevant_information = (
        get_list_of_relevant_information_for_volunteer_in_registration_data(
            object_store=interface.object_store, event=event, volunteer=volunteer
        )
    )
    print(
        "Relevant information for %s, %s"
        % (volunteer.name, str(list_of_relevant_information))
    )
    issues_with_volunteer = relevant_information_requires_clarification(
        list_of_relevant_information=list_of_relevant_information,
        volunteer=volunteer,
    )
    any_issues = len(issues_with_volunteer) > 0
    if any_issues:
        add_list_of_event_warnings(
            object_store=interface.object_store,
            event=event,
            new_list_of_warnings=issues_with_volunteer,
        )

    return process_new_volunteer_at_event_with_active_cadets_with_issues_logged(
        interface=interface,
        event=event,
        list_of_relevant_information=list_of_relevant_information,
        volunteer=volunteer,
        any_issues=any_issues,
    )


def process_new_volunteer_at_event_with_active_cadets_with_issues_logged(
    interface: abstractInterface,
    list_of_relevant_information: ListOfRelevantInformationForVolunteer,
    volunteer: Volunteer,
    event: Event,
    any_issues: bool,
) -> Union[Form, NewForm]:

    
    list_of_associated_cadets = get_list_of_active_associated_cadets_in_mapped_event_data_given_identified_volunteer(
        object_store=interface.object_store, volunteer=volunteer, event=event
    )
    registration_data = (
        get_volunteer_registration_data_from_list_of_relevant_information(
            list_of_relevant_information=list_of_relevant_information,
            list_of_associated_cadets=list_of_associated_cadets,
            any_issues=any_issues,
        )
    )

    print("Adding %s with data %s to event" % (volunteer, str(registration_data)))
    add_volunteer_at_event(
        object_store=interface.object_store,
        event=event,
        volunteer=volunteer,
        registration_data=registration_data,
    )
    update_cadet_connections_when_volunteer_already_at_event(
        object_store=interface.object_store, event=event, volunteer=volunteer
    )

    interface.flush_and_clear()
    return next_volunteer_in_event(interface)
