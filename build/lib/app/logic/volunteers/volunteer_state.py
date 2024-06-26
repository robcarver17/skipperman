from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.volunteers.constants import VOLUNTEER
from app.backend.volunteers.volunteers import (
    get_volunteer_from_id,
    get_volunteer_from_list_of_volunteers_given_volunteer_name,
)
from app.objects.volunteers import Volunteer


def update_state_for_specific_volunteer_given_volunteer_as_str(
    interface: abstractInterface, volunteer_selected: str
):
    volunteer = get_volunteer_from_list_of_volunteers_given_volunteer_name(
        interface=interface, volunteer_name=volunteer_selected
    )
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer.id)


def update_state_with_volunteer_id(interface: abstractInterface, volunteer_id: str):
    interface.set_persistent_value(key=VOLUNTEER, value=volunteer_id)


def get_volunteer_from_state(interface: abstractInterface) -> Volunteer:
    volunteer_id = get_volunteer_id_selected_from_state(interface)

    return get_volunteer_from_id(interface=interface, volunteer_id=volunteer_id)


def get_volunteer_id_selected_from_state(interface: abstractInterface) -> str:
    return str(interface.get_persistent_value(VOLUNTEER))
