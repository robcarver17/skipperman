from typing import List

from app.objects.cadets import Cadet

from app.objects.qualifications import ListOfQualifications, ListOfCadetsWithQualifications, Qualification, CadetWithQualification

from app.data_access.data import data


def load_list_of_qualifications() -> ListOfQualifications:
    return data.data_list_of_qualifications.read()

def save_list_of_qualifications(list_of_qualifications: ListOfQualifications):
    data.data_list_of_qualifications.write(list_of_qualifications)

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

def list_of_named_qualifications_for_cadet(cadet: Cadet) -> list[str]:
    list_of_ids = list_of_qualification_ids_for_cadet(cadet)
    list_of_qualification = load_list_of_qualifications()
    list_of_names= [list_of_qualification.name_given_id(id) for id in list_of_ids]

    return list_of_names

def list_of_qualification_ids_for_cadet(cadet: Cadet) -> list[str]:
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
    return data.data_list_of_cadets_with_qualifications.read()


def save_list_of_cadets_with_qualifications(list_of_cadets_with_qualifications: ListOfCadetsWithQualifications):
    data.data_list_of_cadets_with_qualifications.write(list_of_cadets_with_qualifications)

def update_qualifications_for_cadet(cadet: Cadet, list_of_qualification_names_for_this_cadet: list[str]):
    list_of_cadets_with_qualifications = load_list_of_cadets_with_qualifications()
    list_of_qualifications = load_list_of_qualifications()
    list_of_qualification_ids = [list_of_qualifications.id_given_name(qual_name) for qual_name in list_of_qualification_names_for_this_cadet]
    list_of_cadets_with_qualifications.update_for_cadet(cadet_id = cadet.id, list_of_qualification_ids=list_of_qualification_ids)
    save_list_of_cadets_with_qualifications(list_of_cadets_with_qualifications)
