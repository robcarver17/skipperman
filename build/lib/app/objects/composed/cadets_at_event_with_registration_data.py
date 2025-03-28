from dataclasses import dataclass
from typing import List, Dict

from app.data_access.configuration.field_list import (
    RESPONSIBLE_ADULT_NUMBER,
    RESPONSIBLE_ADULT_NAME,
    CADET_DOUBLE_HANDED_PARTNER,
)
from app.objects.utils import flatten

from app.objects.exceptions import MissingData, arg_not_passed, missing_data

from app.objects.cadet_with_id_at_event import (
    CadetWithIdAtEvent,
    ListOfCadetsWithIDAtEvent,
)
from app.objects.cadets import Cadet, ListOfCadets, sort_a_list_of_cadets
from app.objects.day_selectors import DaySelector, Day
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

    def update_column_in_data(self,
                        column_name: str,
                        new_value_for_column):

        self.data_in_row[column_name] = new_value_for_column

    def clean_data(self):
        self.data_in_row.clear_values()
        self.health = ""
        self.notes = ""

    def two_handed_partner(self, default=arg_not_passed):
        partner = self.data_in_row.get_item(CADET_DOUBLE_HANDED_PARTNER, missing_data)
        if partner is missing_data:
            if default is arg_not_passed:
                raise MissingData
            else:
                return default

        return partner.strip(" ")

    @property
    def emergency_contact(self):
        contact = self.data_in_row.get_item(RESPONSIBLE_ADULT_NUMBER, "")
        contact_name = self.data_in_row.get_item(RESPONSIBLE_ADULT_NAME, "")

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

    def update_notes(self, new_notes: str):
        self.notes = new_notes

    def update_health(self, new_health: str):
        self.health = new_health

