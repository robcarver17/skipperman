import pandas as pd

NO_WA_ID = Exception()
NO_EVENT_ID = Exception
WA_ID_LABEL = "WA_id"
EVENT_ID_LABEL = "Event_id"


class WAEventMapping(object):
    def __init__(self, list_of_event_ids: list, list_of_wa_ids: list):
        self._list_of_event_ids = list_of_event_ids
        self._list_of_wa_ids = list_of_wa_ids

    @classmethod
    def create_empty(cls):
        return cls([], [])

    @classmethod
    def from_df(cls, some_df: pd.DataFrame):
        try:
            events_list = list(some_df[EVENT_ID_LABEL].values)
            wa_list = list(some_df[WA_ID_LABEL].values)
        except KeyError:
            raise Exception(
                "WA/Event mapping needs to have columns %s and %s"
                % (EVENT_ID_LABEL, WA_ID_LABEL)
            )

        return cls(list_of_event_ids=events_list, list_of_wa_ids=wa_list)

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            {EVENT_ID_LABEL: self.list_of_event_ids, WA_ID_LABEL: self.list_of_wa_ids}
        )

    def add_event(self, event_id: str, wa_id: str):
        self._list_of_event_ids.append(event_id)
        self._list_of_wa_ids.append(wa_id)

    def is_event_in_mapping_list(self, event_id: str) -> bool:
        return any([event_id == map_id for map_id in self.list_of_event_ids])

    def is_wa_id_in_mapping_list(self, wa_id: str) -> bool:
        return any([wa_id == map_id for map_id in self.list_of_wa_ids])

    def get_wa_id_for_event(self, event_id: str) -> str:
        try:
            assert self.is_event_in_mapping_list(event_id)
        except:
            raise NO_EVENT_ID

        idx = self.list_of_event_ids.index(event_id)
        return self.list_of_wa_ids[idx]

    def get_event_id_for_wa(self, wa_id: str) -> str:
        try:
            assert self.is_wa_id_in_mapping_list(wa_id)
        except:
            raise NO_WA_ID

        idx = self.list_of_wa_ids.index(wa_id)
        return self.list_of_event_ids[idx]

    @property
    def list_of_event_ids(self) -> list:
        return getattr(self, "_list_of_event_ids")

    @property
    def list_of_wa_ids(self) -> list:
        return getattr(self, "_list_of_wa_ids")
