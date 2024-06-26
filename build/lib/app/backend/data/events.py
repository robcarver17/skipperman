from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.data_access.storage_layer.api import DataLayer

from app.objects.events import Event, ListOfEvents


def get_event_from_id(interface: abstractInterface, event_id: str) -> Event:
    ed = EventData(interface.data)
    return ed.get_event_from_id(event_id)


class EventData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def add_event(self, event: Event):
        list_of_events = self.list_of_events
        list_of_events.add(event)
        self.save_list_of_events(list_of_events)

    def get_event_from_id(self, event_id: str) -> Event:
        list_of_events = self.list_of_events
        return list_of_events.has_id(event_id)

    @property
    def list_of_events(self) -> ListOfEvents:
        return self.data_api.get_list_of_events()

    def save_list_of_events(self, list_of_events: ListOfEvents):
        self.data_api.save_list_of_events(list_of_events)
