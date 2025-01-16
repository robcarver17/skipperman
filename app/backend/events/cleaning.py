from app.data_access.store.object_store import ObjectStore
from app.objects.events import Event


def clean_sensitive_data_for_event(object_store: ObjectStore, event: Event):
    ## We clean:
    clean_sensitive_data_for_event_from_mapped_data(interface=interface, event=event)
    clean_sensitive_data_for_event_from_cadets_at_event_data(
        interface=interface, event=event
    )


def clean_sensitive_data_for_event_from_mapped_data(
    interface: abstractInterface, event: Event
):
    mapped_wa_data = MappedEventsData(interface.data)
    mapped_wa_data.clear_mapped_event_data(event)


def clean_sensitive_data_for_event_from_cadets_at_event_data(
    interface: abstractInterface, event: Event
):
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    cadets_at_event_data.clear_row_data(event)
    cadets_at_event_data.clear_health_information(event)
