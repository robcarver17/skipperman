from app.objects.events import Event

from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import object_definition_for_dict_of_all_event_info_for_cadet
from app.objects.composed.cadets_with_all_event_info import DictOfAllEventInfoForCadet
from app.objects.groups import ListOfGroups


def get_dict_of_all_event_info_for_cadets(object_store: ObjectStore, event: Event, active_only: bool = True) -> DictOfAllEventInfoForCadet:
    return object_store.get(object_definition=object_definition_for_dict_of_all_event_info_for_cadet,
                            event_id=event.id, active_only=active_only)

def update_dict_of_all_event_info_for_cadets(object_store: ObjectStore,
                                                               dict_of_all_event_info_for_cadets: DictOfAllEventInfoForCadet):
    object_store.update(
        new_object=dict_of_all_event_info_for_cadets,
        object_definition=object_definition_for_dict_of_all_event_info_for_cadet,
        event_id=dict_of_all_event_info_for_cadets.event.id,
    )


def get_list_of_all_groups_at_event(object_store: ObjectStore, event: Event) -> ListOfGroups:
    event_info = get_dict_of_all_event_info_for_cadets(object_store=object_store, event=event, active_only=True)
    return event_info.dict_of_cadets_with_days_and_groups.all_groups_at_event()
