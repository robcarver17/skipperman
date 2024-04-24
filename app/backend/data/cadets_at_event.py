from typing import List

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.mapped_wa_event import RowInMappedWAEvent, MappedWAEvent, RegistrationStatus

from app.backend.data.cadets import CadetData
from app.backend.data.mapped_events import MappedEventsData

from app.data_access.storage_layer.api import DataLayer

from app.data_access.data import DEPRECATED_data
from app.objects.cadets import Cadet, ListOfCadets
from app.objects.day_selectors import ListOfDaySelectors, DaySelector
from app.objects.events import Event

from app.objects.cadet_at_event import ListOfCadetsAtEvent, ListOfIdentifiedCadetsAtEvent, CadetAtEvent, \
    get_cadet_at_event_from_row_in_mapped_event
from app.objects.dinghies import ListOfCadetAtEventWithDinghies

def cadet_id_at_event_given_row_id(interface: abstractInterface, event: Event, row_id: str) -> str:
    cadet_data = CadetsAtEventData(interface.data)
    cadet_id = cadet_data.identifed_cadet_id_given_row_id_at_event(row_id=row_id, event=event)

    return cadet_id


class CadetsAtEventData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def update_availability_of_existing_cadet_at_event(self, event: Event, cadet_id: str,
                                                       new_availabilty: DaySelector):

        ## FIXME: FUTURE CHANGE CONSIDER EFFECT ON TWO HANDED PARTNERS WITH DIFFERENT AVAILABILITY
        existing_cadets_at_event = self.get_list_of_cadets_at_event(event)
        existing_cadets_at_event.update_availability_of_existing_cadet_at_event(cadet_id=cadet_id,
                                                                            new_availabilty=new_availabilty)
        self.save_list_of_cadets_at_event(list_of_cadets_at_event=existing_cadets_at_event, event=event)

    def update_status_of_existing_cadet_at_event_to_cancelled_or_deleted(self, event: Event, cadet_id: str,
                                                                         new_status: RegistrationStatus):

        existing_cadets_at_event = self.get_list_of_cadets_at_event(event)
        existing_cadets_at_event.update_status_of_existing_cadet_at_event(cadet_id=cadet_id,
                                                                      new_status=new_status)
        self.save_list_of_cadets_at_event(list_of_cadets_at_event=existing_cadets_at_event, event=event)

    def replace_existing_cadet_at_event(self, new_cadet_at_event: CadetAtEvent, event: Event):
        existing_cadets_at_event = self.get_list_of_cadets_at_event(event)
        existing_cadets_at_event.replace_existing_cadet_at_event(new_cadet_at_event)
        self.save_list_of_cadets_at_event(list_of_cadets_at_event=existing_cadets_at_event, event=event)

    def add_new_cadet_to_event(
            self,
            event: Event,
            row_in_mapped_wa_event: RowInMappedWAEvent,
            cadet_id: str
    ):
        cadet_at_event = get_cadet_at_event_from_row_in_mapped_event(event=event, cadet_id=cadet_id,
                                                                     row_in_mapped_wa_event=row_in_mapped_wa_event)
        existing_cadets_at_event = self.get_list_of_cadets_at_event(event)
        existing_cadets_at_event.add(cadet_at_event)
        self.save_list_of_cadets_at_event(event=event, list_of_cadets_at_event=existing_cadets_at_event)

    def get_all_rows_in_mapped_event_for_cadet_id(self, event: Event, cadet_id: str) ->  MappedWAEvent:

        identified_cadets = self.get_list_of_identified_cadets_at_event(event)
        mapped_event_data = self.get_mapped_wa_data_for_event(event)

        list_of_row_ids = identified_cadets.list_of_row_ids_given_cadet_id(cadet_id)
        relevant_rows =mapped_event_data.subset_with_id(list_of_row_ids)

        return relevant_rows

    def identified_cadet_ids_in_mapped_data(self, event: Event) -> list:
        mapped_event_data = self.mapped_wa_events_data
        row_ids = mapped_event_data.get_list_of_row_ids_for_event(event)
        list_of_cadet_ids = [self.identifed_cadet_id_given_row_id_at_event(row_id=row_id, event=event) for
                             row_id in row_ids]

        return list_of_cadet_ids

    def cadet_at_event_or_missing_data(self, event: Event, cadet_id: str) -> CadetAtEvent:
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)
        return list_of_cadets_at_event.cadet_at_event_or_missing_data(cadet_id)

    def is_cadet_with_id_already_at_event(self, event: Event, cadet_id: str):
        list_of_ids = self.list_of_all_cadet_ids_at_event(event)
        return cadet_id in list_of_ids


    def is_cadet_with_id_in_identified_list_for_event(self, event: Event, cadet_id) -> bool:
        identified_cadets = self.get_list_of_identified_cadets_at_event(event)
        return identified_cadets.is_cadet_with_id_in_identified_list(cadet_id)

    def identifed_cadet_id_given_row_id_at_event(self, event: Event, row_id:str) -> str:
        identified_cadets = self.get_list_of_identified_cadets_at_event(event)
        return identified_cadets.cadet_id_given_row_id(row_id)

    def mark_row_as_skip_cadet(self, event: Event, row_id: str):
        identified_cadets = self.get_list_of_identified_cadets_at_event(event)
        identified_cadets.add_cadet_to_skip(row_id=row_id)
        self.save_list_of_identified_cadets_at_event(event=event, list_of_identified_cadets_at_event=identified_cadets)

    def add_identified_cadet_and_row(self, event: Event, row_id: str, cadet_id: str):
        identified_cadets = self.get_list_of_identified_cadets_at_event(event)
        identified_cadets.add(row_id=row_id, cadet_id=cadet_id)
        self.save_list_of_identified_cadets_at_event(event=event, list_of_identified_cadets_at_event=identified_cadets)

    def row_has_identified_cadet_including_test_cadets(self, row: RowInMappedWAEvent, event: Event) -> bool:
        identified_cadets = self.get_list_of_identified_cadets_at_event(event)
        return identified_cadets.row_has_identified_cadet_including_test_cadets(row_id = row.row_id)


    def list_of_active_cadets_at_event(self, event: Event) -> ListOfCadets:
        active_ids = self.list_of_active_cadet_ids_at_event(event)
        list_of_cadets = self.cadet_data.get_list_of_cadets_given_list_of_cadet_ids(active_ids)

        return list_of_cadets

    def list_of_active_cadet_ids_at_event(self, event: Event) -> List[str]:
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)
        active_cadets_at_event = list_of_cadets_at_event.list_of_active_cadets_at_event()

        return active_cadets_at_event.list_of_cadet_ids()

    def list_of_all_cadet_ids_at_event(self, event: Event) -> List[str]:
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)

        return list_of_cadets_at_event.list_of_cadet_ids()

    def get_attendance_matrix_for_list_of_cadet_ids_at_event(self, list_of_cadet_ids: List[str], event: Event) -> ListOfDaySelectors:
        ### ALL CADETS mus tbe active
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)
        subset_list = list_of_cadets_at_event.subset_given_cadet_ids(list_of_cadet_ids)
        list_of_availability = ListOfDaySelectors([cadet_at_event.availability for cadet_at_event in subset_list])

        return list_of_availability

    def get_list_of_identified_cadets_at_event(self, event: Event)-> ListOfIdentifiedCadetsAtEvent:
        return self.data_api.get_list_of_identified_cadets_at_event(event)

    def save_list_of_identified_cadets_at_event(self, event: Event, list_of_identified_cadets_at_event: ListOfIdentifiedCadetsAtEvent):
        return self.data_api.save_list_of_identified_cadets_at_event(event=event, list_of_identified_cadets_at_event=list_of_identified_cadets_at_event)

    def get_list_of_cadets_at_event(self, event: Event) -> ListOfCadetsAtEvent:
        return self.data_api.get_list_of_cadets_at_event(event)

    def save_list_of_cadets_at_event(self, event: Event, list_of_cadets_at_event: ListOfCadetsAtEvent):
        return self.data_api.save_list_of_cadets_at_event(list_of_cadets_at_event=list_of_cadets_at_event, event=event)

    def get_mapped_wa_data_for_event(self, event: Event):
        return self.mapped_wa_events_data.get_mapped_wa_event(event)

    @property
    def mapped_wa_events_data(self) -> MappedEventsData:
        return MappedEventsData(self.data_api)

    @property
    def cadet_data(self) -> CadetData:
        return CadetData(self.data_api)

