from app.logic.cadets.backend import get_list_of_cadets
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.data_access.data import data
from app.objects.constants import arg_not_passed
from app.objects.volunteers import ListOfVolunteers, Volunteer

from app.logic.volunteers.constants import *
SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"


def get_list_of_volunteers(sort_by: str = arg_not_passed) -> ListOfVolunteers:
    master_list = data.data_list_of_volunteers.read()
    if sort_by is arg_not_passed:
        return master_list
    if sort_by == SORT_BY_SURNAME:
        return master_list.sort_by_surname()
    elif sort_by == SORT_BY_FIRSTNAME:
        return master_list.sort_by_firstname()
    else:
        return master_list

def get_list_of_volunteers_as_str(list_of_volunteers = arg_not_passed) -> list:
    if list_of_volunteers is arg_not_passed:
        list_of_volunteers = get_list_of_volunteers()
    return [str(volunteer) for volunteer in list_of_volunteers]


def update_state_for_specific_volunteer(interface: abstractInterface, volunteer_selected: str):
    interface.set_persistent_value(key=VOLUNTEER, value=volunteer_selected)


def get_volunteer_from_state(interface: abstractInterface) -> Volunteer:
    volunteer_selected = get_volunteer_selected_from_state(interface)

    return get_volunteer_from_list_of_volunteers(volunteer_selected)


def get_volunteer_selected_from_state(interface: abstractInterface) -> str:
    return interface.get_persistent_value(VOLUNTEER)


def get_volunteer_from_list_of_volunteers(volunteer_selected: str) -> Volunteer:
    list_of_volunteers = get_list_of_volunteers()
    list_of_volunteers_as_str = get_list_of_volunteers_as_str(list_of_volunteers=list_of_volunteers)

    idx = list_of_volunteers_as_str.index(volunteer_selected)
    return list_of_volunteers[idx]


def get_dict_of_existing_skills(volunteer: Volunteer)-> dict:
    all_skills = data.data_list_of_volunteer_skills.read()
    return all_skills.dict_of_skills_for_volunteer_id(volunteer_id=volunteer.id)


def get_connected_cadets(volunteer: Volunteer) -> list:
    existing_connections = data.data_list_of_cadet_volunteer_associations.read()
    list_of_cadets = get_list_of_cadets()

    connected_ids = existing_connections.list_of_connections_for_volunteer(volunteer.id)
    connected_cadets = [list_of_cadets.object_with_id(id) for id in connected_ids]
    return connected_cadets
