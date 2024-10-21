from dataclasses import dataclass
from typing import List, Dict

from app.objects.exceptions import MissingData

from app.objects.cadet_with_id_at_event import CadetWithIdAtEvent, ListOfCadetsWithIDAtEvent
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.day_selectors import DaySelector
from app.objects.events import Event, ListOfEvents
from app.objects.registration_data import RegistrationStatus, RowInRegistrationData


@dataclass
class CadetRegistrationData:
    event: Event
    availability: DaySelector
    status: RegistrationStatus
    data_in_row: RowInRegistrationData
    notes: str = ""
    health: str = ""

    @classmethod
    def from_cadet_with_id_at_event(cls, event: Event, cadet_with_id_at_event: CadetWithIdAtEvent):
        availability = cadet_with_id_at_event.availability.intersect(event.day_selector_with_covered_days())

        return cls(
            event=event,
            availability=availability,
            status=cadet_with_id_at_event.status,
            data_in_row=cadet_with_id_at_event.data_in_row,
            notes=cadet_with_id_at_event.notes,
            health=cadet_with_id_at_event.health,
        )

    @property
    def active(self):
        return self.status.is_active

@dataclass
class DEPRECATE_CadetWithEventData:
    cadet: Cadet
    event_data: CadetRegistrationData

    @classmethod
    def from_cadet_with_id_at_event(cls, event: Event, cadet: Cadet, cadet_with_id_at_event: CadetWithIdAtEvent):
        return cls(cadet=cadet, event_data=CadetRegistrationData.from_cadet_with_id_at_event(event=event, cadet_with_id_at_event=cadet_with_id_at_event))


class DictOfCadetsWithRegistrationData(Dict[Cadet, CadetRegistrationData]):
    def __init__(self, raw_list: Dict[Cadet, CadetRegistrationData], list_of_cadets_with_id_at_event: ListOfCadetsWithIDAtEvent):
        super().__init__(raw_list)
        self._list_of_cadets_with_id_at_event = list_of_cadets_with_id_at_event

    def registration_data_for_cadet(self, cadet: Cadet) ->CadetRegistrationData:
        reg_data = self.get(cadet, None)
        if reg_data is None:
            raise MissingData

        return reg_data

    def list_of_active_cadets(self) ->ListOfCadets:
        return ListOfCadets([cadet for cadet, registration_data in self.items() if registration_data.active])

    def list_of_cadets(self):
        return ListOfCadets(list(self.keys()))

    @property
    def  list_of_cadets_with_id_at_event(self)-> ListOfCadetsWithIDAtEvent:
        return self._list_of_cadets_with_id_at_event




def compose_dict_of_cadets_with_event_data(list_of_cadets: ListOfCadets,
                                           list_of_events: ListOfEvents,
                                           event_id: str,
                                           list_of_cadets_with_id_at_event: ListOfCadetsWithIDAtEvent) -> DictOfCadetsWithRegistrationData:

    event = list_of_events.object_with_id(event_id)
    raw_dict = compose_raw_dict_of_cadets_with_event_data(
        event=event,
        list_of_cadets=list_of_cadets,
        list_of_cadets_with_id_at_event=list_of_cadets_with_id_at_event
    )
    return DictOfCadetsWithRegistrationData(raw_dict, list_of_cadets_with_id_at_event=list_of_cadets_with_id_at_event)

def compose_raw_dict_of_cadets_with_event_data(event: Event,
                                                list_of_cadets: ListOfCadets,
                                           list_of_cadets_with_id_at_event: ListOfCadetsWithIDAtEvent) -> Dict[Cadet, CadetRegistrationData]:

    return dict([(
        list_of_cadets.cadet_with_id(cadet_with_id_at_event.cadet_id),
        CadetRegistrationData.from_cadet_with_id_at_event(
        cadet_with_id_at_event=cadet_with_id_at_event,
        event=event
    ))
        for cadet_with_id_at_event in list_of_cadets_with_id_at_event
    ])