def DEPRECATE_cadet_id_at_event_given_row_id(event: Event, row_id: str) -> str:
    identified_cadets_at_event = DEPERCATE_load_identified_cadets_at_event(event)
    cadet_id = identified_cadets_at_event.cadet_id_given_row_id(row_id=row_id)

    return cadet_id


def list_of_row_ids_at_event_given_cadet_id(event: Event, cadet_id: str) -> List[str]:
    identified_cadets_at_event = DEPERCATE_load_identified_cadets_at_event(event)
    list_of_row_ids = identified_cadets_at_event.list_of_row_ids_given_cadet_id(cadet_id)

    return list_of_row_ids


def DEPRECATED_load_cadets_at_event(event: Event) -> ListOfCadetsAtEvent:
    return DEPRECATED_data.data_cadets_at_event.read(event_id=event.id)


def get_cadet_at_event(event: Event, cadet: Cadet)-> CadetAtEvent:
    cadets_at_event = DEPRECATED_load_cadets_at_event(event)

    return cadets_at_event.cadet_at_event_or_missing_data(cadet_id=cadet.id)

def save_cadets_at_event(event: Event , list_of_cadets_at_event: ListOfCadetsAtEvent):
    return DEPRECATED_data.data_cadets_at_event.write(list_of_cadets_at_event=list_of_cadets_at_event, event_id=event.id)

def DEPERCATE_load_identified_cadets_at_event(event: Event) -> ListOfIdentifiedCadetsAtEvent:
    return DEPRECATED_data.data_identified_cadets_at_event.read(event_id=event.id)

def DEPRECATE_save_identified_cadets_at_event(event: Event, list_of_cadets_at_event: ListOfIdentifiedCadetsAtEvent):
    DEPRECATED_data.data_identified_cadets_at_event.write(list_of_cadets_at_event=list_of_cadets_at_event, event_id=event.id)


def load_list_of_cadets_at_event_with_dinghies(event: Event) -> ListOfCadetAtEventWithDinghies:
    cadets_with_dinghies = DEPRECATED_data.data_list_of_cadets_with_dinghies_at_event.read(event.id)

    return cadets_with_dinghies

def save_list_of_cadets_at_event_with_dinghies(event: Event,
                                                    cadets_with_dinghies_at_event: ListOfCadetAtEventWithDinghies):

    DEPRECATED_data.data_list_of_cadets_with_dinghies_at_event.write(event_id=event.id, people_and_boats=cadets_with_dinghies_at_event)



