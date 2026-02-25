from typing import List

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
                            event_id=event.id)

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


def remove_cadet_from_boats_data_across_days_and_return_messages(
interface: abstractInterface, event: Event, cadet: Cadet
) -> List[str]:
    msgs = []
    for day in event.days_in_event():
        msgs+=remove_cadet_from_boats_data_on_day_and_return_messages(
            interface=interface, event=event, cadet=cadet, day=day
        )

    return msgs


def remove_cadet_from_boats_data_on_day_and_return_messages(
interface: abstractInterface, event: Event, cadet: Cadet, day: Day
) -> str:
    dict_of_cadets_and_boat_classes_and_partners_at_event=get_dict_of_cadets_and_boat_classes_and_partners_at_events(object_store=interface.object_store, event=event)
    boat_classes_and_partner_on_day  = dict_of_cadets_and_boat_classes_and_partners_at_event.boat_classes_and_partner_for_cadet(cadet).boat_class_and_partner_on_day(day)
    has_partner= boat_classes_and_partner_on_day.has_partner
    if has_partner:
        partner_cadet = boat_classes_and_partner_on_day.partner_cadet
        message = (
                "%s was sailing with partner %s, now they aren't sailing: %s has no partner on %s"
                % (cadet.name, partner_cadet.name, partner_cadet.name, day.name)
        )

    else:
        message = ""

    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_dinghies_at_event.remove_cadet_from_boats_data_on_day_and_breakup_any_partnerships,
        event_id = event.id,
        cadet_id=cadet.id,
        day=day
    )

    return message
