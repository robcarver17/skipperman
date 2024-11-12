from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.data_access.store.store import DataAccessMethod

from app.OLD_backend.data.cadets import CadetData

from app.data_access.store.data_access import DataLayer

from app.objects.events import Event

from app.objects_OLD.cadet_at_event import DEPRECATE_ListOfCadetsAtEvent


class CadetsAtEventData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api
        self.store = data_api.store

    def get_list_of_cadets_at_event(
        self, event: Event
    ) -> DEPRECATE_ListOfCadetsAtEvent:
        data_method = get_data_access_list_of_cadets_at_event(
            self.cadets_at_event_id_level_data, event=event
        )
        return self.store.read(data_method)

    @property
    def cadets_at_event_id_level_data(self) -> CadetsAtEventIdLevelData:
        return CadetsAtEventIdLevelData(self.data_api)

    @property
    def cadet_data(self) -> CadetData:
        return CadetData(self.data_api)


def get_data_access_list_of_cadets_at_event(
    cadets_at_event_id_level_data: CadetsAtEventIdLevelData, event: Event
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_cadets_at_event",
        read_method=cadets_at_event_id_level_data.get_list_of_cadets_at_event,
        write_method=cadets_at_event_id_level_data.get_list_of_cadets_at_event,  ##FIXME CHANGE
        event=event,
    )
