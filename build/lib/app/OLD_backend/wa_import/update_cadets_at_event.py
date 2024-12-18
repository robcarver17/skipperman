from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.objects.events import Event


def has_cadet_at_event_changed(
    interface: abstractInterface, cadet_id: str, event: Event
) -> bool:
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    list_of_cadets_at_event = cadets_at_event_data.get_list_of_cadets_with_id_at_event(
        event
    )
    cadet = list_of_cadets_at_event.cadet_at_event(cadet_id)

    return cadet.changed


def mark_cadet_at_event_as_unchanged(
    interface: abstractInterface, cadet_id: str, event: Event
):
    cadet_data = CadetsAtEventIdLevelData(interface.data)
    cadet_data.mark_cadet_at_event_as_unchanged(cadet_id=cadet_id, event=event)


