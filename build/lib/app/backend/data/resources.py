from typing import List

from app.objects.constants import missing_data

from app.data_access.storage_layer.api import DataApi

from app.objects.dinghies import ListOfDinghies
from app.objects.events import Event
from app.objects.patrol_boats import ListOfPatrolBoats, ListOfVolunteersAtEventWithPatrolBoats, PatrolBoat, VolunteerAtEventWithPatrolBoat
from app.objects.club_dinghies import ListOfClubDinghies, ListOfCadetAtEventWithClubDinghies, ClubDinghy, CadetAtEventWithClubDinghy

from app.data_access.data import data
from app.objects.utils import in_x_not_in_y

class ClubDinghies():
    def __init__(self, data_api: DataApi):
        self.data_api = data_api

    def list_of_club_dinghies_bool_for_list_of_cadet_ids(self, list_of_cadet_ids: List[str]) ->List[bool]:
        list_of_cadets_at_event_with_club_dinghies = self.data_api.list_of_cadets_at_event_with_club_dinghies
        index_of_cadet_ids_in_list = [list_of_cadets_at_event_with_club_dinghies.dinghy_for_cadet_id(cadet_id=cadet_id,
                                                                                                     default=None) for cadet_id in list_of_cadet_ids]
        list_of_true_false = [ cadet_at_event_with_dinghy is not None for cadet_at_event_with_dinghy in index_of_cadet_ids_in_list]
        return list_of_true_false

def from_patrol_boat_name_to_boat(boat_name: str) -> PatrolBoat:
    list_of_patrol_boats = load_list_of_patrol_boats()
    return list_of_patrol_boats.boat_given_name(boat_name)

def load_list_of_patrol_boats() -> ListOfPatrolBoats:
    list_of_patrol_boats = data.data_list_of_patrol_boats.read()

    return list_of_patrol_boats

def save_list_of_patrol_boats(list_of_boats: ListOfPatrolBoats):
    data.data_list_of_patrol_boats.write(list_of_boats=list_of_boats)

def add_new_patrol_boat_given_string_and_return_list(new_boat_name: str) -> ListOfPatrolBoats:
    list_of_patrol_boats = load_list_of_patrol_boats()
    list_of_patrol_boats.add(new_boat_name)
    save_list_of_patrol_boats(list_of_patrol_boats)

    return list_of_patrol_boats

def delete_patrol_boat_given_string_and_return_list(boat_name: str) -> ListOfPatrolBoats:
    list_of_patrol_boats = load_list_of_patrol_boats()
    list_of_patrol_boats.delete_given_name(boat_name)
    save_list_of_patrol_boats(list_of_patrol_boats)

    return list_of_patrol_boats

def modify_patrol_boat_given_string_and_return_list(existing_value_as_str:str, new_value_as_str:str) -> ListOfPatrolBoats:
    list_of_patrol_boats = load_list_of_patrol_boats()
    list_of_patrol_boats.delete_given_name(existing_value_as_str)
    list_of_patrol_boats.add(new_value_as_str)
    save_list_of_patrol_boats(list_of_patrol_boats)

    return list_of_patrol_boats


def load_list_of_club_dinghies() -> ListOfClubDinghies:
    list_of_boats = data.data_List_of_club_dinghies.read()

    return list_of_boats


def save_list_of_club_dinghies(list_of_boats: ListOfClubDinghies):
    data.data_List_of_club_dinghies.write(list_of_boats)


def load_list_of_cadets_at_event_with_club_dinghies(event: Event) -> ListOfCadetAtEventWithClubDinghies:
    cadets_with_dinghies = data.data_list_of_cadets_at_event_with_club_dinghies.read(event_id=event.id)

    return cadets_with_dinghies

def save_list_of_cadets_at_event_with_club_dinghies(event: Event, cadets_with_club_dinghies_at_event:ListOfCadetAtEventWithClubDinghies):
    data.data_list_of_cadets_at_event_with_club_dinghies.write(event_id=event.id, people_and_boats=cadets_with_club_dinghies_at_event)



