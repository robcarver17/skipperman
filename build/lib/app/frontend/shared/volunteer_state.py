from app.backend.volunteers.list_of_volunteers import get_volunteer_from_list_of_given_str_of_volunteer

from app.objects_OLD.volunteers_at_event import DEPRECATE_VolunteerAtEvent
from app.objects_OLD.primtive_with_id.volunteer_at_event import VolunteerAtEventWithId

from app.OLD_backend.volunteers.volunteer_allocation import DEPRECATE_get_volunteer_at_event_with_id, get_volunteer_at_event
from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id

from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.volunteers import Volunteer

VOLUNTEER = "volunteer"


def update_state_for_specific_volunteer_given_volunteer_as_str(
    interface: abstractInterface, volunteer_selected: str
):
    volunteer = get_volunteer_from_list_of_given_str_of_volunteer(
        object_store=interface.object_store, volunteer_as_str=volunteer_selected
    )
    update_state_with_volunteer_id(interface=interface, volunteer_id=volunteer.id)


def update_state_with_volunteer_id(interface: abstractInterface, volunteer_id: str):
    interface.set_persistent_value(key=VOLUNTEER, value=volunteer_id)


def get_volunteer_from_state(interface: abstractInterface) -> Volunteer:
    volunteer_id = get_volunteer_id_selected_from_state(interface)

    return get_volunteer_from_id(object_store=interface.object_store, volunteer_id=volunteer_id)


def get_volunteer_id_selected_from_state(interface: abstractInterface) -> str:
    return str(interface.get_persistent_value(VOLUNTEER))

def get_volunteer_at_event_from_state(interface: abstractInterface) -> DEPRECATE_VolunteerAtEvent:
    volunteer_id = get_volunteer_id_selected_from_state(interface)  ## NEEDS TO BE SET
    event = get_event_from_state(interface)
    return get_volunteer_at_event(data_layer=interface.data, event = event, volunteer_id=volunteer_id)

def get_volunteer_at_event_with_id_from_state(interface: abstractInterface) -> VolunteerAtEventWithId:
    volunteer_id = get_volunteer_id_selected_from_state(interface)  ## NEEDS TO BE SET
    event = get_event_from_state(interface)
    volunteer_at_event_with_id = DEPRECATE_get_volunteer_at_event_with_id(
        interface=interface, volunteer_id=volunteer_id, event=event
    )

    return volunteer_at_event_with_id
