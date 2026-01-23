import datetime
from copy import copy

from app.data_access.store.object_store import ObjectStore

from app.backend.cadets.list_of_cadets import (
    get_list_of_similar_cadets_from_data,
    get_list_of_cadets,
    update_list_of_cadets,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import (
    Cadet,
    is_cadet_age_surprising,
    cadet_seems_too_old,
    cadet_seems_too_young,
)


def add_new_verified_cadet(interface: abstractInterface, cadet: Cadet) -> Cadet:
    try:
        interface.update(interface.object_store.data_api.data_list_of_cadets.add_cadet, new_cadet=cadet)
    except Exception as e:
        interface.log_error("Error adding cadet %s: %s" % (str(cadet),str(e)))
        raise Exception(str(e))

    return cadet


def modify_cadet(interface: abstractInterface, existing_cadet: Cadet, new_cadet: Cadet):
    interface.update(interface.object_store.data_api.data_list_of_cadets.modify_cadet, existing_cadet=existing_cadet, new_cadet=new_cadet)


def modify_cadet_date_of_birth(
    interface: abstractInterface, existing_cadet: Cadet, new_date_of_birth: datetime.date
):
    new_cadet = copy(existing_cadet)
    new_cadet.date_of_birth = new_date_of_birth
    modify_cadet(interface=interface, existing_cadet=existing_cadet, new_cadet=new_cadet)


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
