from app.data_access.store.object_store import ObjectStore
from app.objects.events import Event


def clean_sensitive_data_for_event(object_store: ObjectStore, event: Event):
    ## We clean:
    clean_sensitive_data_for_event_from_mapped_data(object_store=object_store, event=event)
    clean_sensitive_data_for_event_from_cadets_at_event_data(
        object_store=object_store, event=event
    )


def clean_sensitive_data_for_event_from_mapped_data(
    object_store: ObjectStore, event: Event
):
    pass


def clean_sensitive_data_for_event_from_cadets_at_event_data(
    object_store: ObjectStore, event: Event
):
    pass