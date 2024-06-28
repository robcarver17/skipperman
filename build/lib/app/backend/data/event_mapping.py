from app.objects.events import Event

from app.data_access.storage_layer.api import DataLayer

from app.objects.wa_event_mapping import ListOfWAEventMaps


class EventMappingData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def add_event(self, event_id: str, wa_id: str):
        mapping_data = self.wa_mapping_data
        mapping_data.add_event(event_id=event_id, wa_id=wa_id)
        self.save_wa_mapping_data(mapping_data)

    def is_event_in_mapping_list(self, event: Event) -> bool:
        return self.wa_mapping_data.is_event_in_mapping_list(event_id=event.id)

    def get_wa_id_for_event(self, event: Event) -> str:
        return self.wa_mapping_data.get_wa_id_for_event(event_id=event.id)

    def is_wa_id_in_mapping_list(self, wa_id: str):
        return self.wa_mapping_data.is_wa_id_in_mapping_list(wa_id)

    def get_event_id_for_wa_id(self, wa_id: str) -> str:
        return self.wa_mapping_data.get_event_id_for_wa(wa_id)

    @property
    def wa_mapping_data(self) -> ListOfWAEventMaps:
        return self.data_api.get_wa_event_mapping()

    def save_wa_mapping_data(self, list_of_wa_event_maps: ListOfWAEventMaps):
        return self.data_api.save_wa_event_mapping(list_of_wa_event_maps)
