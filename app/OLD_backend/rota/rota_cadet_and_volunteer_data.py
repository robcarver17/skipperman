from app.OLD_backend.volunteers.volunteers import get_dict_of_existing_skills

from app.data_access.store.DEPRECATE_ad_hoc_cache import AdHocCache
from app.objects.volunteers import Volunteer


def get_str_dict_skills(cache: AdHocCache, volunteer: Volunteer):
    dict_of_skills = cache.get_from_cache(
        get_dict_of_existing_skills, volunteer=volunteer
    )
    if dict_of_skills.empty():
        return "No skills recorded"

    return dict_of_skills.skills_held_as_str()
