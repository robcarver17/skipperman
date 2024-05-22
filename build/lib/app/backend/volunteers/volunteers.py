from typing import List

from app.objects.cadets import ListOfCadets, Cadet

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.cadets import  cadet_from_id
from app.backend.data.volunteers import     VolunteerData
from app.data_access.configuration.configuration import VOLUNTEERS_SKILL_FOR_PB2
from app.objects.constants import arg_not_passed
from app.objects.volunteers import Volunteer, ListOfVolunteerSkills, ListOfVolunteers

def get_volunteer_from_list_of_volunteers_given_volunteer_name(interface: abstractInterface, volunteer_name: str) -> Volunteer:
    volunteer_data = VolunteerData(interface.data)
    return volunteer_data.get_volunteer_from_list_of_volunteers_given_name(volunteer_name=volunteer_name)


def get_dict_of_existing_skills(interface: abstractInterface, volunteer: Volunteer)-> dict:
    volunteer_data = VolunteerData(interface.data)
    return volunteer_data.get_dict_of_existing_skills(volunteer)


def get_connected_cadets(interface: abstractInterface, volunteer: Volunteer) -> ListOfCadets:
    volunteer_data = VolunteerData(interface.data)

    return volunteer_data.get_connected_cadets(volunteer)

def list_of_similar_volunteers(interface: abstractInterface, volunteer: Volunteer) -> list:
    volunteer_data = VolunteerData(interface.data)
    similar_volunteers = volunteer_data.list_of_similar_volunteers(volunteer)

    return similar_volunteers


def warning_for_similar_volunteers(interface: abstractInterface, volunteer: Volunteer) -> str:
    similar_volunteers = list_of_similar_volunteers(interface=interface, volunteer=volunteer)

    if len(similar_volunteers) > 0:
        similar_volunteers_str = ", ".join(
            [str(other_volunteer) for other_volunteer in similar_volunteers]
        )
        ## Some similar volunteers, let's see if it's a match
        return "Following existing volunteers look awfully similar:\n %s" % similar_volunteers_str
    else:
        return ""



def verify_volunteer_and_warn(interface: abstractInterface, volunteer: Volunteer) -> str:
    warn_text = ""
    if len(volunteer.surname) < 4:
        warn_text += "Surname seems too short. "
    if len(volunteer.first_name) < 4:
        warn_text += "First name seems too short. "
    warn_text += warning_for_similar_volunteers(interface=interface, volunteer=volunteer)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text


def are_all_cadet_ids_in_list_already_connection_to_volunteer(interface:abstractInterface, volunteer: Volunteer, list_of_cadet_ids: List[str]) -> bool:
    list_of_already_connected = [is_cadet_already_connected_to_volunteer_in_volunteer_list(interface=interface, volunteer=volunteer, cadet_id=cadet_id) for cadet_id in list_of_cadet_ids]

    return all(list_of_already_connected)


def is_cadet_already_connected_to_volunteer_in_volunteer_list(interface:abstractInterface, cadet_id: str, volunteer: Volunteer) -> bool:
    volunteer_data = VolunteerData(interface.data)
    return volunteer_data.is_cadet_already_connected_to_volunteer_in_volunteer_list(cadet_id=cadet_id, volunteer=volunteer)



def add_list_of_cadet_connections_to_volunteer(interface: abstractInterface,
                                                           volunteer_id: str,
                                                           list_of_connected_cadet_ids: List[str]):

    volunteer_data = VolunteerData(interface.data)

    volunteer = get_volunteer_from_id(interface=interface, volunteer_id=volunteer_id)
    for cadet_id in list_of_connected_cadet_ids:
        cadet = cadet_from_id(interface=interface, cadet_id=cadet_id)
        volunteer_data.add_volunteer_connection_to_cadet_in_master_list_of_volunteers(cadet=cadet, volunteer=volunteer)



def get_volunteer_name_from_id(interface: abstractInterface, volunteer_id: str) -> str:
    volunteer = get_volunteer_from_id(interface=interface, volunteer_id=volunteer_id)
    return volunteer.name


def get_volunteer_from_id(interface: abstractInterface, volunteer_id: str) -> Volunteer:
    volunteer_data= VolunteerData(interface.data)
    list_of_volunteers = volunteer_data.get_list_of_volunteers()
    return list_of_volunteers.object_with_id(volunteer_id)


def boat_related_skill_str(interface: abstractInterface, volunteer_id: str) -> str:
    if boat_related_skill_for_volunteer(interface=interface, volunteer_id=volunteer_id):
        return VOLUNTEERS_SKILL_FOR_PB2
    else:
        return ""

def boat_related_skill_for_volunteer(interface: abstractInterface, volunteer_id: str) -> bool:
    volunteer_data = VolunteerData(interface.data)
    return volunteer_data.boat_related_skill_for_volunteer(volunteer_id)

def add_boat_related_skill_for_volunteer(interface: abstractInterface, volunteer_id: str):
    volunteer_data = VolunteerData(interface.data)
    volunteer_data.add_boat_related_skill_for_volunteer(volunteer_id)

def remove_boat_related_skill_for_volunteer(interface: abstractInterface, volunteer_id: str):
    volunteer_data = VolunteerData(interface.data)
    volunteer_data.remove_boat_related_skill_for_volunteer(volunteer_id)


def add_new_verified_volunteer(interface: abstractInterface, volunteer: Volunteer):
    volunteer_data= VolunteerData(interface.data)
    volunteer_data.add_new_volunteer(volunteer)


def save_skills_for_volunteer(interface: abstractInterface, volunteer: Volunteer, dict_of_skills: dict):
    volunteer_data = VolunteerData(interface.data)
    volunteer_data.save_skills_for_volunteer(volunteer=volunteer, dict_of_skills=dict_of_skills)


def load_list_of_volunteer_skills(interface: abstractInterface)-> ListOfVolunteerSkills:
    volunteer_data = VolunteerData(interface.data)
    return volunteer_data.get_list_of_volunteer_skills()


def get_sorted_list_of_volunteers(interface: abstractInterface, sort_by: str = arg_not_passed) -> ListOfVolunteers:
    volunteer_data = VolunteerData(interface.data)
    return volunteer_data.get_sorted_list_of_volunteers(sort_by)


def load_all_volunteers(interface:abstractInterface)-> ListOfVolunteers:
    volunteer_data = VolunteerData(interface.data)
    return volunteer_data.get_list_of_volunteers()


def delete_connection_in_data(interface: abstractInterface, cadet: Cadet, volunteer: Volunteer):
    volunteer_data = VolunteerData(interface.data)
    volunteer_data.delete_connection_in_data(cadet=cadet, volunteer=volunteer)


def add_volunteer_connection_to_cadet_in_master_list_of_volunteers(interface: abstractInterface, cadet: Cadet, volunteer: Volunteer):
    volunteer_data = VolunteerData(interface.data)
    volunteer_data.add_volunteer_connection_to_cadet_in_master_list_of_volunteers(cadet=cadet, volunteer=volunteer)


def update_existing_volunteer(interface: abstractInterface, volunteer: Volunteer):
    volunteer_data = VolunteerData(interface.data)
    volunteer_data.update_existing_volunteer(volunteer)
