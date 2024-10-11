from typing import List

from app.OLD_backend.data.cadets import CadetData

from app.data_access.store.data_layer import DataLayer

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.exceptions import arg_not_passed
from app.objects.volunteers import (
    ListOfVolunteers,
    Volunteer,
)
from app.objects.composed.volunteers_with_skills import SkillsDict, ListOfVolunteersWithSkills
from app.objects.cadet_volunteer_connections_with_ids import ListOfCadetVolunteerAssociationsWithIds


class VolunteerData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api


    def get_volunteer_given_name(
        self, volunteer_name: str
    ) -> Volunteer:
        list_of_volunteers = self.get_list_of_volunteers()

        return list_of_volunteers.get_volunteer_from_list_of_volunteers_given_name(volunteer_name)

    def is_volunteer_with_id_SI(self, volunteer_id: str) -> bool:
        list_of_skills = self.get_list_of_volunteer_skills()

        return list_of_skills.volunteer_is_senior_instructor(volunteer_id)

    def get_dict_of_existing_skills_for_volunteer(
        self, volunteer: Volunteer
    ) -> SkillsDict:
        return self._get_dict_of_existing_skills_for_volunteer_id(
            volunteer_id=volunteer.id
        )

    def _get_dict_of_existing_skills_for_volunteer_id(
        self, volunteer_id: str
    ) -> SkillsDict:
        all_skills = self.get_list_of_volunteer_skills()
        return all_skills.dict_of_skills_for_volunteer_id(volunteer_id=volunteer_id)

    def add_volunteer_driving_qualification(self, volunteer: Volunteer):
        skills = self.get_list_of_volunteer_skills()
        skills.add_volunteer_driving_qualification(volunteer.id)
        self.save_list_of_volunteer_skills(skills)

    def remove_driving_qualification_for_volunteer(self, volunteer: Volunteer):
        skills = self.get_list_of_volunteer_skills()
        skills.remove_volunteer_driving_qualification(volunteer.id)
        self.save_list_of_volunteer_skills(skills)

    def replace_skills_for_volunteer_with_new_skills_dict(self, volunteer: Volunteer, dict_of_skills: SkillsDict):
        all_skills = self.get_list_of_volunteer_skills()
        all_skills.replace_skills_for_volunteer_with_new_skills_dict(
            volunteer_id=volunteer.id, dict_of_skills=dict_of_skills
        )
        self.save_list_of_volunteer_skills(all_skills)

    def list_of_volunteer_ids_who_can_drive_safety_boat(self) -> List[str]:
        volunteer_skills = self.get_list_of_volunteer_skills()
        list_of_volunteer_ids_with_boat_skills = (
            volunteer_skills.list_of_volunteer_ids_who_can_drive_safety_boat()
        )

        return list_of_volunteer_ids_with_boat_skills

    def can_volunteer_drive_safety_boat(self, volunteer: Volunteer) -> bool:
        return self._can_volunteer_with_id_drive_safety_boat(volunteer.id)

    def _can_volunteer_with_id_drive_safety_boat(self, volunteer_id: str) -> bool:
        skills = self.get_list_of_volunteer_skills()
        return skills.volunteer_id_can_drive_safety_boat(volunteer_id)

    ## Cadet connections

    def delete_cadet_connection(self, cadet: Cadet, volunteer: Volunteer):
        existing_connections = self.get_list_of_cadet_volunteer_associations()
        existing_connections.delete(cadet_id=cadet.id, volunteer_id=volunteer.id)
        self.save_list_of_cadet_volunteer_associations(existing_connections)

    def get_connected_cadets(self, volunteer: Volunteer) -> ListOfCadets:
        existing_connections = self.get_list_of_cadet_volunteer_associations()
        list_of_cadets = self.get_list_of_cadets()

        connected_ids = existing_connections.list_of_connections_for_volunteer(
            volunteer.id
        )
        connected_cadets = [list_of_cadets.cadet_with_id(id) for id in connected_ids]
        return ListOfCadets(connected_cadets)

    def add_volunteer_connection_to_cadet_in_master_list_of_volunteers(
        self, cadet: Cadet, volunteer: Volunteer
    ):
        existing_connections = self.get_list_of_cadet_volunteer_associations()
        existing_connections.add(cadet_id=cadet.id, volunteer_id=volunteer.id)
        self.save_list_of_cadet_volunteer_associations(existing_connections)

    def is_cadet_already_connected_to_volunteer_in_volunteer_list(
        self, cadet_id: str, volunteer: Volunteer
    ) -> bool:
        existing_connections = self.get_list_of_cadet_volunteer_associations()
        connections_for_volunteer = (
            existing_connections.list_of_connections_for_volunteer(volunteer.id)
        )
        return cadet_id in connections_for_volunteer


    def get_list_of_volunteers_connected_to_cadet(self, cadet_id: str) -> ListOfVolunteers:
        list_of_cadet_volunteer_associations = (
            self.get_list_of_cadet_volunteer_associations()
        )
        list_of_associated_ids = list_of_cadet_volunteer_associations.list_of_volunteer_ids_associated_with_cadet_id(
            cadet_id=cadet_id
        )
        list_of_all_volunteers = self.get_list_of_volunteers()

        list_of_volunteers_associated_with_cadet = ListOfVolunteers([
            list_of_all_volunteers.volunteer_with_id(volunteer_id)
            for volunteer_id in list_of_associated_ids
        ])

        return list_of_volunteers_associated_with_cadet

    ## add/modify
    def add_new_volunteer(self, volunteer: Volunteer):
        list_of_volunteers = self.get_list_of_volunteers()

        list_of_volunteers.add(volunteer)
        self.save_list_of_volunteers(list_of_volunteers)

    def update_existing_volunteer(self, volunteer: Volunteer):
        list_of_volunteers = self.get_list_of_volunteers()
        list_of_volunteers.update_existing_volunteer(volunteer=volunteer)
        self.save_list_of_volunteers(list_of_volunteers)

    ## get
    def list_of_similar_volunteers(self, volunteer: Volunteer) -> ListOfVolunteers:
        list_of_volunteers = self.get_list_of_volunteers()
        return list_of_volunteers.similar_volunteers(volunteer)

    def volunteer_with_id(self, volunteer_id: str) -> Volunteer:
        list_of_volunteers = self.get_list_of_volunteers()
        return list_of_volunteers.object_with_id(volunteer_id)

    def get_volunteer_with_matching_name(self, volunteer: Volunteer) -> Volunteer:
        list_of_volunteers = self.get_list_of_volunteers()
        return list_of_volunteers.volunteer_with_matching_name(volunteer)

    def get_sorted_list_of_volunteers(
        self, sort_by: str = arg_not_passed
    ) -> ListOfVolunteers:
        master_list = self.get_list_of_volunteers()
        if sort_by is arg_not_passed:
            return master_list
        if sort_by == SORT_BY_SURNAME:
            return master_list.sort_by_surname()
        elif sort_by == SORT_BY_FIRSTNAME:
            return master_list.sort_by_firstname()
        else:
            return master_list

    ## getters and savers
    def get_list_of_cadets(self) -> ListOfCadets:
        return self.cadet_data.get_list_of_cadets()

    def get_list_of_volunteers(self) -> ListOfVolunteers:
        list_of_volunteers = self.data_api.get_list_of_volunteers()
        return list_of_volunteers

    def save_list_of_volunteers(self, list_of_volunteers: ListOfVolunteers):
        self.data_api.save_list_of_volunteers(list_of_volunteers)

    def get_list_of_cadet_volunteer_associations(
        self,
    ) -> ListOfCadetVolunteerAssociationsWithIds:
        return self.data_api.get_list_of_cadet_volunteer_associations()

    def save_list_of_cadet_volunteer_associations(
        self, list_of_associations: ListOfCadetVolunteerAssociationsWithIds
    ):
        return self.data_api.save_list_of_cadet_volunteer_associations(
            list_of_associations
        )

    def get_list_of_volunteer_skills(self) -> ListOfVolunteersWithSkills:
        return self.data_api.get_list_of_volunteer_skills()

    def save_list_of_volunteer_skills(
        self, list_of_volunteer_skills: ListOfVolunteersWithSkills
    ):
        return self.data_api.save_list_of_volunteer_skills(list_of_volunteer_skills)

    @property
    def cadet_data(self) -> CadetData:
        return CadetData(self.data_api)


SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"
