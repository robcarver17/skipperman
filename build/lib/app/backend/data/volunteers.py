from app.data_access.data import data
from app.objects.cadets import Cadet
from app.objects.constants import arg_not_passed
from app.objects.volunteers import ListOfVolunteerSkills, ListOfVolunteers, Volunteer, ListOfCadetVolunteerAssociations


def add_new_verified_volunteer(volunteer: Volunteer):
    data.data_list_of_volunteers.add(volunteer)


def delete_a_volunteer(volunteer):
    list_of_volunteers= load_all_volunteers()
    list_of_volunteers.pop_with_id(volunteer.id)
    save_list_of_volunteers(list_of_volunteers)



def delete_connection_in_data(cadet: Cadet, volunteer: Volunteer):
    existing_connections = data.data_list_of_cadet_volunteer_associations.read()
    existing_connections.delete(cadet_id=cadet.id, volunteer_id=volunteer.id)
    save_list_of_cadet_volunteer_associations(existing_connections)


def add_volunteer_connection_to_cadet_in_master_list_of_volunteers(cadet: Cadet, volunteer: Volunteer):
    existing_connections = get_list_of_cadet_volunteer_associations()
    existing_connections.add(cadet_id=cadet.id, volunteer_id=volunteer.id)
    save_list_of_cadet_volunteer_associations(existing_connections)


def save_skills_for_volunteer(volunteer: Volunteer, dict_of_skills: dict):
    all_skills = load_list_of_volunteer_skills()
    all_skills.replace_skills_for_volunteer_with_new_skills_dict(volunteer_id=volunteer.id, dict_of_skills=dict_of_skills)
    save_list_of_volunteer_skills(all_skills)


def update_existing_volunteer(volunteer: Volunteer):
    list_of_volunteers = get_sorted_list_of_volunteers()
    index = list_of_volunteers.index_of_id(volunteer.id)
    list_of_volunteers[index] = volunteer
    save_list_of_volunteers(list_of_volunteers)




def get_list_of_cadet_volunteer_associations() -> ListOfCadetVolunteerAssociations:
    list_of_cadet_volunteer_associations = data.data_list_of_cadet_volunteer_associations.read()

    return list_of_cadet_volunteer_associations

def save_list_of_cadet_volunteer_associations(list_of_cadet_volunteer_associations:ListOfCadetVolunteerAssociations):
    data.data_list_of_cadet_volunteer_associations.write(list_of_cadet_volunteer_associations)


def load_list_of_volunteer_skills()-> ListOfVolunteerSkills:
    skills = data.data_list_of_volunteer_skills.read()

    return skills

def save_list_of_volunteer_skills(list_of_volunteer_skills: ListOfVolunteerSkills):
    data.data_list_of_volunteer_skills.write(list_of_volunteer_skills)


SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"

def load_all_volunteers()-> ListOfVolunteers:
    return data.data_list_of_volunteers.read()


def get_sorted_list_of_volunteers(sort_by: str = arg_not_passed) -> ListOfVolunteers:
    master_list = load_all_volunteers()
    if sort_by is arg_not_passed:
        return master_list
    if sort_by == SORT_BY_SURNAME:
        return master_list.sort_by_surname()
    elif sort_by == SORT_BY_FIRSTNAME:
        return master_list.sort_by_firstname()
    else:
        return master_list

def save_list_of_volunteers(list_of_volunteers: ListOfVolunteers):
    data.data_list_of_volunteers.write(list_of_volunteers)
