from typing import Dict

from app.objects.cadets import ListOfCadets, Cadet
from app.objects.events import ListOfEvents, Event

from app.objects.previous_cadet_groups import ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds




class DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds(
    Dict[Cadet, Dict[Event, str]]
):
    def __init__(
        self,
        raw_dict: Dict[Cadet, Dict[Event, str]],
            list_of_group_names_for_events_and_cadet_persistent_version_with_ids: ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds

    ):
        super().__init__(raw_dict)
        self._list_of_group_names_for_events_and_cadet_persistent_version_with_ids = list_of_group_names_for_events_and_cadet_persistent_version_with_ids

    def get_dict_of_group_names_for_cadet(self, cadet: Cadet) -> Dict[Event, str]:
        return self.get(cadet, {})

    def update_most_group_names_across_events_for_cadet(self, cadet: Cadet,
                                                 dict_of_group_names_by_event: Dict[Event, str]):
        self[cadet] = dict_of_group_names_by_event
        dict_with_ids = dict([(event.id, group_name) for event, group_name in dict_of_group_names_by_event.items()])
        self.list_of_group_names_for_events_and_cadet_persistent_version_with_ids.update_does_not_update_core_data(
            cadet_id=str(cadet.id),
            dict_of_event_ids_and_group_names=dict_with_ids
        )

    @property
    def list_of_group_names_for_events_and_cadet_persistent_version_with_ids(self):
        return self._list_of_group_names_for_events_and_cadet_persistent_version_with_ids

def compose_dict_of_group_names_for_events_and_cadets_persistent_version(
    list_of_cadets: ListOfCadets,
list_of_group_names_for_events_and_cadet_persistent_version_with_ids: ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds,
        list_of_events: ListOfEvents) -> DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds:


    raw_dict = compose_raw_dict_of_group_names_for_events_and_cadets_persistent_version(
        list_of_events=list_of_events,
        list_of_cadets=list_of_cadets,
        list_of_group_names_for_events_and_cadet_persistent_version_with_ids=list_of_group_names_for_events_and_cadet_persistent_version_with_ids
    )

    return DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds(
        raw_dict=raw_dict,
        list_of_group_names_for_events_and_cadet_persistent_version_with_ids=list_of_group_names_for_events_and_cadet_persistent_version_with_ids
    )

def compose_raw_dict_of_group_names_for_events_and_cadets_persistent_version(
        list_of_cadets: ListOfCadets,
        list_of_group_names_for_events_and_cadet_persistent_version_with_ids: ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds,
        list_of_events: ListOfEvents

    ) -> Dict[Cadet, Dict[Event, str]]:

    raw_dict = {}

    for cadet_with_group_names_and_ids in list_of_group_names_for_events_and_cadet_persistent_version_with_ids:
        cadet = list_of_cadets.cadet_with_id(cadet_id=str(cadet_with_group_names_and_ids.cadet_id))
        dict_of_event_ids_and_group_names = cadet_with_group_names_and_ids.dict_of_event_ids_and_group_names
        dict_of_group_names_by_event = dict([
            (list_of_events.event_with_id(event_id),
             group_name)
            for event_id, group_name in dict_of_event_ids_and_group_names.items()
        ])

        raw_dict[cadet] = dict_of_group_names_by_event

    return raw_dict

