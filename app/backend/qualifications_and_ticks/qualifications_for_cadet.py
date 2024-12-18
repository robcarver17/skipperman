from typing import List, Union

from app.objects.cadets import Cadet

from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import (
    object_definition_for_dict_of_qualifications_for_cadets,
)
from app.objects.composed.cadets_with_qualifications import (
    DictOfQualificationsForCadets,
    QualificationsForCadet,
)
from app.objects.qualifications import Qualification


def apply_qualification_to_cadet(
    object_store: ObjectStore, cadet: Cadet, qualification: Qualification
):
    dict_of_qualifications_for_all_cadets = get_dict_of_qualifications_for_all_cadets(
        object_store
    )
    dict_of_qualifications_for_all_cadets.apply_qualification_to_cadet(
        cadet=cadet, qualification=qualification
    )
    update_dict_of_qualifications_for_all_cadets(
        object_store=object_store,
        dict_of_qualifications=dict_of_qualifications_for_all_cadets,
    )


def remove_qualification_from_cadet(
    object_store: ObjectStore, cadet: Cadet, qualification: Qualification
):
    dict_of_qualifications_for_all_cadets = get_dict_of_qualifications_for_all_cadets(
        object_store
    )
    dict_of_qualifications_for_all_cadets.remove_qualification_from_cadet(
        cadet=cadet, qualification=qualification
    )
    update_dict_of_qualifications_for_all_cadets(
        object_store=object_store,
        dict_of_qualifications=dict_of_qualifications_for_all_cadets,
    )

class NoQualifications:
    def __repr__(self):
        return "No qualifications"

no_qualifications = NoQualifications()

def highest_qualification_for_cadet(object_store: ObjectStore, cadet: Cadet) -> Union[object, Qualification]:
    list_of_qualifications_for_cadet = get_list_of_qualifications_for_cadet(
        object_store=object_store, cadet=cadet
    )
    if len(list_of_qualifications_for_cadet)==0:
        return no_qualifications

    list_of_qualifications_for_cadet.sort_by_qualification_order()

    return list_of_qualifications_for_cadet[-1]


def sorted_list_of_named_qualifications_for_cadet(
    object_store: ObjectStore, cadet: Cadet
) -> List[str]:
    list_of_qualifications_for_cadet = get_list_of_qualifications_for_cadet(
        object_store=object_store, cadet=cadet
    )
    list_of_qualifications_for_cadet.sort_by_qualification_order()
    list_of_names = [
        qualification.name for qualification in list_of_qualifications_for_cadet
    ]

    return list_of_names


def get_list_of_qualifications_for_cadet(
    object_store: ObjectStore, cadet: Cadet
) -> QualificationsForCadet:
    dict_of_qualifications_for_all_cadets = get_dict_of_qualifications_for_all_cadets(
        object_store
    )

    return dict_of_qualifications_for_all_cadets.qualifications_for_cadet(cadet)


def get_dict_of_qualifications_for_all_cadets(
    object_store: ObjectStore,
) -> DictOfQualificationsForCadets:
    return object_store.get(object_definition_for_dict_of_qualifications_for_cadets)


def update_dict_of_qualifications_for_all_cadets(
    object_store: ObjectStore, dict_of_qualifications: DictOfQualificationsForCadets
):
    object_store.update(
        object_definition=object_definition_for_dict_of_qualifications_for_cadets,
        new_object=dict_of_qualifications,
    )