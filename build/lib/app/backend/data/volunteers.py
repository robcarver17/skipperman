from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.data_access.storage_layer.api import DataLayer

from app.data_access.data import DEPRECATED_data
from app.objects.cadets import Cadet
from app.objects.constants import arg_not_passed
from app.objects.volunteers import ListOfVolunteerSkills, ListOfVolunteers, Volunteer, ListOfCadetVolunteerAssociations


class VolunteerData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def add_volunteer_connection_to_cadet_in_master_list_of_volunteers(self, cadet: Cadet,
                                                                       volunteer: Volunteer):
        existing_connections = self.get_list_of_cadet_volunteer_associations()
        existing_connections.add(cadet_id=cadet.id, volunteer_id=volunteer.id)
        self.save_list_of_cadet_volunteer_associations(existing_connections)

    def is_cadet_already_connected_to_volunteer_in_volunteer_list(self, cadet_id: str,
                                                                  volunteer: Volunteer) -> bool:
        existing_connections = self.get_list_of_cadet_volunteer_associations()
        connections_for_volunteer = existing_connections.list_of_connections_for_volunteer(volunteer.id)
        return cadet_id in connections_for_volunteer

    def add_new_volunteer(self, volunteer: Volunteer):
        list_of_volunteers = self.get_list_of_volunteers()
        list_of_volunteers.add(volunteer)
        self.save_list_of_volunteers(list_of_volunteers)

    def get_list_of_volunteers_associated_with_cadet(self, cadet_id: str) -> list:
        list_of_cadet_volunteer_associations = self.get_list_of_cadet_volunteer_associations()
        list_of_associated_ids = list_of_cadet_volunteer_associations.list_of_volunteer_ids_associated_with_cadet_id(
            cadet_id=cadet_id)
        list_of_all_volunteers = self.get_list_of_volunteers()

        list_of_volunteers_associated_with_cadet = [list_of_all_volunteers.object_with_id(volunteer_id) for volunteer_id
                                                    in list_of_associated_ids]

        return list_of_volunteers_associated_with_cadet

    def list_of_similar_volunteers(self, volunteer: Volunteer) -> list:
        list_of_volunteers = self.get_list_of_volunteers()
        return list_of_volunteers.similar_volunteers(volunteer)

    def matching_volunteer_or_missing_data(self, volunteer: Volunteer) -> Volunteer:
        list_of_volunteers = self.get_list_of_volunteers()
        return list_of_volunteers.matching_volunteer(volunteer)

    def get_list_of_volunteers(self) -> ListOfVolunteers:
        list_of_volunteers = self.data_api.get_list_of_volunteers()
        return list_of_volunteers

    def save_list_of_volunteers(self, list_of_volunteers: ListOfVolunteers):
        self.data_api.save_list_of_volunteers(list_of_volunteers)

    def get_list_of_cadet_volunteer_associations(self) -> ListOfCadetVolunteerAssociations:
        return self.data_api.get_list_of_cadet_volunteer_associations()

    def save_list_of_cadet_volunteer_associations(self, list_of_associations: ListOfCadetVolunteerAssociations):
        return self.data_api.save_list_of_cadet_volunteer_associations(list_of_associations)



def add_new_verified_volunteer(interface: abstractInterface, volunteer: Volunteer):
    volunteer_data= VolunteerData(interface.data)
    volunteer_data.add_new_volunteer(volunteer)


def delete_a_volunteer(volunteer):
    list_of_volunteers= DEPRECATE_load_all_volunteers()
    list_of_volunteers.pop_with_id(volunteer.id)
    save_list_of_volunteers(list_of_volunteers)



def delete_connection_in_data(cadet: Cadet, volunteer: Volunteer):
    existing_connections = DEPRECATED_data.data_list_of_cadet_volunteer_associations.read()
    existing_connections.delete(cadet_id=cadet.id, volunteer_id=volunteer.id)
    save_list_of_cadet_volunteer_associations(existing_connections)


def DEPRECATE_add_volunteer_connection_to_cadet_in_master_list_of_volunteers(cadet: Cadet, volunteer: Volunteer):
    existing_connections = DEPRECATE_get_list_of_cadet_volunteer_associations()
    existing_connections.add(cadet_id=cadet.id, volunteer_id=volunteer.id)
    save_list_of_cadet_volunteer_associations(existing_connections)



def save_skills_for_volunteer(volunteer: Volunteer, dict_of_skills: dict):
    all_skills = load_list_of_volunteer_skills()
    all_skills.replace_skills_for_volunteer_with_new_skills_dict(volunteer_id=volunteer.id, dict_of_skills=dict_of_skills)
    save_list_of_volunteer_skills(all_skills)


def update_existing_volunteer(volunteer: Volunteer):
    list_of_volunteers = DEPRECATED_get_sorted_list_of_volunteers()
    index = list_of_volunteers.index_of_id(volunteer.id)
    list_of_volunteers[index] = volunteer
    save_list_of_volunteers(list_of_volunteers)




def DEPRECATE_get_list_of_cadet_volunteer_associations() -> ListOfCadetVolunteerAssociations:
    list_of_cadet_volunteer_associations = DEPRECATED_data.data_list_of_cadet_volunteer_associations.read()

    return list_of_cadet_volunteer_associations

def save_list_of_cadet_volunteer_associations(list_of_cadet_volunteer_associations:ListOfCadetVolunteerAssociations):
    DEPRECATED_data.data_list_of_cadet_volunteer_associations.write(list_of_cadet_volunteer_associations)


def load_list_of_volunteer_skills()-> ListOfVolunteerSkills:
    skills = DEPRECATED_data.data_list_of_volunteer_skills.read()

    return skills

def save_list_of_volunteer_skills(list_of_volunteer_skills: ListOfVolunteerSkills):
    DEPRECATED_data.data_list_of_volunteer_skills.write(list_of_volunteer_skills)


SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"

def DEPRECATE_load_all_volunteers()-> ListOfVolunteers:
    return DEPRECATED_data.data_list_of_volunteers.read()


def DEPRECATED_get_sorted_list_of_volunteers(sort_by: str = arg_not_passed) -> ListOfVolunteers:
    master_list = DEPRECATE_load_all_volunteers()
    if sort_by is arg_not_passed:
        return master_list
    if sort_by == SORT_BY_SURNAME:
        return master_list.sort_by_surname()
    elif sort_by == SORT_BY_FIRSTNAME:
        return master_list.sort_by_firstname()
    else:
        return master_list

def get_sorted_list_of_volunteers(interface: abstractInterface, sort_by: str = arg_not_passed) -> ListOfVolunteers:
    volunteer_data = VolunteerData(interface.data)
    master_list = volunteer_data.get_list_of_volunteers()
    if sort_by is arg_not_passed:
        return master_list
    if sort_by == SORT_BY_SURNAME:
        return master_list.sort_by_surname()
    elif sort_by == SORT_BY_FIRSTNAME:
        return master_list.sort_by_firstname()
    else:
        return master_list

def load_all_volunteers(interface:abstractInterface)-> ListOfVolunteers:
    volunteer_data = VolunteerData(interface.data)
    return volunteer_data.get_list_of_volunteers()


def save_list_of_volunteers(list_of_volunteers: ListOfVolunteers):
    DEPRECATED_data.data_list_of_volunteers.write(list_of_volunteers)
