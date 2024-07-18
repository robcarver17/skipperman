
from app.data_access.data_layer.data_layer import DataLayer

from app.objects.events import Event

from app.objects.cadet_at_event import  ListOfCadetsAtEvent, CadetAtEvent, CadetEventData
from app.objects.primtive_with_id.cadet_with_id_at_event import ListOfCadetsWithIDAtEvent, CadetWithIdAtEvent

class CadetsAtEventData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api
        self.store = data_api.store

    def get_list_of_cadets_at_event(self, event: Event) -> ListOfCadetsAtEvent:
        list_of_cadets_with_id_at_event = self.get_list_of_cadets_with_id_at_event(event)
        list_of_cadets_at_event = [
            self.get_cadet_at_event(event=event, cadet_with_id_at_event=cadet_with_id_at_event)
            for cadet_with_id_at_event in list_of_cadets_with_id_at_event
        ]

        return ListOfCadetsAtEvent(list_of_cadets_at_event)

    def get_cadet_at_event(self, event: Event, cadet_with_id_at_event: CadetWithIdAtEvent) -> CadetAtEvent:
        list_of_cadets = self.get_list_of_cadets()
        return CadetAtEvent.from_cadet_with_id_at_event(
            cadet=list_of_cadets.cadet_with_id(cadet_with_id_at_event.cadet_id),
            event=event,
            cadet_with_id_at_event=cadet_with_id_at_event
            )

    def get_list_of_cadets_with_id_at_event(self, event: Event) -> ListOfCadetsWithIDAtEvent:
        return self.data_api.get_list_of_cadets_at_event(event)

    def get_list_of_cadets(self):
        return self.data_api.get_list_of_cadets()
