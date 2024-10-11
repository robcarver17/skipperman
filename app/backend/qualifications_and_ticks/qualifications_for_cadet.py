from typing import List

from app.objects.cadets import Cadet

from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import object_definition_for_dict_of_qualifications_for_cadets
from app.objects.composed.cadets_with_qualifications import DictOfQualificationsForCadets, QualificationsForCadet

def sorted_list_of_named_qualifications_for_cadet(
    object_store: ObjectStore, cadet: Cadet
) -> List[str]:
    list_of_qualifications_for_cadet = get_list_of_qualifications_for_cadet(object_store=object_store, cadet=cadet)
    list_of_qualifications_for_cadet.sort_by_qualification_order()
    list_of_names = [
        qualification.name
        for qualification in list_of_qualifications_for_cadet
    ]

    return list_of_names

def get_list_of_qualifications_for_cadet(object_store: ObjectStore, cadet: Cadet) -> QualificationsForCadet:
    dict_of_qualifications_for_all_cadets = get_dict_of_qualifications_for_all_cadets(object_store)

    return dict_of_qualifications_for_all_cadets.qualifications_for_cadet(cadet)

def get_dict_of_qualifications_for_all_cadets(object_store: ObjectStore) -> DictOfQualificationsForCadets:
    return object_store.get(object_definition_for_dict_of_qualifications_for_cadets)