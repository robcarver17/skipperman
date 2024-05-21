from typing import List

from app.objects.cadet_at_event import CadetAtEvent

from app.backend.data.cadets_at_event import CadetsAtEventData

from app.objects.constants import missing_data

from app.objects.day_selectors import Day

from app.backend.data.patrol_boats import PatrolBoatsData
from app.data_access.data import DEPRECATED_data
from app.data_access.storage_layer.api import DataLayer
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.club_dinghies import ListOfCadetAtEventWithClubDinghies, ListOfClubDinghies, NO_BOAT
from app.objects.dinghies import ListOfBoatClasses, ListOfCadetAtEventWithDinghies
from app.objects.events import Event
from app.objects.patrol_boats import ListOfPatrolBoats


class DinghiesData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def remove_two_handed_partner_link_from_existing_cadet_on_day(self, event: Event, cadet_id: str, day: Day):
        list_of_cadets_at_event_with_dinghies = self.get_list_of_cadets_at_event_with_dinghies(event)
        cadet_with_boat_at_event = list_of_cadets_at_event_with_dinghies.object_with_cadet_id_on_day(cadet_id=cadet_id,
                                                                                                                              day=day)
        if not cadet_with_boat_at_event.has_partner():
            return

        partner_id = cadet_with_boat_at_event.partner_cadet_id
        partner_with_boat_at_event = list_of_cadets_at_event_with_dinghies.object_with_cadet_id_on_day(cadet_id=partner_id,
                                                                                                                    day=day)
        partner_with_boat_at_event.clear_partner()
        cadet_with_boat_at_event.clear_partner()

        self.save_list_of_cadets_at_event_with_dinghies(list_of_cadets_at_event_with_dinghies=list_of_cadets_at_event_with_dinghies,
                                                        event=event)

    def remove_club_boat_allocation_for_cadet_on_day(self, event: Event,
                                                     cadet_id: str,
                                                     day: Day):

        cadets_with_club_dinghies_at_event = self.get_list_of_cadets_at_event_with_club_dinghies(event)
        cadets_with_club_dinghies_at_event.delete_allocation_for_cadet_on_day(cadet_id=cadet_id, day=day)
        self.save_list_of_cadets_at_event_with_club_dinghies(
            list_of_cadets_at_event_with_club_dinghies=cadets_with_club_dinghies_at_event,
            event=event)

    def remove_boat_and_partner_for_cadet_at_event(self, event: Event,
                                                   cadet_id: str):

        for day in event.weekdays_in_event():
            self.remove_boat_and_partner_for_cadet_at_event_on_day(event=event, cadet_id=cadet_id, day=day)

    def remove_boat_and_partner_for_cadet_at_event_on_day(self, event: Event,
                                                   cadet_id: str, day: Day):

        list_of_cadets_at_event_with_dinghies = self.get_list_of_cadets_at_event_with_dinghies(event)
        list_of_cadets_at_event_with_dinghies.clear_boat_details_from_existing_cadet_id(day=day, cadet_id=cadet_id)
        self.save_list_of_cadets_at_event_with_dinghies(list_of_cadets_at_event_with_dinghies=list_of_cadets_at_event_with_dinghies,
                                                        event=event)


    def update_club_boat_allocation_for_cadet_at_event_on_day_if_cadet_available(self, boat_name: str,
                                                                                 cadet_id: str, event: Event, day: Day):

        cadet_at_event = self.cadet_at_event_or_missing_data(event, cadet_id=cadet_id)
        if cadet_at_event is missing_data:
            return
        if not cadet_at_event.availability.available_on_day(day):
            return
        if not cadet_at_event.is_active():
            return

        cadets_with_club_dinghies_at_event = self.get_list_of_cadets_at_event_with_club_dinghies(event)
        if boat_name == NO_BOAT:
            cadets_with_club_dinghies_at_event.delete_allocation_for_cadet_on_day(cadet_id=cadet_id, day=day)
        else:
            club_dinghies = self.get_list_of_club_dinghies()
            boat_id = club_dinghies.id_given_name(boat_name)
            cadets_with_club_dinghies_at_event.update_allocation_for_cadet_on_day(cadet_id=cadet_id,
                                                                                  club_dinghy_id=boat_id, day=day)

        self.save_list_of_cadets_at_event_with_club_dinghies(
            list_of_cadets_at_event_with_club_dinghies=cadets_with_club_dinghies_at_event,
            event=event)

    def update_boat_info_for_updated_cadets_at_event_where_cadets_available(self, event: Event,
                                                                            list_of_updated_cadets: ListOfCadetAtEventWithDinghies):

        list_of_cadets_at_event_with_dinghies = self.get_list_of_cadets_at_event_with_dinghies(event)
        for cadet_at_event_with_dinghy in list_of_updated_cadets:
            cadet_at_event = self.cadet_at_event_or_missing_data(event, cadet_id=cadet_at_event_with_dinghy.cadet_id)
            if cadet_at_event is missing_data:
                continue
            if not cadet_at_event.availability.available_on_day(cadet_at_event_with_dinghy.day):
                continue
            if not cadet_at_event.is_active():
                continue
            list_of_cadets_at_event_with_dinghies.update_boat_info_for_cadet_and_partner_at_event_on_day(
                cadet_at_event_with_dinghy
            )

        self.save_list_of_cadets_at_event_with_dinghies(
            list_of_cadets_at_event_with_dinghies=list_of_cadets_at_event_with_dinghies, event=event)

    def sorted_list_of_names_of_dinghies_at_event(self, event: Event) -> List[str]:
        all_boat_classes = self.get_list_of_boat_classes()
        list_of_boat_class_ids = self.unique_sorted_list_of_boat_class_ids_at_event(event)

        dinghy_names = [all_boat_classes.name_given_id(id) for id in list_of_boat_class_ids]

        return dinghy_names

    def unique_sorted_list_of_boat_class_ids_at_event(self, event: Event) -> List[str]:
        all_boat_classes = self.get_list_of_boat_classes()
        cadets_with_dinghies_at_event = self.get_list_of_cadets_at_event_with_dinghies(event)
        list_of_boat_class_ids = cadets_with_dinghies_at_event.unique_sorted_list_of_boat_class_ids(all_boat_classes)

        return list_of_boat_class_ids

    def sorted_list_of_names_of_allocated_club_dinghies(self, event: Event) -> List[str]:
        list_of_dinghy_ids = self.unique_sorted_list_of_allocated_club_dinghy_ids_allocated_at_event(event)
        all_club_dinghies = self.get_list_of_club_dinghies()
        dinghy_names = [all_club_dinghies.name_given_id(id) for id in list_of_dinghy_ids]

        return dinghy_names

    def unique_sorted_list_of_allocated_club_dinghy_ids_allocated_at_event(self, event: Event) -> List[str]:
        cadets_with_club_dinghies_at_event = self.get_list_of_cadets_at_event_with_club_dinghies(event)
        all_club_dinghies = self.get_list_of_club_dinghies()
        list_of_dinghy_ids = cadets_with_club_dinghies_at_event.unique_sorted_list_of_dinghy_ids(all_club_dinghies)

        return list_of_dinghy_ids

    def list_of_club_dinghies_bool_for_list_of_cadet_ids(self, event: Event, list_of_cadet_ids: List[str]) -> List[
        bool]:
        list_of_cadets_at_event_with_club_dinghies = self.get_list_of_cadets_at_event_with_club_dinghies(event)
        list_of_true_false = [
            list_of_cadets_at_event_with_club_dinghies.is_a_club_dinghy_allocated_for_cadet_id_on_any_day(cadet_id=cadet_id) for cadet_id in
            list_of_cadet_ids]
        return list_of_true_false

    def cadet_at_event_or_missing_data(self, event: Event, cadet_id: str) -> CadetAtEvent:
        return self.cadets_at_event_data.cadet_at_event_or_missing_data(event=event, cadet_id=cadet_id)

    def get_list_of_cadets_at_event_with_club_dinghies(self, event: Event) -> ListOfCadetAtEventWithClubDinghies:
        return self.data_api.get_list_of_cadets_at_event_with_club_dinghies(event)

    def save_list_of_cadets_at_event_with_club_dinghies(self, event: Event,
                                                        list_of_cadets_at_event_with_club_dinghies: ListOfCadetAtEventWithClubDinghies):
        self.data_api.save_list_of_cadets_at_event_with_club_dinghies(event=event,
                                                                      list_of_cadets_at_event_with_club_dinghies=list_of_cadets_at_event_with_club_dinghies)

    def get_list_of_club_dinghies(self):
        return self.data_api.get_list_of_club_dinghies()

    def save_list_of_club_dinghies(self, list_of_club_dinghies:  ListOfClubDinghies):
        self.data_api.save_list_of_club_dinghies(list_of_club_dinghies)

    def get_list_of_cadets_at_event_with_dinghies(self, event: Event) -> ListOfCadetAtEventWithDinghies:
        return self.data_api.get_list_of_cadets_at_event_with_dinghies(event)

    def save_list_of_cadets_at_event_with_dinghies(self, event: Event,
                                                   list_of_cadets_at_event_with_dinghies: ListOfCadetAtEventWithDinghies):
        self.data_api.save_list_of_cadets_at_event_with_dinghies(
            list_of_cadets_at_event_with_dinghies=list_of_cadets_at_event_with_dinghies, event=event
            )

    def get_list_of_boat_classes(self) -> ListOfBoatClasses:
        return self.data_api.get_list_of_boat_classes()


    def save_list_of_boat_classes(self, list_of_boat_classes: ListOfBoatClasses):
        self.data_api.save_list_of_boat_classes(list_of_boat_classes)

    @property
    def cadets_at_event_data(self) -> CadetsAtEventData:
        return CadetsAtEventData(data_api=self.data_api)


