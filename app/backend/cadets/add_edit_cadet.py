from app.data_access.data_layer.object_store import ObjectStore

from app.backend.cadets.list_of_cadets import get_list_of_similar_cadets, get_list_of_cadets, update_list_of_cadets
from app.objects.cadets import Cadet, is_cadet_age_surprising

def add_new_verified_cadet(object_store: ObjectStore, cadet: Cadet) -> Cadet:
    list_of_cadets = get_list_of_cadets(object_store)
    cadet = list_of_cadets.add(cadet)
    update_list_of_cadets(object_store=object_store, updated_list_of_cadets=list_of_cadets)

    return cadet



def verify_cadet_and_return_warnings(object_store: ObjectStore, cadet: Cadet) -> str:
    print("Checking %s" % cadet)
    warn_text = ""
    if len(cadet.surname) < 4:
        warn_text += "Surname seems too short. "
    if len(cadet.first_name) < 4:
        warn_text += "First name seems too short. "
    if is_cadet_age_surprising(cadet):
        warn_text += "Cadet seems awfully old or young."
    warn_text += warning_for_similar_cadets(cadet=cadet, object_store=object_store)

    if len(warn_text) > 0:
        warn_text = "DOUBLE CHECK BEFORE ADDING: " + warn_text

    return warn_text


def warning_for_similar_cadets(object_store: ObjectStore, cadet: Cadet) -> str:
    similar_cadets = get_list_of_similar_cadets(object_store=object_store, cadet=cadet)

    if len(similar_cadets) > 0:
        similar_cadets_str = ", ".join(
            [str(other_cadet) for other_cadet in similar_cadets]
        )
        return "Following cadets look awfully similar:\n %s" % similar_cadets_str
    else:
        return ""
