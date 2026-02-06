from typing import List, Union

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import Cadet

from app.data_access.store.object_store import ObjectStore
from app.objects.composed.cadets_with_qualifications import (
    QualificationsForCadet, DictOfQualificationsForCadets,
)
from app.objects.qualifications import Qualification, NoQualifications


def apply_qualification_to_cadet(
    interface: abstractInterface,
    cadet: Cadet,
    qualification: Qualification,
    awarded_by: str,
):
    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_qualifications.apply_qualification_to_cadet,
        cadet_id=cadet.id,
    qualification_id= qualification.id,
    awarded_by=awarded_by
    )

def remove_qualification_from_cadet(
    interface: abstractInterface, cadet: Cadet, qualification: Qualification
):
    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_qualifications.remove_qualification_from_cadet,
        cadet_id=cadet.id,
    qualification_id= qualification.id,
    )

def delete_all_qualifications_for_cadet(
    interface: abstractInterface, cadet: Cadet, areyousure=False
):
    if not areyousure:
        return

    interface.update(
        interface.object_store.data_api.data_list_of_cadets_with_qualifications.delete_all_qualifications_for_cadet,
        cadet_id=cadet.id,
    )


def name_of_highest_qualification_for_cadet(
    object_store: ObjectStore, cadet: Cadet
) -> str:
    highest_qualification = highest_qualification_for_cadet(object_store, cadet=cadet)
    if highest_qualification is NoQualifications:
        return "None"

    return highest_qualification.name




def sorted_list_of_named_qualifications_for_cadet(
    object_store: ObjectStore, cadet: Cadet
) -> List[str]:
    return object_store.get(object_store.data_api.data_list_of_cadets_with_qualifications.sorted_list_of_named_qualifications_for_cadet,
                            cadet_id=cadet.id)



def get_list_of_qualifications_for_cadet(
    object_store: ObjectStore, cadet: Cadet
) -> QualificationsForCadet:
    return object_store.get(object_store.data_api.data_list_of_cadets_with_qualifications.get_dict_of_qualifications_for_all_cadets,
                            cadet=cadet)


def get_dict_of_qualifications_for_all_cadets(
    object_store: ObjectStore,
) -> DictOfQualificationsForCadets:
    return object_store.get(object_store.data_api.data_list_of_cadets_with_qualifications.get_dict_of_qualifications_for_all_cadets)


def highest_qualification_for_cadet(
    object_store: ObjectStore, cadet: Cadet
) -> Union[object, Qualification]:
    return object_store.get(
        object_store.data_api.data_list_of_cadets_with_qualifications.highest_qualification_for_cadet, cadet=cadet)

