from app.backend.cadets.list_of_cadets import get_cadet_from_id
from app.frontend.shared.cadet_state import get_cadet_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet


def get_cadet_to_delete_from_state(interface: abstractInterface) -> Cadet:
    return get_cadet_from_state(interface)  ## to make it clearer


def set_cadet_to_merge_with_in_state(interface: abstractInterface, cadet: Cadet):
    interface.set_persistent_value(CADET_TO_MERGE_WITH, cadet.id)


def get_cadet_to_merge_with_from_state(interface: abstractInterface):
    id = interface.get_persistent_value(CADET_TO_MERGE_WITH)
    return get_cadet_from_id(object_store=interface.object_store, cadet_id=id)


CADET_TO_MERGE_WITH = "merge_cadet_with"
