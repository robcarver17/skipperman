from app.backend.cadets import get_list_of_cadets
from app.data_access.data import data
from app.objects.cadets import Cadet
from app.objects.constants import arg_not_passed
from app.objects.volunteers import ListOfVolunteers, Volunteer

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


def get_volunteer_from_list_of_volunteers(volunteer_selected: str) -> Volunteer:
    list_of_volunteers = get_list_of_volunteers()
    list_of_volunteers_as_str = get_list_of_volunteers_as_str(list_of_volunteers=list_of_volunteers)

    idx = list_of_volunteers_as_str.index(volunteer_selected)
    return list_of_volunteers[idx]

def get_volunteer_from_volunteer_id(volunteer_id: str) -> Volunteer:
    list_of_volunteers = get_list_of_volunteers()
    return list_of_volunteers.object_with_id(volunteer_id)


def get_dict_of_existing_skills(volunteer: Volunteer)-> dict:
    all_skills = data.data_list_of_volunteer_skills.read()
    return all_skills.dict_of_skills_for_volunteer_id(volunteer_id=volunteer.id)


def get_connected_cadets(volunteer: Volunteer) -> list:
    existing_connections = data.data_list_of_cadet_volunteer_associations.read()
    list_of_cadets = get_list_of_cadets()

    connected_ids = existing_connections.list_of_connections_for_volunteer(volunteer.id)
    connected_cadets = [list_of_cadets.object_with_id(id) for id in connected_ids]
    return connected_cadets


def list_of_similar_volunteers(volunteer: Volunteer) -> list:
    existing_volunteers = data.data_list_of_volunteers.read()
    similar_volunteers = existing_volunteers.similar_volunteers(
        volunteer=volunteer
    )

    return similar_volunteers


def add_new_verified_volunteer(volunteer: Volunteer):
    data.data_list_of_volunteers.add(volunteer)


def delete_a_volunteer(volunteer):
    all_volunteers= data.data_list_of_volunteers.read()
    all_volunteers.pop_with_id(volunteer.id)
    data.data_list_of_volunteers.write(all_volunteers)


def warning_for_similar_volunteers(volunteer: Volunteer) -> str:
    similar_volunteers = list_of_similar_volunteers(volunteer)

    if len(similar_volunteers) > 0:
        similar_volunteers_str = ", ".join(
            [str(other_volunteer) for other_volunteer in similar_volunteers]
        )
        ## Some similar volunteers, let's see if it's a match
        return "Following existing volunteers look awfully similar:\n %s" % similar_volunteers_str
    else:
        return ""


def verify_volunteer_and_warn(volunteer: Volunteer) -> str:
    warn_text = ""
    if len(volunteer.surname) < 4:
        warn_text += "Surname seems too short. "
    if len(volunteer.first_name) < 4:
        warn_text += "First name seems too short. "
    warn_text += warning_for_similar_volunteers(volunteer)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text

def is_cadet_already_connected_to_volunteer_in_volunteer_list(cadet: Cadet, volunteer: Volunteer) -> bool:
    existing_connections = data.data_list_of_cadet_volunteer_associations.read()
    return cadet.id in existing_connections.list_of_connections_for_volunteer(volunteer.id)


def delete_connection_in_data(cadet: Cadet, volunteer: Volunteer):
    existing_connections = data.data_list_of_cadet_volunteer_associations.read()
    existing_connections.delete(cadet_id=cadet.id, volunteer_id=volunteer.id)
    data.data_list_of_cadet_volunteer_associations.write(existing_connections)


def add_volunteer_connection_to_cadet_in_master_list_of_volunteers(cadet: Cadet, volunteer: Volunteer):
    existing_connections = data.data_list_of_cadet_volunteer_associations.read()
    existing_connections.add(cadet_id=cadet.id, volunteer_id=volunteer.id)
    data.data_list_of_cadet_volunteer_associations.write(existing_connections)


def save_skills_for_volunteer(volunteer: Volunteer, dict_of_skills: dict):
    all_skills = data.data_list_of_volunteer_skills.read()
    all_skills.replace_skills_for_volunteer_with_new_skills_dict(volunteer_id=volunteer.id, dict_of_skills=dict_of_skills)
    data.data_list_of_volunteer_skills.write(all_skills)


def save_volunteer_details(volunteer: Volunteer):
    list_of_volunteers = data.data_list_of_volunteers.read()
    index = list_of_volunteers.index_of_id(volunteer.id)
    list_of_volunteers[index] = volunteer
    data.data_list_of_volunteers.write(list_of_volunteers)
