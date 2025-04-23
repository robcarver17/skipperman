from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.volunteers import Volunteer


def set_volunteer_to_merge_with_in_state(interface: abstractInterface, volunteer: Volunteer):
    interface.set_persistent_value(VOLUNTEER_TO_MERGE_WITH, volunteer.id)


def get_volunteer_to_merge_with_from_state(interface: abstractInterface) -> Volunteer:
    id = interface.get_persistent_value(VOLUNTEER_TO_MERGE_WITH)
    return get_volunteer_from_id(object_store=interface.object_store, volunteer_id=id)

VOLUNTEER_TO_MERGE_WITH = "merge_volunteer_with"

