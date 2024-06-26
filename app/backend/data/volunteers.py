from typing import List

from app.backend.data.cadets import CadetData
from app.data_access.configuration.configuration import SI_SKILL

from app.data_access.storage_layer.api import DataLayer

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.constants import arg_not_passed
from app.objects.volunteers import ListOfVolunteerSkills, ListOfVolunteers, Volunteer, ListOfCadetVolunteerAssociations, \
    SkillsDict


class VolunteerData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def update_existing_volunteer(self, volunteer: Volunteer):

        list_of_volunteers = self.get_list_of_volunteers()
        index = list_of_volunteers.index_of_id(volunteer.id)
        list_of_volunteers[index] = volunteer
        self.save_list_of_volunteers(list_of_volunteers)

    def get_volunteer_from_list_of_volunteers_given_name(self, volunteer_name: str) -> Volunteer:
        list_of_volunteers = self.get_list_of_volunteers()
        list_of_volunteers_as_str = [volunteer.name for volunteer in list_of_volunteers]

        idx = list_of_volunteers_as_str.index(volunteer_name)

        return list_of_volunteers[idx]

    def is_volunteer_id_SI(self, volunteer_id: str) -> bool:
        dict_of_skills = self.get_dict_of_existing_skills_for_volunteer_id(volunteer_id)
        return dict_of_skills.get(SI_SKILL, False)

    def get_dict_of_existing_skills_for_volunteer(self, volunteer: Volunteer) -> SkillsDict:
        return self.get_dict_of_existing_skills_for_volunteer_id(volunteer_id=volunteer.id)

    def get_dict_of_existing_skills_for_volunteer_id(self, volunteer_id: str) ->SkillsDict:

        all_skills = self.get_list_of_volunteer_skills()
        return all_skills.dict_of_skills_for_volunteer_id(volunteer_id=volunteer_id)

    def add_boat_related_skill_for_volunteer(self, volunteer_id: str):
        skills = self.get_list_of_volunteer_skills()
        skills.add_boat_related_skill_for_volunteer(volunteer_id)
        self.save_list_of_volunteer_skills(skills)

    def remove_boat_related_skill_for_volunteer(self, volunteer_id: str):
        skills = self.get_list_of_volunteer_skills()
        skills.remove_boat_related_skill_for_volunteer(volunteer_id)
        self.save_list_of_volunteer_skills(skills)

    def save_skills_for_volunteer(self, volunteer: Volunteer, dict_of_skills: dict):
        all_skills = self.get_list_of_volunteer_skills()
        all_skills.replace_skills_for_volunteer_with_new_skills_dict(volunteer_id=volunteer.id,
                                                                     dict_of_skills=dict_of_skills)
        self.save_list_of_volunteer_skills(all_skills)

    def get_list_of_volunteer_ids_with_boat_skills(self ) -> List[str]:
        volunteer_skills = self.get_list_of_volunteer_skills()
        list_of_volunteer_ids_with_boat_skills = volunteer_skills.list_of_volunteer_ids_with_boat_related_skill()

        return list_of_volunteer_ids_with_boat_skills

    def boat_related_skill_for_volunteer(self, volunteer: Volunteer) -> bool:
        return self.boat_related_skill_for_volunteer_id(volunteer.id)

    def boat_related_skill_for_volunteer_id(self, volunteer_id: str) -> bool:
        skills = self.get_list_of_volunteer_skills()
        return skills.volunteer_id_has_boat_related_skills(volunteer_id)

    def delete_connection_in_data(self, cadet: Cadet, volunteer: Volunteer):

        existing_connections = self.get_list_of_cadet_volunteer_associations()
        existing_connections.delete(cadet_id=cadet.id, volunteer_id=volunteer.id)
        self.save_list_of_cadet_volunteer_associations(existing_connections)

    def get_connected_cadets(self, volunteer: Volunteer) -> ListOfCadets:
        existing_connections = self.get_list_of_cadet_volunteer_associations()
        list_of_cadets = self.get_list_of_cadets()

        connected_ids = existing_connections.list_of_connections_for_volunteer(volunteer.id)
        connected_cadets = [list_of_cadets.object_with_id(id) for id in connected_ids]
        return ListOfCadets(connected_cadets)

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

    def volunteer_with_id(self, volunteer_id: str) -> Volunteer:
        list_of_volunteers = self.get_list_of_volunteers()
        return list_of_volunteers.object_with_id(volunteer_id)

    def matching_volunteer_or_missing_data(self, volunteer: Volunteer) -> Volunteer:
        list_of_volunteers = self.get_list_of_volunteers()
        return list_of_volunteers.matching_volunteer(volunteer)

    def get_sorted_list_of_volunteers(self, sort_by: str = arg_not_passed) -> ListOfVolunteers:
        master_list = self.get_list_of_volunteers()
        if sort_by is arg_not_passed:
            return master_list
        if sort_by == SORT_BY_SURNAME:
            return master_list.sort_by_surname()
        elif sort_by == SORT_BY_FIRSTNAME:
            return master_list.sort_by_firstname()
        else:
            return master_list



    def get_list_of_cadets(self) -> ListOfCadets:
        return self.cadet_data.get_list_of_cadets()

    def get_list_of_volunteers(self) -> ListOfVolunteers:
        list_of_volunteers = self.data_api.get_list_of_volunteers()
        return list_of_volunteers

    def save_list_of_volunteers(self, list_of_volunteers: ListOfVolunteers):
        self.data_api.save_list_of_volunteers(list_of_volunteers)

    def get_list_of_cadet_volunteer_associations(self) -> ListOfCadetVolunteerAssociations:
        return self.data_api.get_list_of_cadet_volunteer_associations()

    def save_list_of_cadet_volunteer_associations(self, list_of_associations: ListOfCadetVolunteerAssociations):
        return self.data_api.save_list_of_cadet_volunteer_associations(list_of_associations)


    def get_list_of_volunteer_skills(self) -> ListOfVolunteerSkills:
        return self.data_api.get_list_of_volunteer_skills()

    def save_list_of_volunteer_skills(self, list_of_volunteer_skills: ListOfVolunteerSkills):
        return self.data_api.save_list_of_volunteer_skills(list_of_volunteer_skills)

    @property
    def cadet_data(self) -> CadetData:
        return CadetData(self.data_api)



SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"
