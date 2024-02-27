from typing import List

from app.objects.events import Event
from app.objects.patrol_boats import ListOfPatrolBoats, ListOfVolunteersAtEventWithPatrolBoats, PatrolBoat, VolunteerAtEventWithPatrolBoat
from app.objects.club_dinghies import ListOfClubDinghies, ListOfCadetAtEventWithClubDinghies, ClubDinghy, CadetAtEventWithClubDinghy

from app.data_access.data import data
from app.objects.utils import in_x_not_in_y

def get_list_of_patrol_boats() -> ListOfPatrolBoats:
    list_of_patrol_boats = data.data_list_of_patrol_boats.read()

    return list_of_patrol_boats

def save_list_of_patrol_boats(list_of_boats: ListOfPatrolBoats):
    data.data_list_of_patrol_boats.write(list_of_boats=list_of_boats)

def add_new_patrol_boat_given_string_and_return_list(new_boat_name: str) -> ListOfPatrolBoats:
    list_of_patrol_boats = get_list_of_patrol_boats()
    list_of_patrol_boats.add(new_boat_name)
    save_list_of_patrol_boats(list_of_patrol_boats)

    return list_of_patrol_boats

def delete_patrol_boat_given_string_and_return_list(boat_name: str) -> ListOfPatrolBoats:
    list_of_patrol_boats = get_list_of_patrol_boats()
    list_of_patrol_boats.delete_given_name(boat_name)
    save_list_of_patrol_boats(list_of_patrol_boats)

    return list_of_patrol_boats

def modify_patrol_boat_given_string_and_return_list(existing_value_as_str:str, new_value_as_str:str) -> ListOfPatrolBoats:
    list_of_patrol_boats = get_list_of_patrol_boats()
    list_of_patrol_boats.delete_given_name(existing_value_as_str)
    list_of_patrol_boats.add(new_value_as_str)
    save_list_of_patrol_boats(list_of_patrol_boats)

    return list_of_patrol_boats


def get_list_of_club_dinghies() -> ListOfClubDinghies:
    list_of_boats = data.data_List_of_club_dinghies.read()

    return list_of_boats

def save_list_of_club_dinghies(list_of_boats: ListOfClubDinghies):
    data.data_List_of_club_dinghies.write(list_of_boats)

def add_new_club_dinghy_given_string_and_return_list(new_boat_name: str) -> ListOfClubDinghies:
    list_of_boats = get_list_of_club_dinghies()
    list_of_boats.add(new_boat_name)
    save_list_of_club_dinghies(list_of_boats)

    return list_of_boats

def delete_club_dinghy_given_string_and_return_list(boat_name: str) -> ListOfClubDinghies:
    list_of_boats = get_list_of_club_dinghies()
    list_of_boats.delete_given_name(boat_name)
    save_list_of_club_dinghies(list_of_boats)

    return list_of_boats

def modify_club_dinghy_given_string_and_return_list(existing_value_as_str:str, new_value_as_str:str) -> ListOfClubDinghies:
    list_of_boats = get_list_of_club_dinghies()
    list_of_boats.delete_given_name(existing_value_as_str)
    list_of_boats.add(new_value_as_str)
    save_list_of_club_dinghies(list_of_boats)

    return list_of_boats


def get_list_of_boats_excluding_boats_already_at_event(event: Event) -> ListOfPatrolBoats:
    list_of_all_patrol_boats = get_list_of_patrol_boats()
    list_of_patrol_boats_at_event = get_list_of_boats_at_event(event)

    return ListOfPatrolBoats(in_x_not_in_y(x=list_of_all_patrol_boats, y=list_of_patrol_boats_at_event))

def get_list_of_boats_at_event(event: Event) -> ListOfPatrolBoats:
    boats_at_event = data.data_list_of_volunteers_at_event_with_patrol_boats.read(event_id=event.id)
    list_of_all_patrol_boats = get_list_of_patrol_boats()

    return boats_at_event.list_of_boats_at_event_including_unallocated(list_of_patrol_boats=list_of_all_patrol_boats)

