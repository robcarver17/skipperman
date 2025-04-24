from app.data_access.configuration.configuration import SIMILARITY_LEVEL_TO_WARN_NAME
from app.data_access.store.object_store import ObjectStore

from app.backend.volunteers.list_of_volunteers import (
    get_list_of_volunteers,
    update_list_of_volunteers, list_of_similar_volunteers,
)
from app.objects.cadets import Cadet
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.utilities.utils import similar
from app.objects.volunteers import Volunteer


## adding and warning


def modify_volunteer(
    object_store: ObjectStore,
    existing_volunteer: Volunteer,
    updated_volunteer: Volunteer,
):
    list_of_volunteers = get_list_of_volunteers(object_store)
    list_of_volunteers.update_existing_volunteer(
        existing_volunteer=existing_volunteer, updated_volunteer=updated_volunteer
    )
    update_list_of_volunteers(
        object_store=object_store, list_of_volunteers=list_of_volunteers
    )


def add_new_verified_volunteer(object_store: ObjectStore, volunteer: Volunteer):
    list_of_volunteers = get_list_of_volunteers(object_store)

    list_of_volunteers.add(volunteer)
    update_list_of_volunteers(
        list_of_volunteers=list_of_volunteers, object_store=object_store
    )


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


def verify_volunteer_and_warn(object_store: ObjectStore, volunteer: Volunteer, cadet: Cadet = arg_not_passed) -> str:
    warn_text = ""
    if len(volunteer.surname) < 3:
        warn_text += "Surname seems too short. "
    if len(volunteer.first_name) < 3:
        warn_text += "First name seems too short. "
    warn_text += warning_str_for_similar_volunteers(
        object_store=object_store, volunteer=volunteer
    )
    if cadet is not arg_not_passed:
        could_be_cadet_not_volunteer = volunteer_name_is_similar_to_cadet_name(
            volunteer=volunteer, cadet=cadet
        )
        if could_be_cadet_not_volunteer:
            warn_text += "Volunteer name is similar to cadet name %s - are you sure this is actually a volunteer and not a cadet?" % cadet.name

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text


def volunteer_name_is_similar_to_cadet_name(cadet: Cadet, volunteer: Volunteer) -> bool:

    return similar(volunteer.name, cadet.name) > SIMILARITY_LEVEL_TO_WARN_NAME
