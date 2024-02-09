from app.backend.cadets import get_cadet_from_list_of_cadets
from app.logic.cadets.constants import CADET
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet


def update_state_for_specific_cadet(interface: abstractInterface, cadet_selected: str):
    interface.set_persistent_value(key=CADET, value=cadet_selected)


def get_cadet_from_state(interface: abstractInterface) -> Cadet:
    cadet_selected = get_cadet_selected_from_state(interface)

    return get_cadet_from_list_of_cadets(cadet_selected)


def get_cadet_selected_from_state(interface: abstractInterface) -> str:
    return interface.get_persistent_value(CADET)


