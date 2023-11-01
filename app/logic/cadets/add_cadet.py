from app.objects.cadets import Cadet, is_cadet_age_surprising
from app.data_access.api.generic_api import GenericDataApi
from app.data_access.configuration.configuration import (
    SIMILARITY_LEVEL_TO_WARN_DATE,
    SIMILARITY_LEVEL_TO_WARN_NAME,
)

def verify_cadet_and_warn(data: GenericDataApi, cadet: Cadet)->str:
    warn_text = ""
    if len(cadet.surname)<4:
        warn_text+= "Surname seems too short. "
    if len(cadet.first_name)<4:
        warn_text+="First name seems too short. "
    if is_cadet_age_surprising(cadet):
        warn_text+="Cadet seems awfully old or young."
    warn_text+=warning_for_similar_cadets(data=data, cadet=cadet)

    if len(warn_text)>0:
        warn_text="DOUBLE CHECK BEFORE ADDING: "+warn_text

    return warn_text

def warning_for_similar_cadets(data: GenericDataApi, cadet: Cadet) -> str:
    existing_cadets = data.data_list_of_cadets.read()
    similar_cadets = existing_cadets.similar_cadets(
        cadet,
        name_threshold=SIMILARITY_LEVEL_TO_WARN_NAME,
        dob_threshold=SIMILARITY_LEVEL_TO_WARN_DATE,
    )

    if len(similar_cadets) > 0:
        similar_cadets_str = ", ".join([str(other_cadet) for other_cadet in similar_cadets])
        ## Some similar cadets, let's see if it's a match
        return "Following cadets look awfully similar:\n %s" % similar_cadets_str
    else:
        return ""

def add_new_verified_cadet(cadet: Cadet, data: GenericDataApi):
    data.data_list_of_cadets.add(cadet)