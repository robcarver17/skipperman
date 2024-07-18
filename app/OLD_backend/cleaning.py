from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.events import Event
from app.OLD_backend.data.mapped_events import MappedEventsData
from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData


def clean_sensitive_data_for_event(interface: abstractInterface, event: Event):
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
