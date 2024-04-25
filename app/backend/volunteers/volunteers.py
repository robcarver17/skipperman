from typing import List

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.cadets import DEPRECATE_get_sorted_list_of_cadets,  cadet_from_id
from app.backend.data.volunteers import DEPRECATED_get_sorted_list_of_volunteers, load_list_of_volunteer_skills, \
    save_list_of_volunteer_skills, \
    DEPRECATE_get_list_of_cadet_volunteer_associations, \
    DEPRECATE_load_all_volunteers, VolunteerData
from app.data_access.configuration.configuration import VOLUNTEERS_SKILL_FOR_PB2
from app.objects.constants import arg_not_passed
from app.objects.volunteers import Volunteer


def get_list_of_volunteers_as_str(list_of_volunteers = arg_not_passed) -> list:
    if list_of_volunteers is arg_not_passed:
        list_of_volunteers = DEPRECATE_load_all_volunteers()
    return [str(volunteer) for volunteer in list_of_volunteers]


def get_volunteer_from_list_of_volunteers(volunteer_selected: str) -> Volunteer:
    list_of_volunteers = DEPRECATE_load_all_volunteers()
    list_of_volunteers_as_str = get_list_of_volunteers_as_str(list_of_volunteers=list_of_volunteers)

    idx = list_of_volunteers_as_str.index(volunteer_selected)
    return list_of_volunteers[idx]



def get_dict_of_existing_skills(volunteer: Volunteer)-> dict:
    all_skills = load_list_of_volunteer_skills()
    return all_skills.dict_of_skills_for_volunteer_id(volunteer_id=volunteer.id)


def get_connected_cadets(volunteer: Volunteer) -> list:
    existing_connections = DEPRECATE_get_list_of_cadet_volunteer_associations()
    list_of_cadets = DEPRECATE_get_sorted_list_of_cadets()

    connected_ids = existing_connections.list_of_connections_for_volunteer(volunteer.id)
    connected_cadets = [list_of_cadets.object_with_id(id) for id in connected_ids]
    return connected_cadets


def DEPRECATE_list_of_similar_volunteers(volunteer: Volunteer) -> list:
    existing_volunteers = DEPRECATED_get_sorted_list_of_volunteers()
    similar_volunteers = existing_volunteers.similar_volunteers(
        volunteer=volunteer
    )

    return similar_volunteers

def list_of_similar_volunteers(interface: abstractInterface, volunteer: Volunteer) -> list:
    volunteer_data = VolunteerData(interface.data)
    similar_volunteers = volunteer_data.list_of_similar_volunteers(volunteer)

    return similar_volunteers


def DEPRECATE_warning_for_similar_volunteers(volunteer: Volunteer) -> str:
    similar_volunteers = DEPRECATE_list_of_similar_volunteers(volunteer)

    if len(similar_volunteers) > 0:
        similar_volunteers_str = ", ".join(
            [str(other_volunteer) for other_volunteer in similar_volunteers]
        )
        ## Some similar volunteers, let's see if it's a match
        return "Following existing volunteers look awfully similar:\n %s" % similar_volunteers_str
    else:
        return ""

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


def DEPRECATE_verify_volunteer_and_warn(volunteer: Volunteer) -> str:
    warn_text = ""
    if len(volunteer.surname) < 4:
        warn_text += "Surname seems too short. "
    if len(volunteer.first_name) < 4:
        warn_text += "First name seems too short. "
    warn_text += DEPRECATE_warning_for_similar_volunteers(volunteer)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text

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


def DEPRECATED_get_volunteer_from_id(volunteer_id: str) -> Volunteer:
    list_of_volunteers = DEPRECATED_get_sorted_list_of_volunteers()
    return list_of_volunteers.object_with_id(volunteer_id)


from app.backend.data.volunteers import get_sorted_list_of_volunteers

def get_volunteer_name_from_id(interface: abstractInterface, volunteer_id: str) -> str:
    volunteer = get_volunteer_from_id(interface=interface, volunteer_id=volunteer_id)
    return volunteer.name


def get_volunteer_from_id(interface: abstractInterface, volunteer_id: str) -> Volunteer:
    volunteer_data= VolunteerData(interface.data)
    list_of_volunteers = volunteer_data.get_list_of_volunteers()
    return list_of_volunteers.object_with_id(volunteer_id)


def DEPRECATED_get_volunteer_name_from_id(volunteer_id) -> str:
    volunteer = DEPRECATED_get_volunteer_from_id(volunteer_id)
    return volunteer.name

def boat_related_skill_str(volunteer_id: str) -> str:
    if boat_related_skill_for_volunteer(volunteer_id):
        return VOLUNTEERS_SKILL_FOR_PB2
    else:
        return ""

def boat_related_skill_for_volunteer(volunteer_id: str) -> bool:
    skills =load_list_of_volunteer_skills()
    return skills.volunteer_id_has_boat_related_skills(volunteer_id)

def add_boat_related_skill_for_volunteer(volunteer_id: str):
    skills =load_list_of_volunteer_skills()
    skills.add_boat_related_skill_for_volunteer(volunteer_id)
    save_list_of_volunteer_skills(skills)

def remove_boat_related_skill_for_volunteer(volunteer_id: str):
    skills =load_list_of_volunteer_skills()
    skills.remove_boat_related_skill_for_volunteer(volunteer_id)
    save_list_of_volunteer_skills(skills)