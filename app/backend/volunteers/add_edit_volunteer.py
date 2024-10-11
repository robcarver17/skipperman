from app.OLD_backend.data.volunteers import VolunteerData
from app.data_access.store.data_layer import DataLayer
from app.data_access.store.object_store import ObjectStore

from app.backend.volunteers.list_of_volunteers import get_list_of_volunteers, update_list_of_volunteers
from app.objects.volunteers import Volunteer




## adding and warning


def modify_volunteer(object_store: ObjectStore, existing_volunteer: Volunteer, updated_volunteer: Volunteer):
    list_of_volunteers = get_list_of_volunteers(object_store)
    list_of_volunteers.update_existing_volunteer(existing_volunteer=existing_volunteer, updated_volunteer=updated_volunteer)
    update_list_of_volunteers(object_store=object_store, list_of_volunteers=list_of_volunteers)


def add_new_verified_volunteer(
        object_store: ObjectStore, volunteer: Volunteer
):
    list_of_volunteers = get_list_of_volunteers(object_store)

    list_of_volunteers.add(volunteer)
    update_list_of_volunteers(list_of_volunteers=list_of_volunteers, object_store=object_store)


def warning_str_for_similar_volunteers(
    object_store: ObjectStore, volunteer: Volunteer
) -> str:
    similar_volunteers = list_of_similar_volunteers(
        object_store=object_store, volunteer=volunteer
    )

    if len(similar_volunteers) > 0:
        similar_volunteers_str = ", ".join(
            [str(other_volunteer) for other_volunteer in similar_volunteers]
        )
        ## Some similar volunteers, let's see if it's a match
        return (
            "Following existing volunteers look awfully similar:\n %s"
            % similar_volunteers_str
        )
    else:
        return ""


def list_of_similar_volunteers(
    object_store: ObjectStore, volunteer: Volunteer
) -> list:
    list_of_volunteers = get_list_of_volunteers(object_store)
    return list_of_volunteers.similar_volunteers(volunteer)


def verify_volunteer_and_warn(
    object_store: ObjectStore, volunteer: Volunteer
) -> str:
    warn_text = ""
    if len(volunteer.surname) < 4:
        warn_text += "Surname seems too short. "
    if len(volunteer.first_name) < 4:
        warn_text += "First name seems too short. "
    warn_text += warning_str_for_similar_volunteers(
        object_store=object_store, volunteer=volunteer
    )

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text
