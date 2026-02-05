from typing import List, Dict

from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.club_dinghies import ClubDinghy, ClubDinghyAndGenericLimit
from app.objects.events import Event


def update_limit_for_club_dinghy_at_event(
    interface: abstractInterface, club_dinghy: ClubDinghy, event: Event, new_limit: int
):
    interface.update(
        interface.object_store.data_api.data_List_of_club_dinghy_limits.update_limit_for_club_dinghy_at_event,
        event_id=event.id,
        club_dinghy_id=club_dinghy.id,
        new_limit=new_limit
    )


def clear_and_set_generic_limit(
    interface: abstractInterface,
    original_boat: ClubDinghy,
    new_limit: int,
):
    interface.update(
        interface.object_store.data_api.data_List_of_club_dinghy_limits.clear_and_set_generic_limit,
        club_dinghy_id=original_boat.id,
        new_limit=new_limit
    )



def get_list_of_boats_and_generic_limits(
    object_store: ObjectStore,
) -> List[ClubDinghyAndGenericLimit]:
   return object_store.get(
       object_store.data_api.data_List_of_club_dinghy_limits.get_list_of_boats_and_generic_limits
   )

def get_dict_of_names_and_limits_for_all_visible_club_boats_at_event(object_store: ObjectStore, event: Event) -> Dict[str, int]:
    return object_store.get(
        object_store.data_api.data_List_of_club_dinghy_limits.get_dict_of_names_and_limits_for_all_visible_club_boats_at_event,
        event_id=event.id
    )
