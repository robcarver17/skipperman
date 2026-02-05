from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet
from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import (
 DictOfCadetsAndBoatClassAndPartners,
)
from app.objects.day_selectors import Day
from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore



def get_dict_of_cadets_and_boat_classes_and_partners_at_events(
    object_store: ObjectStore, event: Event
) -> DictOfCadetsAndBoatClassAndPartners:
    return object_store.get(object_store.data_api.data_list_of_cadets_with_dinghies_at_event.get_dict_of_cadets_and_boat_classes_and_partners_at_events,
                            event=event)

def add_two_handed_partnership_on_day_for_new_cadet_when_have_dinghy_for_existing_cadet(
    interface: abstractInterface,
    day: Day,
    event: Event,
    original_cadet: Cadet,
    new_cadet: Cadet,
):
    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_dinghies_at_event.add_two_handed_partnership_on_day_for_new_cadet_when_have_dinghy_for_existing_cadet,
        event_id=event.id,
        day=day,
        original_cadet_id=original_cadet.id,
        new_cadet_id=new_cadet.id
    )


