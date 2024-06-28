from dataclasses import dataclass

from app.objects.cadets import Cadet

from app.objects.cadet_with_id_at_event import CadetWithIdAtEvent
from app.objects.day_selectors import DaySelector
from app.objects.generic import GenericSkipperManObject, GenericListOfObjects

from app.objects.mapped_wa_event import RowInMappedWAEvent, RegistrationStatus


## following must match attributes


@dataclass
class CadetAtEvent(GenericSkipperManObject):
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


class ListOfCadetsAtEvent(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return CadetAtEvent
