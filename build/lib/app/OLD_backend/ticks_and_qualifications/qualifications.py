from typing import List

from app.objects.cadets import Cadet
from app.objects.qualifications import ListOfCadetsWithIdsAndQualifications

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.data.qualification import QualificationData


def load_list_of_cadets_with_qualifications(
    interface: abstractInterface,
) -> ListOfCadetsWithIdsAndQualifications:
    qualification_data = QualificationData(interface.data)
    return qualification_data.get_list_of_cadets_with_qualifications()


def list_of_qualification_ids_for_cadet(
    interface: abstractInterface, cadet: Cadet
) -> List[str]:
    qualification_data = QualificationData(interface.data)

    return qualification_data.list_of_qualification_ids_for_cadet(cadet)


def sorted_list_of_named_qualifications_for_cadet(
    interface: abstractInterface, cadet: Cadet
) -> List[str]:
    qualification_data = QualificationData(interface.data)
    return qualification_data.list_of_named_qualifications_for_cadet(cadet)


def get_list_of_all_qualification_names(interface: abstractInterface):
    qualification_data = QualificationData(interface.data)
    return qualification_data.get_list_of_all_qualification_names()
