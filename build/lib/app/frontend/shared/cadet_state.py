from app.objects.exceptions import missing_data, MissingData

from app.OLD_backend.cadets import get_cadet_from_id
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet


def clear_cadet_state(interface: abstractInterface):
    interface.clear_persistent_value(CADET)


def update_state_for_specific_cadet(interface: abstractInterface, cadet: Cadet):
    update_state_for_specific_cadet_id(interface=interface, cadet_id=cadet.id)


def update_state_for_specific_cadet_id(interface: abstractInterface, cadet_id: str):
    interface.set_persistent_value(key=CADET, value=cadet_id)


def get_cadet_from_state(interface: abstractInterface) -> Cadet:
    cadet_id = get_cadet_id_selected_from_state(interface)
    if cadet_id is missing_data:
        raise MissingData

    return get_cadet_from_id(data_layer=interface.data, cadet_id=cadet_id)


def get_cadet_id_selected_from_state(
    interface: abstractInterface, default=missing_data
) -> str:
    return interface.get_persistent_value(CADET, default=default)


CADET = "Selected_Cadet"