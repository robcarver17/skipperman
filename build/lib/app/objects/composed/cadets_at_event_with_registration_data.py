from dataclasses import dataclass
from typing import List, Dict

from app.data_access.configuration.field_list import (
    RESPONSIBLE_ADULT_NUMBER,
    RESPONSIBLE_ADULT_NAME,
    CADET_DOUBLE_HANDED_PARTNER,
)
from app.data_access.configuration.field_list_groups import (
    FIELDS_TO_EDIT_IN_EDIT_VIEW,
    FIELDS_VIEW_ONLY_IN_EDIT_VIEW,
)
from app.objects.utilities.utils import flatten

from app.objects.utilities.exceptions import MissingData, arg_not_passed, missing_data

from app.objects.cadet_with_id_at_event import (
    CadetWithIdAtEvent
)
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.utilities.cadet_matching_and_sorting import sort_a_list_of_cadets
from app.objects.day_selectors import DaySelector, empty_day_selector
from app.objects.events import Event
from app.objects.registration_data import RowInRegistrationData
from app.objects.registration_status import RegistrationStatus, empty_status


@dataclass
class CadetRegistrationData:
    availability: DaySelector
    status: RegistrationStatus
    data_in_row: RowInRegistrationData
    notes: str = ""
    health: str = ""

    def availability_empty_if_inactive(self):
        if self.status.is_active:
            return self.availability
        else:
            return empty_day_selector

    @classmethod
    def create_empty(cls):
        return cls(
            availability=empty_day_selector,
            status=empty_status,
            data_in_row=RowInRegistrationData.create_empty(),
            notes="",
            health="",
        )

    def update_column_in_data(self, column_name: str, new_value_for_column):
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


    def availability_dict(self) -> Dict[Cadet, DaySelector]:
        return dict(
            [
                (
                    cadet,
                    self.registration_data_for_cadet(
                        cadet
                    ).availability_empty_if_inactive(),
                )
                for cadet in self.list_of_cadets()
            ]
        )


    def list_of_registration_fields(self):
        all_fields = [reg_data.data_fields for reg_data in list(self.values())]
        all_fields = flatten(all_fields)
        list_of_fields = list(set(all_fields))

        return get_ordered_list_of_columns_excluding_special_fields(list_of_fields)

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
                return CadetRegistrationData.create_empty()
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
            dict([(cadet, self[cadet]) for cadet in sorted_list_of_cadets])
        )


def get_ordered_list_of_columns_excluding_special_fields(
    field_names: List[str],
) -> list:
    all_columns = get_columns_to_edit(field_names) + get_columns_to_view(field_names)

    return all_columns


def get_columns_to_edit(all_columns: List[str]) -> list:
    columns_to_edit = [
        column_name
        for column_name in FIELDS_TO_EDIT_IN_EDIT_VIEW
        if column_name in all_columns
    ]  ## preserve order

    return columns_to_edit


def get_columns_to_view(all_columns: List[str]) -> list:
    columns_to_view = [
        column_name
        for column_name in FIELDS_VIEW_ONLY_IN_EDIT_VIEW
        if column_name in all_columns
    ]  ## preserve order

    return columns_to_view
