from typing import List

from app.backend.boat_classes.cadets_with_boat_classes_at_event import \
    remove_cadet_from_boats_data_across_days_and_return_messages
from app.backend.registration_data.cadet_registration_data import (
    add_new_cadet_to_event_from_row_in_registration_data, add_empty_row_to_raw_registration_data_and_return_row,
    get_registration_data_for_single_cadet_at_event,
)
from app.backend.registration_data.identified_cadets_at_event import (
    add_identified_cadet_and_row,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.cadets import ListOfCadets, Cadet

from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore

from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadets



def get_health_notes_for_list_of_cadets_at_event(
    object_store: ObjectStore, list_of_cadets: ListOfCadets, event: Event
) -> List[str]:

    health_notes = []
    for cadet_at_event in list_of_cadets:
        registration_data = get_registration_data_for_single_cadet_at_event(object_store=object_store, event=event,
                                                                            cadet=cadet_at_event)
        health_for_cadet = registration_data.health
        if len(health_for_cadet) == 0:
            health_for_cadet = "none"
        health_notes.append(health_for_cadet)

    return health_notes

def get_health_notes_for_cadet_at_event(
    object_store: ObjectStore, cadet: Cadet, event: Event
) -> str:

    registration_data = get_registration_data_for_single_cadet_at_event(object_store=object_store, event=event, cadet=cadet)
    health_for_cadet = registration_data.health
    if len(health_for_cadet) == 0:
        health_for_cadet = "none"

    return health_for_cadet


def get_dict_of_all_event_info_for_cadets(object_store: ObjectStore, event: Event) -> DictOfAllEventInfoForCadets:

    return object_store.get(object_store.data_api.dict_of_all_event_data_for_cadets.get_dict_of_all_event_info_for_cadets,
                     event=event)



def add_new_cadet_manually_to_event(
    interface: abstractInterface,
    new_cadet: Cadet,
    event: Event,
):
    new_row = add_empty_row_to_raw_registration_data_and_return_row(
        interface=interface, event=event, cadet=new_cadet
    )

    add_identified_cadet_and_row(
        interface=interface, event=event, row_id=new_row.row_id, cadet=new_cadet
    )

    add_new_cadet_to_event_from_row_in_registration_data(
        interface=interface,
        event=event,
        row_in_registration_data=new_row,
        cadet=new_cadet,
    )


def delete_cadet_from_event_and_return_messages(
    interface: abstractInterface, event: Event, cadet: Cadet, areyousure: bool = False
) -> List[str]:
    if not areyousure:
        return []

    messages = []
    messages += interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_groups.delete_cadet_from_event_and_return_messages,
        event_id=event.id,
        cadet_id=cadet.id
    )

    messages += remove_cadet_from_boats_data_across_days_and_return_messages(
        interface=interface,
        event=event,
        cadet=cadet,
    )

    messages+= interface.update(interface.object_store.data_api.data_list_of_cadets_with_food_requirement_at_event.delete_cadet_from_event_and_return_messages,
                                event_id=event.id,
                                cadet_id=cadet.id
                                )

    messages+= interface.update(interface.object_store.data_api.data_list_of_cadets_at_event_with_club_dinghies.delete_cadet_from_event_and_return_messages,
                                event_id=event.id,
                                cadet_id=cadet.id
                                )

    messages+= interface.update(interface.object_store.data_api.data_list_of_cadets_with_clothing_at_event.delete_cadet_from_event_and_return_messages,
                                event_id=event.id,
                                cadet_id=cadet.id
                                )

    messages += interface.update(interface.object_store.data_api.data_cadets_at_event.delete_cadet_from_event_and_return_messages,
                                 event_id=event.id,
                                 cadet_id=cadet.id
                                 )

    messages+= interface.update(interface.object_store.data_api.data_identified_cadets_at_event.delete_cadet_from_identified_data_and_return_messages,
                                event_id=event.id,
                                cadet_id=cadet.id
                                )

    if len(messages) > 0:
        messages.insert(0, "Will remove cadet from event %s" % str(event))