class DictOfCadetsWithRegistrationData(Dict[Cadet, CadetRegistrationData]):
    def __init__(
        self,
        raw_list: Dict[Cadet, CadetRegistrationData],
        list_of_cadets_with_id_at_event: ListOfCadetsWithIDAtEvent,
    ):
        super().__init__(raw_list)
        self._list_of_cadets_with_id_at_event = list_of_cadets_with_id_at_event

    def update_health_for_existing_cadet_at_event(
            self, cadet: Cadet, new_health: str
    ):
        reg_data_for_cadet = self.registration_data_for_cadet(cadet)
        reg_data_for_cadet.update_health(new_health)

        self.list_of_cadets_with_id_at_event.update_health_for_existing_cadet_at_event(
            cadet_id=cadet.id,
             new_health=new_health
        )

    def update_row_in_registration_data_for_existing_cadet_at_event(self, cadet: Cadet,
                                                                    column_name: str,
                                                                    new_value_for_column
                                                                    ):
        reg_data_for_cadet = self.registration_data_for_cadet(cadet)
        existing_value =reg_data_for_cadet.data_in_row[column_name]
        if existing_value==new_value_for_column:
            return

        reg_data_for_cadet.update_column_in_data(column_name=column_name, new_value_for_column=new_value_for_column)
        self.list_of_cadets_with_id_at_event.update_data_row_for_existing_cadet_at_event(
            cadet_id=cadet.id,
            column_name=column_name,
            new_value_for_column=new_value_for_column
        )

    def update_notes_for_existing_cadet_at_event(self, cadet: Cadet, notes: str):
        reg_data_for_cadet = self.registration_data_for_cadet(cadet)
        reg_data_for_cadet.update_notes(notes)

        ## propogate down
        self.list_of_cadets_with_id_at_event.update_notes_for_existing_cadet_at_event(
            cadet_id=cadet.id,
            new_notes=notes
        )

    def availability_dict(self) -> Dict[Cadet, DaySelector]:
        return dict(
            [
                (cadet, self.registration_data_for_cadet(cadet).availability)
                for cadet in self.list_of_cadets()
            ]
        )

    def clear_user_data(self):
        for reg_data_for_cadet in self.values():
            reg_data_for_cadet.clean_data()

        self.list_of_cadets_with_id_at_event.clear_private_data()

    def make_cadet_available_on_day(self, cadet: Cadet, day: Day):

        registration_data = self.registration_data_for_cadet(cadet)
        registration_data.availability.make_available_on_day(day)

        cadet_at_event_data = (
            self.list_of_cadets_with_id_at_event.cadet_with_id_and_data_at_event(
                cadet_id=cadet.id
            )
        )
        cadet_at_event_data.availability.make_available_on_day(day)

    def make_cadet_unavailable_on_day(self, cadet: Cadet, day: Day):

        registration_data = self.registration_data_for_cadet(cadet)
        registration_data.availability.make_unavailable_on_day(day)

        cadet_at_event_data = (
            self.list_of_cadets_with_id_at_event.cadet_with_id_and_data_at_event(
                cadet_id=cadet.id
            )
        )
        cadet_at_event_data.availability.make_unavailable_on_day(day)

    def update_status_of_existing_cadet_in_event_info(
        self, cadet: Cadet, new_status: RegistrationStatus
    ):
        existing_registration = self.registration_data_for_cadet(cadet)
        existing_registration.status = new_status

        cadet_at_event_with_id = (
            self.list_of_cadets_with_id_at_event.cadet_with_id_and_data_at_event(
                cadet_id=cadet.id
            )
        )
        cadet_at_event_with_id.status = new_status

    def list_of_registration_fields(self):
        all_fields = [reg_data.data_fields for reg_data in list(self.values())]
        all_fields = flatten(all_fields)
        return list(set(all_fields))

    def get_emergency_contact_for_list_of_cadets_at_event(
        self, list_of_cadets: ListOfCadets
    ) -> List[str]:
        list_of_contacts = []
        for cadet in list_of_cadets:
            reg_data = self.registration_data_for_cadet(cadet, default=missing_data)
            if reg_data is missing_data:
                list_of_contacts.append("")
            else:
                list_of_contacts.append(reg_data.emergency_contact)

        return list_of_contacts

    def get_health_notes_for_list_of_cadets_at_event(
        self, list_of_cadets: ListOfCadets
    ) -> List[str]:
        list_of_contacts = []
        for cadet in list_of_cadets:
            reg_data = self.registration_data_for_cadet(cadet, default=missing_data)
            if reg_data is missing_data:
                list_of_contacts.append("")
            else:
                list_of_contacts.append(reg_data.health)

        return list_of_contacts

    def registration_data_for_cadet(
        self, cadet: Cadet, default=arg_not_passed
    ) -> CadetRegistrationData:
        reg_data = self.get(cadet, missing_data)
        if reg_data is missing_data:
            if default is arg_not_passed:
                raise MissingData
            else:
                return default

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

    def sort_by(
        self, sort_by: str = arg_not_passed
    ) -> "DictOfCadetsWithRegistrationData":
        list_of_cadets = self.list_of_cadets()
        sorted_list_of_cadets = sort_a_list_of_cadets(list_of_cadets, sort_by=sort_by)

        return DictOfCadetsWithRegistrationData(
            dict([(cadet, self[cadet]) for cadet in sorted_list_of_cadets]),
            list_of_cadets_with_id_at_event=self.list_of_cadets_with_id_at_event,
        )

    @property
    def list_of_cadets_with_id_at_event(self) -> ListOfCadetsWithIDAtEvent:
        return self._list_of_cadets_with_id_at_event


def compose_dict_of_cadets_with_event_data(
    list_of_cadets: ListOfCadets,
    list_of_events: ListOfEvents,
    event_id: str,
    list_of_cadets_with_id_at_event: ListOfCadetsWithIDAtEvent,
) -> DictOfCadetsWithRegistrationData:

    event = list_of_events.event_with_id(event_id)
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
