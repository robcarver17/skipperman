from typing import Dict

from app.objects.cadets import ListOfCadets, Cadet
from app.objects.events import ListOfEvents, Event

from app.objects.previous_cadet_groups import (
    ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds,
    GroupNamesForEventsAndCadetPersistentVersionWithIds,
)


class DictOfOfGroupNamesForEventsAndCadetPersistentVersionWithIds(
    Dict[Cadet, Dict[Event, str]]
):
    def get_dict_of_group_names_for_cadet(self, cadet: Cadet) -> Dict[Event, str]:
        return self.get(cadet, {})

    def update_most_group_names_across_events_for_cadet(
        self, cadet: Cadet, dict_of_group_names_by_event: Dict[Event, str]
    ):
        self[cadet] = dict_of_group_names_by_event

    def as_list_with_ids(
        self,
    ) -> ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds:
        return ListOfGroupNamesForEventsAndCadetPersistentVersionWithIds(
            [
                GroupNamesForEventsAndCadetPersistentVersionWithIds(
                    cadet_id=cadet.id,
                    dict_of_event_ids_and_group_names=dict(
                        [
                            (event.id, group_name)
                            for event, group_name in dict_of_events_and_group_names.items()
                        ]
                    ),
                )
                for cadet, dict_of_events_and_group_names in self.items()
            ]
        )
