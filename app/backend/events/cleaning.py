from app.backend.registration_data.raw_mapped_registration_data import (
    get_raw_mapped_registration_data,
    update_raw_mapped_registration_data,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.events import Event
from app.backend.registration_data.cadet_registration_data import (
    DEPRECATE_get_dict_of_cadets_with_registration_data,
    update_dict_of_cadets_with_registration_data,
)
from app.backend.registration_data.volunteer_registration_data import (
    get_dict_of_registration_data_for_volunteers_at_event,
    update_dict_of_registration_data_for_volunteers_at_event,
)


def clean_sensitive_data_for_event(object_store: ObjectStore, event: Event):
    ## We clean:
    clean_sensitive_data_for_event_from_mapped_data(
        object_store=object_store, event=event
    )
    clean_sensitive_data_for_event_from_cadets_at_event_data(
        object_store=object_store, event=event
    )
    clean_sensitive_data_for_event_from_volunteers_at_event_data(
        object_store=object_store, event=event
    )


def clean_sensitive_data_for_event_from_mapped_data(
    object_store: ObjectStore, event: Event
):
    raw_data = get_raw_mapped_registration_data(object_store=object_store, event=event)
    raw_data.clear_user_data()
    update_raw_mapped_registration_data(
        object_store=object_store, event=event, registration_data=raw_data
    )


def clean_sensitive_data_for_event_from_cadets_at_event_data(
    object_store: ObjectStore, event: Event
):
    reg_data = DEPRECATE_get_dict_of_cadets_with_registration_data(
        object_store=object_store, event=event
    )
    reg_data.clear_user_data()
    update_dict_of_cadets_with_registration_data(
        object_store=object_store,
        event=event,
        dict_of_cadets_with_registration_data=reg_data,
    )


def clean_sensitive_data_for_event_from_volunteers_at_event_data(
    object_store: ObjectStore, event: Event
):
    reg_data = get_dict_of_registration_data_for_volunteers_at_event(
        object_store=object_store, event=event
    )
    reg_data.clear_user_data()
    update_dict_of_registration_data_for_volunteers_at_event(
        object_store=object_store, dict_of_registration_data=reg_data, event=event
    )
