from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import missing_data
from app.objects.volunteers import Volunteer

VOLUNTEER = "volunteer"


def update_state_for_specific_volunteer(
    interface: abstractInterface, volunteer: Volunteer
):
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer.id)



def update_state_with_volunteer_id(interface: abstractInterface, volunteer_id: str):
    interface.set_persistent_value(key=VOLUNTEER, value=volunteer_id)


def get_volunteer_from_state(interface: abstractInterface) -> Volunteer:
    volunteer_id = get_volunteer_id_selected_from_state(interface)

    return get_volunteer_from_id(
        object_store=interface.object_store, volunteer_id=volunteer_id
    )

def is_volunteer_id_set_in_state(interface: abstractInterface) -> bool:
    volunteer_id = get_volunteer_id_selected_from_state(interface=interface, default=missing_data)

    return not volunteer_id is missing_data

def get_volunteer_id_selected_from_state(interface: abstractInterface, default = missing_data) -> str:
    return str(interface.get_persistent_value(VOLUNTEER, default=default))


def get_volunteer_at_event_from_state(
    interface: abstractInterface,
) -> Volunteer:
    volunteer_id = get_volunteer_id_selected_from_state(interface)  ## NEEDS TO BE SET
    return get_volunteer_from_id(
        object_store=interface.object_store, volunteer_id=volunteer_id
    )

def clear_volunteer_id_in_state(interface: abstractInterface):
    interface.clear_persistent_value(VOLUNTEER)