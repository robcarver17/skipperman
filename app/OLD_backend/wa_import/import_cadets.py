from app.OLD_backend.data.cadets import CadetData
from app.backend.cadets.import_membership_list import (
    get_temp_cadet_file_list_of_memberships,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet


def get_current_cadet_from_temp_file(cadet_id: str) -> Cadet:
    temp_file = get_temp_cadet_file_list_of_memberships()
    cadet = temp_file.object_with_id(cadet_id)
    cadet_without_id = Cadet(cadet.first_name, cadet.surname, cadet.date_of_birth)
    return cadet_without_id


def replace_cadet_with_id_with_new_cadet_details(
    interface: abstractInterface, existing_cadet_id: str, new_cadet: Cadet
):
    cadet_data = CadetData(interface.data)
    cadet_data.replace_cadet_with_id_with_new_cadet_details(
        existing_cadet_id=existing_cadet_id, new_cadet=new_cadet
    )


