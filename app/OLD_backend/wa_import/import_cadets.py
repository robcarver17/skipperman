from app.OLD_backend.data.cadets import CadetData
from app.OLD_backend.data.cadets_at_event_id_level import CadetsAtEventIdLevelData
from app.backend.cadets.import_membership_list import get_temp_cadet_file_list_of_memberships
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet
from app.objects.exceptions import missing_data
from app.objects.events import Event


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


def is_cadet_marked_as_test_cadet_to_skip_in_for_row_in_mapped_data(
    interface: abstractInterface, row_id: str, event: Event
) -> bool:
    cadets_at_event_data = CadetsAtEventIdLevelData(interface.data)
    cadet_id = cadets_at_event_data.identifed_cadet_id_given_row_id_at_event(
        event=event, row_id=row_id
    )
    return cadet_id is missing_data
