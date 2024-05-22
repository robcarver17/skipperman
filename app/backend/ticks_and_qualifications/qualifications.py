from typing import List

from app.objects.cadets import Cadet
from app.objects.qualifications import Qualification, ListOfCadetsWithQualifications

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.qualification import QualificationData

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



def list_of_qualification_ids_for_cadet(interface: abstractInterface, cadet: Cadet) -> List[str]:
    qualification_data = QualificationData(interface.data)

    return qualification_data.list_of_qualification_ids_for_cadet(cadet)


def sorted_list_of_named_qualifications_for_cadet(interface: abstractInterface, cadet: Cadet) -> List[str]:
    qualification_data = QualificationData(interface.data)
    return qualification_data.list_of_named_qualifications_for_cadet(cadet)


def get_list_of_all_qualification_names(interface: abstractInterface):
    qualification_data = QualificationData(interface.data)
    return qualification_data.get_list_of_all_qualification_names()


