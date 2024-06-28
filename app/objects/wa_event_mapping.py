from dataclasses import dataclass
from app.objects.generic import GenericSkipperManObject, GenericListOfObjects
import pandas as pd

NO_WA_ID = Exception()
NO_EVENT_ID = Exception
WA_ID_LABEL = "WA_id"
EVENT_ID_LABEL = "Event_id"


@dataclass
class WAEventMap(GenericSkipperManObject):
    event_id: str
    wa_id: str


class ListOfWAEventMaps(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return WAEventMap

    def add_event(self, event_id: str, wa_id: str):
        self.append(WAEventMap(event_id=event_id, wa_id=wa_id))

    def is_event_in_mapping_list(self, event_id: str) -> bool:
        return any([event_id == event_map.event_id for event_map in self])

    def is_wa_id_in_mapping_list(self, wa_id: str) -> bool:
        return any([wa_id == event_map.wa_id for event_map in self])

    def get_wa_id_for_event(self, event_id: str) -> str:
        try:
            assert self.is_event_in_mapping_list(event_id)
        except:
            raise NO_EVENT_ID

        idx = self.list_of_event_ids.index(event_id)
        return str(self.list_of_wa_ids[idx])

    def get_event_id_for_wa(self, wa_id: str) -> str:
        try:
            assert self.is_wa_id_in_mapping_list(wa_id)
        except:
            raise NO_WA_ID

        idx = self.list_of_wa_ids.index(wa_id)
        return self.list_of_event_ids[idx]

    @property
    def list_of_event_ids(self) -> list:
        return [event_map.event_id for event_map in self]

    @property
    def list_of_wa_ids(self) -> list:
        return [event_map.wa_id for event_map in self]