def DEPRECATE_load_list_of_club_dinghies() -> ListOfClubDinghies:
    list_of_boats = DEPRECATED_data.data_List_of_club_dinghies.read()

    return list_of_boats



def DEPRECATE_load_list_of_cadets_at_event_with_club_dinghies(event: Event) -> ListOfCadetAtEventWithClubDinghies:
    cadets_with_dinghies = DEPRECATED_data.data_list_of_cadets_at_event_with_club_dinghies.read(event_id=event.id)

    return cadets_with_dinghies


def load_list_of_cadets_at_event_with_club_dinghies(interface: abstractInterface, event: Event) -> ListOfCadetAtEventWithClubDinghies:
    dinghies_data = DinghiesData(interface.data)
    cadets_with_dinghies = dinghies_data.get_list_of_cadets_at_event_with_club_dinghies(event)

    return cadets_with_dinghies




def get_sorted_list_of_boats_excluding_boats_already_at_event(interface: abstractInterface,
                                                              event: Event) -> ListOfPatrolBoats:
    patrol_boat_data = PatrolBoatsData(interface.data)
    return patrol_boat_data.get_sorted_list_of_boats_excluding_boats_already_at_event(event)


def load_list_of_patrol_boats_at_event(interface: abstractInterface, event: Event) -> ListOfPatrolBoats:
    patrol_boat_data = PatrolBoatsData(interface.data)
    return patrol_boat_data.list_of_unique_boats_at_event_including_unallocated(event)


