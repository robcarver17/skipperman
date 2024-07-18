from app.OLD_backend.cadets import  DEPRECATE_get_cadet_from_id
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet


def clear_cadet_state(interface: abstractInterface):
    interface.clear_persistent_value(CADET)

def update_state_for_specific_cadet(interface: abstractInterface, cadet_id_selected: str):
    interface.set_persistent_value(key=CADET, value=cadet_id_selected)


def get_cadet_from_state(interface: abstractInterface) -> Cadet:
    cadet_id = get_cadet_id_selected_from_state(interface)

    return DEPRECATE_get_cadet_from_id(interface=interface, cadet_id=cadet_id)


def get_cadet_id_selected_from_state(interface: abstractInterface) -> str:
    return interface.get_persistent_value(CADET)


CADET = "Selected_Cadet"
