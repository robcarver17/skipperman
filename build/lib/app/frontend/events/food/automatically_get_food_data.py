from app.OLD_backend.volunteers.volunteers import EPRECATE_get_volunteer_name_from_id

from app.objects.relevant_information_for_volunteers import (
    missing_relevant_information,
)

from app.backend.registration_data.identified_volunteers_at_event import \
    get_list_of_relevant_information_for_volunteer_in_registration_data

from app.frontend.events.volunteer_allocation.track_state_in_volunteer_allocation import (
    list_of_unique_volunteer_ids_in_identified_event_data,
)

from app.objects.registration_data import RowInRegistrationData

from app.objects_OLD.food import guess_food_requirements_from_food_field

from app.OLD_backend.cadets import cadet_name_from_id
from app.data_access.configuration.field_list import CADET_FOOD_PREFERENCE

from app.objects.exceptions import DuplicateCadets, NoMoreData

from app.OLD_backend.food import (
    is_cadet_with_id_already_at_event_with_food,
    add_new_cadet_with_food_to_event,
    is_volunteer_with_id_already_at_event_with_food,
    add_new_volunteer_with_food_to_event,
)

from app.objects.events import Event

from app.backend.registration_data.identified_cadets_at_event import \
    list_of_cadet_ids_in_event_data_and_identified_in_raw_registration_data_for_event, \
    get_row_in_registration_data_for_cadet_both_cancelled_and_active
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface


def get_and_save_food_for_cadets_from_registration_data(interface: abstractInterface):
    event = get_event_from_state(interface)
    list_of_ids = list_of_cadet_ids_in_event_data_and_identified_in_raw_registration_data_for_event(
        event=event, interface=interface, include_identified_in_raw_registration_data=False
    )

    for cadet_id in list_of_ids:
        process_update_to_cadet_food_data(
            interface=interface, event=event, cadet_id=cadet_id
        )


def process_update_to_cadet_food_data(
    interface: abstractInterface, event: Event, cadet_id: str
):
    cadet_already_at_event = is_cadet_with_id_already_at_event_with_food(
        interface=interface, event=event, cadet_id=cadet_id
    )
    if cadet_already_at_event:
        return

    process_update_to_cadet_food_data_if_new_to_event(
        interface=interface, event=event, cadet_id=cadet_id
    )


def process_update_to_cadet_food_data_if_new_to_event(
    interface: abstractInterface, event: Event, cadet_id: str
):
    try:
        relevant_row = get_row_in_registration_data_for_cadet_both_cancelled_and_active(
            interface=interface,
            cadet_id=cadet_id,
            event=event,
            raise_error_on_duplicate=True,
        )
    except DuplicateCadets:
        interface.log_error(
            "ACTION REQUIRED: Cadet %s appears more than once in WA file with an active registration - using the first registration found - go to WA and cancel all but one of the registrations please, and then check details here are correct!"
            % cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id)
        )
        relevant_row = get_row_in_registration_data_for_cadet_both_cancelled_and_active(
            interface=interface,
            cadet_id=cadet_id,
            event=event,
            raise_error_on_duplicate=False,  ## try again this time allowing duplicates
        )
    except NoMoreData:
        interface.log_error(
            "ACTION REQUIRED: Cadet %s vanished from WA mapping file - contact support"
            % cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id)
        )
        return

    process_update_to_cadet_food_data_given_registration_data(
        interface=interface, event=event, cadet_id=cadet_id, relevant_row=relevant_row
    )


def process_update_to_cadet_food_data_given_registration_data(
    interface: abstractInterface,
    event: Event,
    cadet_id: str,
    relevant_row: RowInRegistrationData,
):
    food_from_registration = relevant_row.get_item(CADET_FOOD_PREFERENCE, "")
    food_requirements = guess_food_requirements_from_food_field(food_from_registration)
    add_new_cadet_with_food_to_event(
        interface=interface,
        event=event,
        food_requirements=food_requirements,
        cadet_id=cadet_id,
    )
    interface.log_error(
        "Added food for cadet %s to event"
        % cadet_name_from_id(data_layer=interface.data, cadet_id=cadet_id)
    )


def get_and_save_food_for_volunteers_from_registration_data(
    interface: abstractInterface,
):
    event = get_event_from_state(interface)
    list_of_ids = list_of_unique_volunteer_ids_in_identified_event_data(interface)

    for volunteer_id in list_of_ids:
        process_update_to_volunteer_food_data(
            interface=interface, event=event, volunteer_id=volunteer_id
        )


def process_update_to_volunteer_food_data(
    interface: abstractInterface, event: Event, volunteer_id: str
):
    volunteer_already_at_event = is_volunteer_with_id_already_at_event_with_food(
        interface=interface, event=event, volunteer_id=volunteer_id
    )
    if volunteer_already_at_event:
        return

    process_update_to_volunteer_food_data_if_new_to_event(
        interface=interface, event=event, volunteer_id=volunteer_id
    )


def process_update_to_volunteer_food_data_if_new_to_event(
    interface: abstractInterface, event: Event, volunteer_id: str
):
    list_of_food_preferences_as_single_str = (
        get_volunteer_food_preferences_as_single_str(
            interface=interface, event=event, volunteer_id=volunteer_id
        )
    )

    food_requirements = guess_food_requirements_from_food_field(
        list_of_food_preferences_as_single_str
    )
    add_new_volunteer_with_food_to_event(
        interface=interface,
        event=event,
        food_requirements=food_requirements,
        volunteer_id=volunteer_id,
    )
    interface.log_error(
        "Added food for volunteer %s to event"
        % EPRECATE_get_volunteer_name_from_id(
            volunteer_id=volunteer_id, interface=interface
        )
    )


def get_volunteer_food_preferences_as_single_str(
    interface: abstractInterface, event: Event, volunteer_id: str
) -> str:
    list_of_relevant_information = get_list_of_relevant_information_for_volunteer_in_registration_data(
        volunteer_id=volunteer_id, event=event, interface=interface
    )
    list_of_relevant_information = [
        relevant_information
        for relevant_information in list_of_relevant_information
        if relevant_information is not missing_relevant_information
    ]
    list_of_food_preferences = [
        relevant_information.details.food_preference
        for relevant_information in list_of_relevant_information
    ]
    list_of_food_preferences = [
        food for food in list_of_food_preferences if len(food) > 0
    ]
    list_of_food_preferences_as_single_str = ", ".join(list_of_food_preferences)

    return list_of_food_preferences_as_single_str