def add_new_club_dinghy_given_string_and_return_list(new_boat_name: str) -> ListOfClubDinghies:
    list_of_boats = load_list_of_club_dinghies()
    list_of_boats.add(new_boat_name)
    save_list_of_club_dinghies(list_of_boats)

    return list_of_boats

def delete_club_dinghy_given_string_and_return_list(boat_name: str) -> ListOfClubDinghies:
    list_of_boats = load_list_of_club_dinghies()
    list_of_boats.delete_given_name(boat_name)
    save_list_of_club_dinghies(list_of_boats)

    return list_of_boats

def modify_club_dinghy_given_string_and_return_list(existing_value_as_str:str, new_value_as_str:str) -> ListOfClubDinghies:
    list_of_boats = load_list_of_club_dinghies()
    list_of_boats.delete_given_name(existing_value_as_str)
    list_of_boats.add(new_value_as_str)
    save_list_of_club_dinghies(list_of_boats)

    return list_of_boats


def get_list_of_boats_excluding_boats_already_at_event(event: Event) -> ListOfPatrolBoats:
    list_of_all_patrol_boats = load_list_of_patrol_boats()
    list_of_patrol_boats_at_event = load_list_of_patrol_boats_at_event(event)
    boats_not_already_at_event = in_x_not_in_y(x=list_of_all_patrol_boats, y=list_of_patrol_boats_at_event)
    sorted_boats_not_already_at_event = [boat for boat in list_of_all_patrol_boats if boat in boats_not_already_at_event]

    return ListOfPatrolBoats(sorted_boats_not_already_at_event)

def load_list_of_patrol_boats_at_event(event: Event) -> ListOfPatrolBoats:
    volunteers_with_boats_at_event = load_list_of_voluteers_at_event_with_patrol_boats(event)
    list_of_all_patrol_boats = load_list_of_patrol_boats()

    return volunteers_with_boats_at_event.list_of_unique_boats_at_event_including_unallocated(list_of_patrol_boats=list_of_all_patrol_boats)

def load_list_of_voluteers_at_event_with_patrol_boats(event: Event) -> ListOfVolunteersAtEventWithPatrolBoats:
    volunteers_with_boats_at_event = data.data_list_of_volunteers_at_event_with_patrol_boats.read(event_id=event.id)

    return volunteers_with_boats_at_event

def save_list_of_voluteers_at_event_with_patrol_boats(event: Event, volunteers_with_boats_at_event:ListOfVolunteersAtEventWithPatrolBoats):
    data.data_list_of_volunteers_at_event_with_patrol_boats.write(event_id=event.id,
                                                                  people_and_boats=volunteers_with_boats_at_event)


def load_list_of_boat_classes() -> ListOfDinghies:
    list_of_boats = data.data_list_of_dinghies.read()

    return list_of_boats


def save_list_of_boat_classes(list_of_boats: ListOfDinghies):
    data.data_list_of_dinghies.write(list_of_boats)


def add_new_boat_class_given_string_and_return_list(new_boat_name: str) -> ListOfDinghies:
    list_of_boats = load_list_of_boat_classes()
    list_of_boats.add(new_boat_name)
    save_list_of_boat_classes(list_of_boats)

    return list_of_boats


def delete_boat_class_given_string_and_return_list(boat_name: str) -> ListOfDinghies:
    list_of_boats = load_list_of_boat_classes()
    list_of_boats.delete_given_name(boat_name)
    save_list_of_boat_classes(list_of_boats)

    return list_of_boats


def modify_boat_class_given_string_and_return_list(existing_value_as_str:str, new_value_as_str:str) -> ListOfDinghies:
    list_of_boats = load_list_of_boat_classes()
    list_of_boats.delete_given_name(existing_value_as_str)
    list_of_boats.add(new_value_as_str)
    save_list_of_boat_classes(list_of_boats)

    return list_of_boats
