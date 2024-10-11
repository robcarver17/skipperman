from dataclasses import dataclass
from typing import List

from app.objects.events import Event

from app.objects.cadets import Cadet

from app.objects.cadet_with_id_at_event import CadetWithIdAtEvent
from app.objects.day_selectors import DaySelector
from app.objects.generic_list_of_objects import GenericListOfObjects
from app.objects.generic_objects import GenericSkipperManObject

from app.objects_OLD.mapped_wa_event import RowInMappedWAEvent, RegistrationStatus


@dataclass
class CadetEventData:
    event: Event
    availability: DaySelector
    status: RegistrationStatus
    data_in_row: RowInMappedWAEvent
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



@dataclass
class CadetAtEvent:
    cadet: Cadet
    event_data: CadetEventData

    @classmethod
    def from_cadet_with_id_at_event(cls, event: Event, cadet: Cadet, cadet_with_id_at_event: CadetWithIdAtEvent):
        return cls(cadet=cadet, event_data=CadetEventData.from_cadet_with_id_at_event(event=event, cadet_with_id_at_event=cadet_with_id_at_event))

class ListOfCadetsAtEvent(List[CadetAtEvent]):
    pass

@dataclass
class DEPRECATE_CadetAtEvent(GenericSkipperManObject):
    cadet: Cadet
    availability: DaySelector
    status: RegistrationStatus
    data_in_row: RowInMappedWAEvent
    notes: str = ""
    health: str = ""
    changed: bool = False

    @classmethod
    def from_cadet_with_id_at_event(
        cls, cadet: Cadet, cadet_with_id_at_event: CadetWithIdAtEvent
    ):
        return cls(
            cadet=cadet,
            availability=cadet_with_id_at_event.availability,
            status=cadet_with_id_at_event.status,
            data_in_row=cadet_with_id_at_event.data_in_row,
            notes=cadet_with_id_at_event.notes,
            health=cadet_with_id_at_event.health,
            changed=cadet_with_id_at_event.changed,
        )


class DEPRECATE_ListOfCadetsAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return DEPRECATE_CadetAtEvent
