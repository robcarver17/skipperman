from typing import List

from app.data_access.store.data_layer import DataLayer

from app.objects.cadets import ListOfCadets

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.volunteers import VolunteerData, SORT_BY_SURNAME
from app.objects.exceptions import arg_not_passed
from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.composed.volunteers_with_skills import SkillsDict, ListOfVolunteersWithSkills


def get_volunteer_with_name(
    data_layer: DataLayer, volunteer_name: str
) -> Volunteer:
    volunteer_data = VolunteerData(data_layer)
    return volunteer_data.get_volunteer_given_name(
        volunteer_name=volunteer_name
    )



def EPRECATE_get_volunteer_name_from_id(interface: abstractInterface, volunteer_id: str) -> str:
    volunteer = DEPRECATE_get_volunteer_from_id(interface=interface, volunteer_id=volunteer_id)
    return volunteer.name

def get_volunteer_name_from_id(data_layer: DataLayer, volunteer_id: str) -> str:
    volunteer = get_volunteer_from_id(data_layer=data_layer, volunteer_id=volunteer_id)
    return volunteer.name



def DEPRECATE_get_volunteer_from_id(interface: abstractInterface, volunteer_id: str) -> Volunteer:
    volunteer_data = VolunteerData(interface.data)
    list_of_volunteers = volunteer_data.get_list_of_volunteers()
    return list_of_volunteers.object_with_id(volunteer_id)

def get_volunteer_from_id(data_layer: DataLayer, volunteer_id: str) -> Volunteer:
    volunteer_data = VolunteerData(data_layer)
    list_of_volunteers = volunteer_data.get_list_of_volunteers()
    return list_of_volunteers.object_with_id(volunteer_id)



#### CONNECTIONS

def are_all_cadet_ids_in_list_already_connection_to_volunteer(
    data_layer: DataLayer, volunteer: Volunteer, list_of_cadet_ids: List[str]
) -> bool:
    list_of_already_connected = [
        is_cadet_already_connected_to_volunteer_in_volunteer_list(
            data_layer=data_layer, volunteer=volunteer, cadet_id=cadet_id
        )
        for cadet_id in list_of_cadet_ids
    ]

    return all(list_of_already_connected)


def is_cadet_already_connected_to_volunteer_in_volunteer_list(
    data_layer: DataLayer, cadet_id: str, volunteer: Volunteer
) -> bool:
    volunteer_data = VolunteerData(data_layer)
    return volunteer_data.is_cadet_already_connected_to_volunteer_in_volunteer_list(
        cadet_id=cadet_id, volunteer=volunteer
    )


def get_connected_cadets(data_layer: DataLayer, volunteer: Volunteer) -> ListOfCadets:
    volunteer_data = VolunteerData(data_layer)

    return volunteer_data.get_connected_cadets(volunteer)


def add_list_of_cadet_connections_to_volunteer(
    data_layer: DataLayer,
    volunteer: Volunteer,
    list_of_cadets_to_connect: ListOfCadets,
):
    volunteer_data = VolunteerData(data_layer)

    for cadet in list_of_cadets_to_connect:
        volunteer_data.add_volunteer_connection_to_cadet_in_master_list_of_volunteers(
            cadet=cadet, volunteer=volunteer
        )

### skills

def get_dict_of_existing_skills(data_layer: DataLayer, volunteer: Volunteer) -> SkillsDict:
    volunteer_data = VolunteerData(data_layer)
    return volunteer_data.get_dict_of_existing_skills_for_volunteer(volunteer)


def string_if_volunteer_can_drive_else_empty(data_layer: DataLayer, volunteer: Volunteer) -> str:
    if can_volunteer_drive_safety_boat(data_layer=data_layer, volunteer=volunteer):
        return "PB2" ## can be anything
    else:
        return ""


def can_volunteer_drive_safety_boat(
    data_layer: DataLayer, volunteer: Volunteer
) -> bool:
    volunteer_data = VolunteerData(data_layer)
    return volunteer_data.can_volunteer_drive_safety_boat(volunteer)


def add_boat_related_skill_for_volunteer(
    data_layer: DataLayer, volunteer: Volunteer
):
    volunteer_data = VolunteerData(data_layer)
    volunteer_data.add_volunteer_driving_qualification(volunteer)


def remove_boat_related_skill_for_volunteer(
    data_layer: DataLayer, volunteer: Volunteer
):
    volunteer_data = VolunteerData(data_layer)
    volunteer_data.remove_driving_qualification_for_volunteer(volunteer)


def load_list_of_volunteer_skills(data_layer: DataLayer) -> ListOfVolunteersWithSkills:
    volunteer_data = VolunteerData(data_layer)
    return volunteer_data.get_list_of_volunteer_skills()


def is_volunteer_with_id_qualified_as_SI(data_layer: DataLayer, volunteer_id: str):
    volunteer_data = VolunteerData(data_layer)
    return volunteer_data.is_volunteer_with_id_SI(volunteer_id)


def get_list_of_volunteers_sorted_by_surname(
    data_layer: DataLayer
) -> ListOfVolunteers:
    return get_sorted_list_of_volunteers(data_layer=data_layer, sort_by=SORT_BY_SURNAME)

### lists
def get_sorted_list_of_volunteers(
    data_layer: DataLayer, sort_by: str = arg_not_passed
) -> ListOfVolunteers:
    volunteer_data = VolunteerData(data_layer)
    return volunteer_data.get_sorted_list_of_volunteers(sort_by)



def get_list_of_all_volunteers(data_layer: DataLayer) -> ListOfVolunteers:
    volunteer_data = VolunteerData(data_layer)
    return volunteer_data.get_list_of_volunteers()


def get_dict_of_volunteer_names_and_volunteers(data_layer: DataLayer):
    list_of_volunteers = get_list_of_all_volunteers(data_layer)
    return dict([(str(volunteer), volunteer) for volunteer in list_of_volunteers])
