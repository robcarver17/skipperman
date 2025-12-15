from typing import List

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.cadets import (
    ListOfCadets,
    Cadet,
)
from app.objects.utilities.cadet_matching_and_sorting import (
    sort_a_list_of_cadets,
    SORT_BY_SURNAME,
    SORT_BY_FIRSTNAME,
    SORT_BY_DOB_ASC,
    SORT_BY_DOB_DSC,
    get_list_of_similar_cadets,
    get_list_of_very_similar_cadets, SORT_BY_SIMILARITY_BOTH, sort_list_of_cadets_by_similarity,
)
from app.objects.utilities.exceptions import arg_not_passed


from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import (
    DEPRECATE_object_definition_for_list_of_cadets,
)
from app.data_access.configuration.configuration import (
    SIMILARITY_LEVEL_TO_WARN_NAME,
    SIMILARITY_LEVEL_TO_MATCH_VERY_SIMILAR_FIRST_NAMES,
)


def DEPRECATE_delete_cadet(interface: abstractInterface, cadet: Cadet, areyousure=False):
    if not areyousure:
        return

    list_of_cadets = get_sorted_list_of_cadets_from_raw_data(interface.object_store)
    list_of_cadets.pop_cadet(cadet)
    update_list_of_cadets(
        interface=interface, updated_list_of_cadets=list_of_cadets
    )
    interface.clear() ## move up to next level


def get_matching_cadet(object_store: ObjectStore, cadet: Cadet) -> Cadet:
    return object_store.get(object_store.data_api.data_list_of_cadets.get_matching_cadet, cadet=cadet)


def are_there_no_similar_cadets(
    object_store: ObjectStore,
    cadet: Cadet,
    name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME,
) -> bool:
    similar_cadets = get_list_of_similar_cadets_from_data(
        object_store=object_store, cadet=cadet, name_threshold=name_threshold
    )

    return len(similar_cadets) == 0


def get_list_of_very_similar_cadets_from_data(
    object_store: ObjectStore,
    cadet: Cadet,
    first_name_threshold=SIMILARITY_LEVEL_TO_MATCH_VERY_SIMILAR_FIRST_NAMES,
):
    list_of_cadets = get_sorted_list_of_cadets_from_raw_data(object_store)
    return get_list_of_very_similar_cadets(
        list_of_cadets, other_cadet=cadet, first_name_threshold=first_name_threshold
    )


def get_list_of_similar_cadets_from_data(
    object_store: ObjectStore,
    cadet: Cadet,
    name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME,
) -> list:
    list_of_cadets = DEPRECATE_get_list_of_cadets(object_store)
    return get_list_of_similar_cadets(
        list_of_cadets, other_cadet=cadet, name_threshold=name_threshold
    )


def get_cadet_from_list_of_cadets_given_str_of_cadet(
    object_store: ObjectStore, cadet_selected: str
) -> Cadet:
    list_of_cadets = DEPRECATE_get_list_of_cadets(object_store)
    list_of_cadets_as_str = get_list_of_cadets_as_str(
        list_of_cadets
    )  ## don't use stored version in case changes
    cadet_idx = list_of_cadets_as_str.index(cadet_selected)

    cadet = list_of_cadets[cadet_idx]

    return cadet


def get_cadet_from_list_of_cadets_given_name_of_cadet(
    object_store: ObjectStore, cadet_selected: str, default=arg_not_passed
) -> Cadet:
    list_of_cadets = DEPRECATE_get_list_of_cadets(object_store)
    cadet = list_of_cadets.matching_cadet_with_name(cadet_selected, default=default)
    return cadet


def get_cadet_from_id(object_store: ObjectStore, cadet_id: str) -> Cadet:
    cadet =  object_store.get(object_store.data_api.data_list_of_cadets.get_cadet_from_id, cadet_id = cadet_id)

    return cadet

def get_list_of_cadets_sorted_by_surname(object_store: ObjectStore) -> ListOfCadets:
    return get_sorted_list_of_cadets(object_store=object_store, sort_by=SORT_BY_SURNAME)


def get_list_of_cadets_sorted_by_first_name(object_store: ObjectStore) -> ListOfCadets:
    return get_sorted_list_of_cadets(
        object_store=object_store, sort_by=SORT_BY_FIRSTNAME
    )


def get_sorted_list_of_cadets(
    object_store: ObjectStore,
    sort_by: str = arg_not_passed,
    similar_cadet: Cadet = arg_not_passed,
    exclude_cadet: Cadet = arg_not_passed,
) -> ListOfCadets:
    master_list = DEPRECATE_get_list_of_cadets(object_store)

    list_of_cadets = sort_a_list_of_cadets(
        master_list=master_list, sort_by=sort_by, similar_cadet=similar_cadet
    )
    if exclude_cadet is not arg_not_passed:
        try:
            list_of_cadets.remove(exclude_cadet)
        except:
            pass

    return list_of_cadets


def get_list_of_cadets_as_str(list_of_cadets: ListOfCadets) -> List[str]:
    return [str(cadet) for cadet in list_of_cadets]


def DEPRECATE_get_list_of_cadets(object_store: ObjectStore) -> ListOfCadets:
    return object_store.DEPRECATE_get(DEPRECATE_object_definition_for_list_of_cadets)

def get_sorted_list_of_cadets_from_raw_data(object_store: ObjectStore, sort_by: str = arg_not_passed,
                                            exclude_cadet: Cadet = arg_not_passed,
                                            similar_cadet: Cadet = arg_not_passed
                                            ) -> ListOfCadets:

    list_of_cadets =  object_store.get(object_store.data_api.data_list_of_cadets.read, sort_by=sort_by,
                                       exclude_cadet=exclude_cadet)

    if sort_by in [arg_not_passed, SORT_BY_SURNAME, SORT_BY_FIRSTNAME, SORT_BY_DOB_ASC, SORT_BY_DOB_DSC]:
        return list_of_cadets ## sorting done in raw data for speed
    elif sort_by == SORT_BY_SIMILARITY_BOTH:
        if similar_cadet is arg_not_passed:
            raise Exception(
                "Need to pass cadet if sorting by similarity, sort order %s" % sort_by
            )
        return sort_list_of_cadets_by_similarity(list_of_cadets, other_cadet=similar_cadet)

    else:
        raise Exception("Sort order %s not known" % sort_by)


def update_list_of_cadets(
    interface: abstractInterface, updated_list_of_cadets: ListOfCadets
):
    interface.update(interface.object_store.data_api.data_list_of_cadets.write, list_of_cadets=updated_list_of_cadets)


all_sort_types = [SORT_BY_SURNAME, SORT_BY_FIRSTNAME, SORT_BY_DOB_ASC, SORT_BY_DOB_DSC]
