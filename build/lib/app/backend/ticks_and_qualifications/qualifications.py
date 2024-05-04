from app.objects.qualifications import Qualification

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.data.qualification import QualificationData

def apply_qualification_to_cadet(interface: abstractInterface, cadet_id:str, qualification: Qualification):
    qualification_data = QualificationData(interface.data)
    qualification_data.apply_qualification_to_cadet(cadet_id=cadet_id, qualification=qualification)


def remove_qualification_from_cadet(interface: abstractInterface, cadet_id:str, qualification: Qualification):
    qualification_data = QualificationData(interface.data)
    qualification_data.remove_qualification_from_cadet(cadet_id=cadet_id, qualification=qualification)
