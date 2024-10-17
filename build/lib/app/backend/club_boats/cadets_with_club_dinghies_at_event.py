from app.data_access.store.object_definitions import object_definition_for_cadets_with_ids_and_club_dinghies_at_event, \
    object_definition_for_dict_of_cadets_and_club_dinghies_at_event
from app.objects.composed.cadets_at_event_with_club_dinghies import DictOfCadetsAndClubDinghiesAtEvent

from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore

from app.objects.cadet_at_event_with_club_boat_with_ids import ListOfCadetAtEventWithIdAndClubDinghies

#




def get_dict_of_cadets_and_club_dinghies_at_event(object_store: ObjectStore, event: Event) ->  DictOfCadetsAndClubDinghiesAtEvent:
    return object_store.get(object_definition=object_definition_for_dict_of_cadets_and_club_dinghies_at_event,
                            event_id=event.id)


def update_dict_of_cadets_and_club_dinghies_at_event(object_store: ObjectStore, event: Event, dict_of_cadets_and_club_dinghies_at_event:  DictOfCadetsAndClubDinghiesAtEvent):
    object_store.update(object_definition=object_definition_for_dict_of_cadets_and_club_dinghies_at_event,
                            event_id=event.id,
                        new_object=dict_of_cadets_and_club_dinghies_at_event)



def get_list_of_cadets_with_ids_with_club_dinghies_at_event(object_store: ObjectStore, event: Event) -> ListOfCadetAtEventWithIdAndClubDinghies:
    return object_store.get(object_definition=object_definition_for_cadets_with_ids_and_club_dinghies_at_event,
                            event_id=event.id)

def update_list_of_cadets_with_ids_with_club_dinghies_at_event(object_store: ObjectStore, event: Event,
                                                               list_of_cadets_with_ids_with_club_dinghies_at_event: ListOfCadetAtEventWithIdAndClubDinghies):
    object_store.update(
        new_object=list_of_cadets_with_ids_with_club_dinghies_at_event,
        object_definition=object_definition_for_cadets_with_ids_and_club_dinghies_at_event,
        event_id=event.id,
    )
