from app.backend.registration_data.raw_mapped_registration_data import (
    get_raw_mapped_registration_data,
    update_raw_mapped_registration_data,
)
from app.backend.registration_data.volunteer_registration_data import (
    get_list_of_registration_data_for_volunteers_at_event,
    update_list_of_registration_data_for_volunteers_at_event,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event
from app.backend.registration_data.cadet_registration_data import (
    get_list_of_cadets_with_id_and_registration_data_at_event,
    update_list_of_cadets_with_registration_data,
)


def clean_sensitive_data_for_event(interface: abstractInterface, event: Event):
    ## We clean:
    clean_sensitive_data_for_event_from_mapped_data(interface=interface, event=event)
    clean_sensitive_data_for_event_from_cadets_at_event_data(
        interface=interface, event=event
    )
    clean_sensitive_data_for_event_from_volunteers_at_event_data(
        interface=interface, event=event
    )


def clean_sensitive_data_for_event_from_mapped_data(
    interface: abstractInterface, event: Event
):
    raw_data = get_raw_mapped_registration_data(
        object_store=interface.object_store, event=event
    )
    raw_data.clear_user_data()
    update_raw_mapped_registration_data(
        interface=interface, event=event, registration_data=raw_data
    )


def clean_sensitive_data_for_event_from_cadets_at_event_data(
    interface: abstractInterface, event: Event
):
    list_of_cadets_at_event = get_list_of_cadets_with_id_and_registration_data_at_event(
        object_store=interface.object_store, event=event
    )
    list_of_cadets_at_event.clear_private_data()
    update_list_of_cadets_with_registration_data(
        interface=interface,
        event=event,
        list_of_cadets_at_event=list_of_cadets_at_event,
    )


def clean_sensitive_data_for_event_from_volunteers_at_event_data(
    interface: abstractInterface, event: Event
):
    list_of_volunteers_at_event = get_list_of_registration_data_for_volunteers_at_event(
        object_store=interface.object_store, event=event
    )
    list_of_volunteers_at_event.clear_user_data()
    update_list_of_registration_data_for_volunteers_at_event(
        interface=interface,
        event=event,
        list_of_volunteers_at_event=list_of_volunteers_at_event,
    )
