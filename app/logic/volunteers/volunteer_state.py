from app.logic.abstract_interface import abstractInterface
from app.logic.volunteers.constants import VOLUNTEER
from app.backend.volunteers import get_volunteer_from_list_of_volunteers
from app.objects.volunteers import Volunteer


def update_state_for_specific_volunteer(interface: abstractInterface, volunteer_selected: str):
    interface.set_persistent_value(key=VOLUNTEER, value=volunteer_selected)


def get_volunteer_from_state(interface: abstractInterface) -> Volunteer:
    volunteer_selected = get_volunteer_selected_from_state(interface)

    return get_volunteer_from_list_of_volunteers(volunteer_selected)


def get_volunteer_selected_from_state(interface: abstractInterface) -> str:
    return interface.get_persistent_value(VOLUNTEER)
