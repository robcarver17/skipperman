import datetime
from copy import copy

from app.data_access.store.object_store import ObjectStore

from app.backend.cadets.list_of_cadets import (
    get_list_of_similar_cadets_from_data,
    DEPRECATE_get_list_of_cadets,
    update_list_of_cadets,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import (
    Cadet,
    is_cadet_age_surprising,
    cadet_seems_too_old,
    cadet_seems_too_young,
)


def add_new_verified_cadet(object_store: ObjectStore, cadet: Cadet) -> Cadet:
    list_of_cadets = DEPRECATE_get_list_of_cadets(object_store)
    cadet = list_of_cadets.add(cadet)
    update_list_of_cadets(
        object_store=object_store, updated_list_of_cadets=list_of_cadets
    )

    return cadet


def modify_cadet(interface: abstractInterface, existing_cadet: Cadet, new_cadet: Cadet):
    interface.update(interface.object_store.data_api.data_list_of_cadets.modify_cadet, existing_cadet=existing_cadet, new_cadet=new_cadet)


def modify_cadet_date_of_birth(
    object_store: ObjectStore, existing_cadet: Cadet, new_date_of_birth: datetime.date
):
    new_cadet = copy(existing_cadet)
    new_cadet.date_of_birth = new_date_of_birth
    list_of_cadets = DEPRECATE_get_list_of_cadets(object_store)
    list_of_cadets.update_cadet(existing_cadet=existing_cadet, new_cadet=new_cadet)
    update_list_of_cadets(
        object_store=object_store, updated_list_of_cadets=list_of_cadets
    )


def verify_cadet_and_return_warnings(object_store: ObjectStore, cadet: Cadet) -> str:
    warn_text = ""
    if len(cadet.surname) < 3:
        warn_text += "Surname seems too short. "
    if len(cadet.first_name) < 3:
        warn_text += "First name seems too short. "

    if cadet.has_default_date_of_birth:
        warn_text += "Date of birth not available - using default. "
    elif cadet_seems_too_old(cadet):
        warn_text += (
            "Sailor is too old to be a cadet: OK if event is a junior race series. "
        )
    elif cadet_seems_too_young(cadet):
        warn_text += "** SAILOR IS TOO YOUNG TO BE A CADET MEMBER **"

    warn_text += warning_for_similar_cadets(cadet=cadet, object_store=object_store)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text


def warning_for_similar_cadets(object_store: ObjectStore, cadet: Cadet) -> str:
    similar_cadets = get_list_of_similar_cadets_from_data(
        object_store=object_store, cadet=cadet
    )

    if len(similar_cadets) > 0:
        similar_cadets_str = ", ".join(
            [str(other_cadet) for other_cadet in similar_cadets]
        )
        return "Following cadets look awfully similar:\n %s" % similar_cadets_str
    else:
        return ""
