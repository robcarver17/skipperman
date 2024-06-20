from typing import List, Dict

from app.objects.constants import missing_data

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.mapped_wa_event import RowInMappedWAEvent, MappedWAEvent, RegistrationStatus

from app.backend.data.cadets import CadetData
from app.backend.data.mapped_events import MappedEventsData

from app.data_access.storage_layer.api import DataLayer

from app.objects.cadets import ListOfCadets
from app.objects.day_selectors import ListOfDaySelectors, DaySelector, Day
from app.objects.events import Event

from app.objects.cadet_at_event import ListOfCadetsAtEvent, ListOfIdentifiedCadetsAtEvent, CadetAtEvent, \
    get_cadet_at_event_from_row_in_mapped_event
from app.objects.cadet_at_event import active_status

def cadet_id_at_event_given_row_id(interface: abstractInterface, event: Event, row_id: str) -> str:
    cadet_data = CadetsAtEventData(interface.data)
    cadet_id = cadet_data.identifed_cadet_id_given_row_id_at_event(row_id=row_id, event=event)

    return cadet_id



class CadetsAtEventData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    ### UPDATES
    def clear_health_information(self, event: Event):
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)
        list_of_ids = list_of_cadets_at_event.list_of_cadet_ids()

        for id in list_of_ids:
            self.update_health_for_existing_cadet_with_id_at_event(event=event, cadet_id=id, new_health='')

    def clear_row_data(self, event: Event):
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)
        list_of_ids = list_of_cadets_at_event.list_of_cadet_ids()

        for id in list_of_ids:
            self.clear_data_row_for_existing_cadet_at_event(event=event, cadet_id=id)

    def mark_cadet_at_event_as_unchanged(self, cadet_id: str, event: Event):
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)
        list_of_cadets_at_event.mark_cadet_as_unchanged(cadet_id)
        self.save_list_of_cadets_at_event(list_of_cadets_at_event=list_of_cadets_at_event, event=event)

    def mark_row_as_skip_cadet(self, event: Event, row_id: str):
        identified_cadets = self.get_list_of_identified_cadets_at_event(event)
        identified_cadets.add_cadet_to_skip(row_id=row_id)
        self.save_list_of_identified_cadets_at_event(event=event, list_of_identified_cadets_at_event=identified_cadets)

    def add_identified_cadet_and_row(self, event: Event, row_id: str, cadet_id: str):
        identified_cadets = self.get_list_of_identified_cadets_at_event(event)
        identified_cadets.add(row_id=row_id, cadet_id=cadet_id)
        self.save_list_of_identified_cadets_at_event(event=event, list_of_identified_cadets_at_event=identified_cadets)


    def clear_data_row_for_existing_cadet_at_event(self, event: Event, cadet_id: str):

        existing_cadets_at_event = self.get_list_of_cadets_at_event(event)
        existing_cadets_at_event.clear_data_row_for_existing_cadet_at_event(cadet_id=cadet_id)
        self.save_list_of_cadets_at_event(list_of_cadets_at_event=existing_cadets_at_event, event=event)



    def update_data_row_for_existing_cadet_at_event(self, event: Event, cadet_id: str,
                                                    new_data_in_row: RowInMappedWAEvent):

        existing_cadets_at_event = self.get_list_of_cadets_at_event(event)
        existing_cadets_at_event.update_data_row_for_existing_cadet_at_event(cadet_id=cadet_id,
                                                                             new_data_in_row=new_data_in_row)
        self.save_list_of_cadets_at_event(list_of_cadets_at_event=existing_cadets_at_event, event=event)


    def update_notes_for_existing_cadet_at_event(self, event: Event, cadet_id: str,
                                                 new_notes: str):

        existing_cadets_at_event = self.get_list_of_cadets_at_event(event)
        existing_cadets_at_event.update_notes_for_existing_cadet_at_event(cadet_id=cadet_id, new_notes=new_notes)
        self.save_list_of_cadets_at_event(list_of_cadets_at_event=existing_cadets_at_event, event=event)


    def update_health_for_existing_cadet_with_id_at_event(self, event: Event, cadet_id: str,
                                                          new_health: str):

        existing_cadets_at_event = self.get_list_of_cadets_at_event(event)
        existing_cadets_at_event.update_health_for_existing_cadet_at_event(cadet_id=cadet_id, new_health=new_health)
        self.save_list_of_cadets_at_event(list_of_cadets_at_event=existing_cadets_at_event, event=event)



    def update_availability_of_existing_cadet_at_event(self, event: Event, cadet_id: str,
                                                       new_availabilty: DaySelector):

        existing_cadets_at_event = self.get_list_of_cadets_at_event(event)
        existing_cadets_at_event.update_availability_of_existing_cadet_at_event(cadet_id=cadet_id,
                                                                            new_availabilty=new_availabilty)
        self.save_list_of_cadets_at_event(list_of_cadets_at_event=existing_cadets_at_event, event=event)

    def make_cadet_available_on_day(self, event: Event, cadet_id: str, day: Day):
        existing_cadets_at_event = self.get_list_of_cadets_at_event(event)
        cadet = existing_cadets_at_event.cadet_at_event(cadet_id)
        cadet.availability.make_available_on_day(day)
        self.save_list_of_cadets_at_event(list_of_cadets_at_event=existing_cadets_at_event, event=event)

    def update_status_of_existing_cadet_at_event_to_cancelled_or_deleted(self, event: Event, cadet_id: str,
                                                                         new_status: RegistrationStatus):

        existing_cadets_at_event = self.get_list_of_cadets_at_event(event)
        print("update %s to %s" % (cadet_id, new_status.name))
        existing_cadets_at_event.update_status_of_existing_cadet_at_event(cadet_id=cadet_id,
                                                                      new_status=new_status)
        self.save_list_of_cadets_at_event(list_of_cadets_at_event=existing_cadets_at_event, event=event)


    def update_status_of_existing_cadet_at_event_to_active(self, event: Event, cadet_id: str):

        existing_cadets_at_event = self.get_list_of_cadets_at_event(event)
        existing_cadets_at_event.update_status_of_existing_cadet_at_event(cadet_id=cadet_id,
                                                                      new_status=active_status)
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

    ### GETS
    def get_sorted_list_of_cadets_at_event(self, event: Event, sort_by: str) -> ListOfCadetsAtEvent:
        cadets_at_event = self.get_list_of_cadets_at_event(event)
        list_of_cadets = self.cadet_data.get_sorted_list_of_cadets(sort_by=sort_by)
        cadets_at_event = cadets_at_event.subset_given_cadet_ids(list_of_cadets.list_of_ids)

        return cadets_at_event


    def get_all_rows_in_mapped_event_for_cadet_id(self, event: Event, cadet_id: str) ->  MappedWAEvent:

        identified_cadets = self.get_list_of_identified_cadets_at_event(event)
        mapped_event_data = self.get_mapped_wa_data_for_event(event)

        list_of_row_ids = identified_cadets.list_of_row_ids_given_cadet_id_allowing_duplicates(cadet_id)
        relevant_rows =mapped_event_data.subset_with_id(list_of_row_ids)

        return relevant_rows

    def identified_cadet_ids_in_mapped_data(self, event: Event) -> list:
        mapped_event_data = self.mapped_wa_events_data
        row_ids = mapped_event_data.get_list_of_row_ids_for_event(event)
        list_of_cadet_ids = [self.identifed_cadet_id_given_row_id_at_event(row_id=row_id, event=event) for
                             row_id in row_ids]
        list_of_cadet_ids = [cadet_id for cadet_id in list_of_cadet_ids if cadet_id is not missing_data]


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


    def row_has_identified_cadet_including_test_cadets(self, row: RowInMappedWAEvent, event: Event) -> bool:
        identified_cadets = self.get_list_of_identified_cadets_at_event(event)
        return identified_cadets.row_has_identified_cadet_including_test_cadets(row_id = row.row_id)

    def list_of_active_cadets_available_on_day(self, event: Event, day: Day) -> ListOfCadets:
        cadets_at_event = self.list_of_active_cadets_at_event_available_on_day(event=event,
                                                                               day=day)
        active_ids = cadets_at_event.list_of_cadet_ids()
        list_of_cadets = self.cadet_data.get_list_of_cadets_given_list_of_cadet_ids(active_ids)

        return list_of_cadets


    def list_of_active_cadets_at_event_available_on_day(self, event: Event, day: Day) -> ListOfCadetsAtEvent:
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)
        return list_of_cadets_at_event.active_and_available_on_day(day)

    def list_of_active_cadets_at_event(self, event: Event) -> ListOfCadets:
        active_ids = self.list_of_active_cadet_ids_at_event(event)
        list_of_cadets = self.cadet_data.get_list_of_cadets_given_list_of_cadet_ids(active_ids)

        return list_of_cadets

    def list_of_cadet_ids_at_event_including_cancelled_and_deleted(self, event: Event):
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)

        return list_of_cadets_at_event.list_of_cadet_ids()


    def list_of_active_cadet_ids_at_event(self, event: Event) -> List[str]:
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)
        active_cadets_at_event = list_of_cadets_at_event.list_of_active_cadets_at_event()

        return active_cadets_at_event.list_of_cadet_ids()

    def list_of_all_cadet_ids_at_event(self, event: Event) -> List[str]:
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)

        return list_of_cadets_at_event.list_of_cadet_ids()

    def get_availability_dict_for_active_cadet_ids_at_event(self, event: Event) -> Dict[str, DaySelector]:
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)
        active_cadets_at_event = list_of_cadets_at_event.list_of_active_cadets_at_event()

        return dict([(cadet.cadet_id, cadet.availability)
              for cadet in active_cadets_at_event])


    def get_attendance_matrix_for_list_of_cadet_ids_at_event(self, list_of_cadet_ids: List[str], event: Event) -> ListOfDaySelectors:
        ### ALL CADETS mus tbe active
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)
        subset_list = list_of_cadets_at_event.subset_given_cadet_ids(list_of_cadet_ids)
        list_of_availability = ListOfDaySelectors([cadet_at_event.availability for cadet_at_event in subset_list])

        return list_of_availability

    def get_health_notes_for_list_of_cadet_ids_at_event(self, event: Event, list_of_cadet_ids: List[str])-> List[str]:
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)
        subset_list = list_of_cadets_at_event.subset_given_cadet_ids(list_of_cadet_ids)

        health_notes = []
        for cadet_at_event in subset_list:
            health_for_cadet = cadet_at_event.health
            if len(health_for_cadet)==0:
                health_for_cadet='none'
            health_notes.append(health_for_cadet)

        return health_notes


    def get_emergency_contact_for_list_of_cadet_ids_at_event(self, event: Event, list_of_cadet_ids: List[str])-> List[str]:
        list_of_cadets_at_event = self.get_list_of_cadets_at_event(event)
        subset_list = list_of_cadets_at_event.subset_given_cadet_ids(list_of_cadet_ids)

        list_of_contacts = []
        for cadet_at_event in subset_list:
            contact =cadet_at_event.emergency_contact()
            list_of_contacts.append(contact)

        return list_of_contacts

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


def list_of_row_ids_at_event_given_cadet_id(interface: abstractInterface, event: Event, cadet_id: str) -> List[str]:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    identified_cadets_at_event = cadets_at_event_data.get_list_of_identified_cadets_at_event(event)
    list_of_row_ids = identified_cadets_at_event.list_of_unique_row_id_given_cadet_id(cadet_id)

    return list_of_row_ids


def load_cadets_at_event(interface: abstractInterface, event: Event) -> ListOfCadetsAtEvent:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    return cadets_at_event_data.get_list_of_cadets_at_event(event)


def load_identified_cadets_at_event(interface: abstractInterface, event: Event) -> ListOfIdentifiedCadetsAtEvent:
    cadets_at_event_data = CadetsAtEventData(interface.data)
    return cadets_at_event_data.get_list_of_identified_cadets_at_event(event)


