from app.objects.volunteers import Volunteer


from app.objects.composed.cadets_at_event_with_registration_data import (
    CadetRegistrationData,
)

from app.objects.cadets import Cadet

from app.backend.registration_data.cadet_registration_data import (
    get_dict_of_cadets_with_registration_data,
)


from app.objects.relevant_information_for_volunteers import (
    missing_relevant_information,
)

from app.backend.registration_data.identified_volunteers_at_event import (
    get_list_of_relevant_information_for_volunteer_in_registration_data,
)

from app.objects.food import guess_food_requirements_from_food_field

from app.data_access.configuration.field_list import CADET_FOOD_PREFERENCE

from app.backend.food.modify_food_data import (
    is_cadet_with_already_at_event_with_food,
    add_new_cadet_with_food_to_event,
    is_volunteer_with_already_at_event_with_food,
    add_new_volunteer_with_food_to_event,
    remove_food_requirements_for_cadet_at_event,
)

from app.objects.events import Event

from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface


def update_food_for_cadets_from_registration_data(interface: abstractInterface):
    event = get_event_from_state(interface)
    dict_of_cadets_at_event_with_registration_data = (
        get_dict_of_cadets_with_registration_data(
            object_store=interface.object_store, event=event
        )
    )

    for (
        cadet,
        registration_data,
    ) in dict_of_cadets_at_event_with_registration_data.items():
        process_update_to_cadet_food_data(
            interface=interface,
            event=event,
            cadet=cadet,
            registration_data=registration_data,
        )


def process_update_to_cadet_food_data(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    registration_data: CadetRegistrationData,
):
    cadet_already_at_event = is_cadet_with_already_at_event_with_food(
        object_store=interface.object_store, event=event, cadet=cadet
    )
    if cadet_already_at_event:
        return

    process_update_to_cadet_food_data_if_new_to_event(
        interface=interface,
        event=event,
        cadet=cadet,
        registration_data=registration_data,
    )


def process_update_to_cadet_food_data_if_already_at_event(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    registration_data: CadetRegistrationData,
):

    cadet_active_at_event = registration_data.active
    if cadet_active_at_event:
        return

    remove_food_requirements_for_cadet_at_event(
        object_store=interface.object_store, event=event, cadet=cadet
    )


def process_update_to_cadet_food_data_if_new_to_event(
    interface: abstractInterface,
    event: Event,
    cadet: Cadet,
    registration_data: CadetRegistrationData,
):

    food_from_registration = registration_data.data_in_row.get_item(
        CADET_FOOD_PREFERENCE, ""
    )
    food_requirements = guess_food_requirements_from_food_field(food_from_registration)
    add_new_cadet_with_food_to_event(
        object_store=interface.object_store,
        event=event,
        cadet=cadet,
        food_requirements=food_requirements,
    )


from app.backend.volunteers.volunteers_at_event import (
    get_dict_of_registration_data_for_volunteers_at_event,
)


def update_food_for_volunteers_from_registration_data(
    interface: abstractInterface,
):
    event = get_event_from_state(interface)
    dict_volunteers_registered_to_event = (
        get_dict_of_registration_data_for_volunteers_at_event(
            object_store=interface.object_store, event=event
        )
    )

    for volunteer in dict_volunteers_registered_to_event.list_of_volunteers_at_event():
        process_update_to_volunteer_food_data(
            interface=interface, event=event, volunteer=volunteer
        )


def process_update_to_volunteer_food_data(
    interface: abstractInterface, event: Event, volunteer: Volunteer
):
    volunteer_already_at_event = is_volunteer_with_already_at_event_with_food(
        object_store=interface.object_store, event=event, volunteer=volunteer
    )
    if volunteer_already_at_event:
        ## it isnt possible to have 'inactive' volunteers, so no need to remove
        pass
    else:
        process_update_to_volunteer_food_data_if_new_to_event(
            interface=interface, event=event, volunteer=volunteer
        )


def process_update_to_volunteer_food_data_if_new_to_event(
    interface: abstractInterface, event: Event, volunteer: Volunteer
):
    list_of_food_preferences_as_single_str = (
        get_volunteer_food_preferences_as_single_str(
            interface=interface, event=event, volunteer=volunteer
        )
    )

    food_requirements = guess_food_requirements_from_food_field(
        list_of_food_preferences_as_single_str
    )
    add_new_volunteer_with_food_to_event(
        object_store=interface.object_store,
        event=event,
        food_requirements=food_requirements,
        volunteer=volunteer,
    )
    interface.log_error("Added food for volunteer %s to event" % volunteer.name)


def get_volunteer_food_preferences_as_single_str(
    interface: abstractInterface, event: Event, volunteer: Volunteer
) -> str:
    list_of_relevant_information = (
        get_list_of_relevant_information_for_volunteer_in_registration_data(
            object_store=interface.object_store, event=event, volunteer=volunteer
        )
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
