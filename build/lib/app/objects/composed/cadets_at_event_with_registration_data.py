from dataclasses import dataclass
from typing import List, Dict

from app.data_access.configuration.field_list import RESPONSIBLE_ADULT_NUMBER, RESPONSIBLE_ADULT_NAME
from app.objects.utils import flatten

from app.backend.cadets.list_of_cadets import sort_a_list_of_cadets
from app.objects.exceptions import MissingData, arg_not_passed

from app.objects.cadet_with_id_at_event import (
    CadetWithIdAtEvent,
    ListOfCadetsWithIDAtEvent,
)
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.day_selectors import DaySelector
from app.objects.events import Event, ListOfEvents
from app.objects.registration_data import RowInRegistrationData
from app.objects.registration_status import RegistrationStatus


@dataclass
class CadetRegistrationData:
    event: Event
    availability: DaySelector
    status: RegistrationStatus
    data_in_row: RowInRegistrationData
    notes: str = ""
    health: str = ""

    @property
    def emergency_contact(self):
        contact = self.data_in_row.get_item(RESPONSIBLE_ADULT_NUMBER, '')
        contact_name = self.data_in_row.get_item(RESPONSIBLE_ADULT_NAME, '')

        return "%s (%s)" % (contact_name, str(contact))

    @property
    def data_fields(self) -> List[str]:
        return list(self.data_in_row.keys())

    @classmethod
    def from_cadet_with_id_at_event(
        cls, event: Event, cadet_with_id_at_event: CadetWithIdAtEvent
    ):
        availability = cadet_with_id_at_event.availability.intersect(
            event.day_selector_for_days_in_event()
        )

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
    def from_cadet_with_id_at_event(
        cls, event: Event, cadet: Cadet, cadet_with_id_at_event: CadetWithIdAtEvent
    ):
        return cls(
            cadet=cadet,
            event_data=CadetRegistrationData.from_cadet_with_id_at_event(
                event=event, cadet_with_id_at_event=cadet_with_id_at_event
            ),
        )

class DictOfCadetsWithRegistrationData(Dict[Cadet, CadetRegistrationData]):
    def __init__(
        self,
        raw_list: Dict[Cadet, CadetRegistrationData],
        list_of_cadets_with_id_at_event: ListOfCadetsWithIDAtEvent,
    ):
        super().__init__(raw_list)
        self._list_of_cadets_with_id_at_event = list_of_cadets_with_id_at_event

    def update_availability_of_existing_cadet_at_event(
            self, cadet: Cadet,
            new_availabilty: DaySelector,
    ):

        registration_data = self.registration_data_for_cadet(cadet)
        registration_data.availability = new_availabilty
        cadet_at_event_data = self.list_of_cadets_with_id_at_event.cadet_at_event(cadet)
        cadet_at_event_data.availability = new_availabilty

    def update_status_of_existing_cadet_in_event_info_to_cancelled_or_deleted(self,
            cadet: Cadet, new_status: RegistrationStatus):

        self[cadet].status = new_status
        cadet_at_event_with_id = self.list_of_cadets_with_id_at_event.cadet_at_event(cadet)
        cadet_at_event_with_id.status = new_status

    def list_of_registration_fields(self):
        all_fields = [
            reg_data.data_fields for reg_data in list(self.values())
        ]
        all_fields = flatten(all_fields)
        return list(set(all_fields))

    def get_emergency_contact_for_list_of_cadets_at_event(self,  list_of_cadets: ListOfCadets) -> List[str]:
        list_of_contacts = []
        for cadet in list_of_cadets:
            try:
                reg_data = self.registration_data_for_cadet(cadet)
                list_of_contacts.append(reg_data.emergency_contact)
            except MissingData:
                list_of_contacts.append("")

        return list_of_contacts

    def get_health_notes_for_list_of_cadets_at_event(self, list_of_cadets: ListOfCadets) -> List[str]:
        list_of_contacts = []
        for cadet in list_of_cadets:
            try:
                reg_data = self.registration_data_for_cadet(cadet)
                list_of_contacts.append(reg_data.health)
            except MissingData:
                list_of_contacts.append("")

        return list_of_contacts

    def registration_data_for_cadet(self, cadet: Cadet) -> CadetRegistrationData:
        reg_data = self.get(cadet, None)
        if reg_data is None:
            raise MissingData

        return reg_data

    def list_of_active_cadets(self) -> ListOfCadets:
        return ListOfCadets(
            [
                cadet
                for cadet, registration_data in self.items()
                if registration_data.active
            ]
        )

    def list_of_cadets(self):
        return ListOfCadets(list(self.keys()))

    def sort_by(self, sort_by: str = arg_not_passed) -> 'DictOfCadetsWithRegistrationData':
        list_of_cadets = self.list_of_cadets()
        sorted_list_of_cadets= sort_a_list_of_cadets(list_of_cadets, sort_by=sort_by)

        return DictOfCadetsWithRegistrationData(dict([
            (cadet, self[cadet])
            for cadet in sorted_list_of_cadets
        ]),
        list_of_cadets_with_id_at_event=self.list_of_cadets_with_id_at_event)

    @property
    def list_of_cadets_with_id_at_event(self) -> ListOfCadetsWithIDAtEvent:
        return self._list_of_cadets_with_id_at_event


def compose_dict_of_cadets_with_event_data(
    list_of_cadets: ListOfCadets,
    list_of_events: ListOfEvents,
    event_id: str,
    list_of_cadets_with_id_at_event: ListOfCadetsWithIDAtEvent,
) -> DictOfCadetsWithRegistrationData:
    event = list_of_events.object_with_id(event_id)
    raw_dict = compose_raw_dict_of_cadets_with_event_data(
        event=event,
        list_of_cadets=list_of_cadets,
        list_of_cadets_with_id_at_event=list_of_cadets_with_id_at_event,
    )
    return DictOfCadetsWithRegistrationData(
        raw_dict, list_of_cadets_with_id_at_event=list_of_cadets_with_id_at_event
    )


def compose_raw_dict_of_cadets_with_event_data(
    event: Event,
    list_of_cadets: ListOfCadets,
    list_of_cadets_with_id_at_event: ListOfCadetsWithIDAtEvent,
) -> Dict[Cadet, CadetRegistrationData]:
    return dict(
        [
            (
                list_of_cadets.cadet_with_id(cadet_with_id_at_event.cadet_id),
                CadetRegistrationData.from_cadet_with_id_at_event(
                    cadet_with_id_at_event=cadet_with_id_at_event, event=event
                ),
            )
            for cadet_with_id_at_event in list_of_cadets_with_id_at_event
        ]
    )
