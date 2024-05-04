from typing import List

from app.objects.cadets import Cadet

from app.objects.qualifications import ListOfQualifications, ListOfCadetsWithQualifications, Qualification, CadetWithQualification

from app.data_access.data import DEPRECATED_data

from typing import List

from app.objects.constants import arg_not_passed

from app.data_access.storage_layer.api import DataLayer
from app.data_access.data import DEPRECATED_data
from app.objects.cadets import Cadet, ListOfCadets


class QualificationData():
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def apply_qualification_to_cadet(self, cadet_id: str, qualification: Qualification):
        list_of_cadets_with_qualifications = self.get_list_of_cadets_with_qualifications()
        list_of_cadets_with_qualifications.apply_qualification_to_cadet(cadet_id=cadet_id, qualification_id=qualification.id)
        save_list_of_cadets_with_qualifications(list_of_cadets_with_qualifications)

    def remove_qualification_from_cadet(self, cadet_id: str, qualification: Qualification):
        list_of_cadets_with_qualifications = self.get_list_of_cadets_with_qualifications()
        list_of_cadets_with_qualifications.remove_qualification_from_cadet(cadet_id=cadet_id, qualification_id=qualification.id)
        save_list_of_cadets_with_qualifications(list_of_cadets_with_qualifications)


    def list_of_cadet_ids_with_qualification(self, qualification: Qualification) -> List[str]:
        list_of_qualification_ids_for_cadet = self.get_list_of_cadets_with_qualifications()
        return list_of_qualification_ids_for_cadet.list_of_cadet_ids_with_qualification(qualification_id = qualification.id)

    def does_cadet_id_have_qualification(self, cadet_id, qualification_id: str)-> bool:
        list_of_qualification_ids_for_cadet = self.get_list_of_cadets_with_qualifications()

        return list_of_qualification_ids_for_cadet.does_cadet_id_have_qualification(cadet_id=cadet_id, qualification_id=qualification_id)

    def get_qualification_given_name(self, name: str) -> Qualification:
        list_of_qualifications = self.load_list_of_qualifications()
        idx = list_of_qualifications.idx_given_name(name)
        return list_of_qualifications[idx]


    def get_qualification_given_id(self, id: str) -> Qualification:
        list_of_qualifications = self.load_list_of_qualifications()

        return list_of_qualifications.object_with_id(id)

    def load_list_of_qualifications(self) -> ListOfQualifications:
        return self.data_api.get_list_of_qualifications()

    def get_list_of_cadets_with_qualifications(self) -> ListOfCadetsWithQualifications:
        return self.data_api.get_list_of_cadets_with_qualifications()

    def save_list_of_cadets_with_qualifications(self, list_of_cadets_with_qualifications: ListOfCadetsWithQualifications):
        self.data_api.save_list_of_cadets_with_qualifications(list_of_cadets_with_qualifications)


def load_list_of_qualifications() -> ListOfQualifications:
    return DEPRECATED_data.data_list_of_qualifications.read()

def save_list_of_qualifications(list_of_qualifications: ListOfQualifications):
    DEPRECATED_data.data_list_of_qualifications.write(list_of_qualifications)

def get_list_of_qualification_names():
    list_of_quals = load_list_of_qualifications()
    return list_of_quals.list_of_names()

def add_new_qualification_given_string_and_return_list(new_qualification: str) -> ListOfQualifications:
    list_of_qualifications = load_list_of_qualifications()
    list_of_qualifications.add(new_qualification)
    save_list_of_qualifications(list_of_qualifications)

    return list_of_qualifications

def delete_qualification_given_string_and_return_list(qualification: str) -> ListOfQualifications:
    list_of_qualifications = load_list_of_qualifications()
    list_of_qualifications.delete_given_name(qualification)
    save_list_of_qualifications(list_of_qualifications)

    return list_of_qualifications

def modify_qualification_given_string_and_return_list(existing_value_as_str:str, new_value_as_str:str) -> ListOfQualifications:
    list_of_qualifications = load_list_of_qualifications()
    list_of_qualifications.delete_given_name(existing_value_as_str)
    list_of_qualifications.add(new_value_as_str)
    save_list_of_qualifications(list_of_qualifications)

    return list_of_qualifications

def list_of_named_qualifications_for_cadet(cadet: Cadet) -> List[str]:
    list_of_ids = list_of_qualification_ids_for_cadet(cadet)
    list_of_qualification = load_list_of_qualifications()
    list_of_names= [list_of_qualification.name_given_id(id) for id in list_of_ids]

    return list_of_names

def list_of_qualification_ids_for_cadet(cadet: Cadet) -> List[str]:
    list_of_cadets_with_qualifications = load_list_of_cadets_with_qualifications()
    list_of_ids = list_of_cadets_with_qualifications.list_of_qualification_ids_for_cadet(cadet_id=cadet.id)
    return list_of_ids

def highest_qualification_for_cadet(cadet: Cadet) -> str:
    list_of_ids = list_of_qualification_ids_for_cadet(cadet)
    list_of_qualification = load_list_of_qualifications() ## last is best
    highest = ''
    for qual in list_of_qualification:
        if qual.id in list_of_ids:
            highest = qual.name

    return highest


def load_list_of_cadets_with_qualifications() -> ListOfCadetsWithQualifications:
    return DEPRECATED_data.data_list_of_cadets_with_qualifications.read()


def save_list_of_cadets_with_qualifications(list_of_cadets_with_qualifications: ListOfCadetsWithQualifications):
    DEPRECATED_data.data_list_of_cadets_with_qualifications.write(list_of_cadets_with_qualifications)

def update_qualifications_for_cadet(cadet: Cadet, list_of_qualification_names_for_this_cadet: List[str]):
    list_of_cadets_with_qualifications = load_list_of_cadets_with_qualifications()
    list_of_qualifications = load_list_of_qualifications()
    list_of_qualification_ids = [list_of_qualifications.id_given_name(qual_name) for qual_name in list_of_qualification_names_for_this_cadet]
    list_of_cadets_with_qualifications.update_for_cadet(cadet_id = cadet.id, list_of_qualification_ids=list_of_qualification_ids)
    save_list_of_cadets_with_qualifications(list_of_cadets_with_qualifications)
