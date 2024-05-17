from typing import List

from app.objects.cadets import Cadet
from app.objects.qualifications import Qualification, ListOfCadetsWithQualifications, ListOfQualifications

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.qualification import QualificationData, DEPRECATE_load_list_of_qualifications, \
    DEPRECATE_list_of_qualification_ids_for_cadet, DEPRECATE_save_list_of_qualifications


def apply_qualification_to_cadet(interface: abstractInterface, cadet_id:str, qualification: Qualification):
    qualification_data = QualificationData(interface.data)
    qualification_data.apply_qualification_to_cadet(cadet_id=cadet_id, qualification=qualification)


def remove_qualification_from_cadet(interface: abstractInterface, cadet_id:str, qualification: Qualification):
    qualification_data = QualificationData(interface.data)
    qualification_data.remove_qualification_from_cadet(cadet_id=cadet_id, qualification=qualification)


def update_qualifications_for_cadet(interface: abstractInterface, cadet: Cadet, list_of_qualification_names_for_this_cadet: List[str]):
    qualification_data = QualificationData(interface.data)
    qualification_data.update_qualifications_for_cadet(cadet=cadet, list_of_qualification_names_for_this_cadet=list_of_qualification_names_for_this_cadet)


def load_list_of_cadets_with_qualifications(interface: abstractInterface) -> ListOfCadetsWithQualifications:
    qualification_data = QualificationData(interface.data)
    return qualification_data.get_list_of_cadets_with_qualifications()


def highest_qualification_for_cadet(interface: abstractInterface, cadet: Cadet) -> str:
    list_of_ids = DEPRECATE_list_of_qualification_ids_for_cadet(cadet)
    list_of_qualification = DEPRECATE_load_list_of_qualifications() ## last is best
    highest = ''
    for qual in list_of_qualification:
        if qual.id in list_of_ids:
            highest = qual.name

    return highest


def list_of_qualification_ids_for_cadet(interface: abstractInterface, cadet: Cadet) -> List[str]:
    qualification_data = QualificationData(interface.data)

    return qualification_data.list_of_qualification_ids_for_cadet(cadet)


def sorted_list_of_named_qualifications_for_cadet(interface: abstractInterface, cadet: Cadet) -> List[str]:
    qualification_data = QualificationData(interface.data)
    return qualification_data.list_of_named_qualifications_for_cadet(cadet)


def get_list_of_all_qualification_names(interface: abstractInterface):
    qualification_data = QualificationData(interface.data)
    return qualification_data.get_list_of_all_qualification_names()


def add_new_qualification_given_string_and_return_list(new_qualification: str) -> ListOfQualifications:
    list_of_qualifications = DEPRECATE_load_list_of_qualifications()
    list_of_qualifications.add(new_qualification)
    DEPRECATE_save_list_of_qualifications(list_of_qualifications)

    return list_of_qualifications


def delete_qualification_given_string_and_return_list(qualification: str) -> ListOfQualifications:
    list_of_qualifications = DEPRECATE_load_list_of_qualifications()
    list_of_qualifications.delete_given_name(qualification)
    DEPRECATE_save_list_of_qualifications(list_of_qualifications)

    return list_of_qualifications


def modify_qualification_given_string_and_return_list(existing_value_as_str:str, new_value_as_str:str) -> ListOfQualifications:
    list_of_qualifications = DEPRECATE_load_list_of_qualifications()
    list_of_qualifications.delete_given_name(existing_value_as_str)
    list_of_qualifications.add(new_value_as_str)
    DEPRECATE_save_list_of_qualifications(list_of_qualifications)

    return list_of_qualifications
