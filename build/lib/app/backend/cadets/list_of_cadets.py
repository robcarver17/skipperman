from typing import List

from app.objects.cadets import (
    ListOfCadets,
    Cadet,
    sort_a_list_of_cadets,
    SORT_BY_SURNAME,
)
from app.objects.exceptions import arg_not_passed


from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import (
    object_definition_for_list_of_cadets,
)


def get_matching_cadet(
    object_store: ObjectStore, cadet: Cadet, exact_match_required: bool = True
) -> Cadet:
    list_of_cadets = get_list_of_cadets(object_store)

    return list_of_cadets.matching_cadet(
        cadet=cadet, exact_match_required=exact_match_required
    )


def are_there_no_similar_cadets(object_store: ObjectStore, cadet: Cadet) -> bool:
    similar_cadets = get_list_of_similar_cadets(object_store=object_store, cadet=cadet)

    return len(similar_cadets) == 0


def get_list_of_similar_cadets(object_store: ObjectStore, cadet: Cadet) -> list:
    list_of_cadets = get_list_of_cadets(object_store)
    return list_of_cadets.similar_cadets(cadet)


def get_cadet_from_list_of_cadets_given_str_of_cadet(
    object_store: ObjectStore, cadet_selected: str
) -> Cadet:
    list_of_cadets = get_list_of_cadets(object_store)
    list_of_cadets_as_str = get_list_of_cadets_as_str(
        list_of_cadets
    )  ## don't use stored version in case changes
    cadet_idx = list_of_cadets_as_str.index(cadet_selected)

    return list_of_cadets[cadet_idx]


def get_cadet_from_id(object_store: ObjectStore, cadet_id: str) -> Cadet:
    list_of_cadets = get_list_of_cadets(object_store)
    return list_of_cadets.cadet_with_id(cadet_id)


def get_list_of_cadets_sorted_by_surname(object_store: ObjectStore) -> ListOfCadets:
    return get_sorted_list_of_cadets(object_store=object_store, sort_by=SORT_BY_SURNAME)


def get_sorted_list_of_cadets(
    object_store: ObjectStore, sort_by: str = arg_not_passed
) -> ListOfCadets:
    master_list = get_list_of_cadets(object_store)

    return sort_a_list_of_cadets(master_list=master_list, sort_by=sort_by)


def get_list_of_cadets_as_str(list_of_cadets: ListOfCadets) -> List[str]:
    return [str(cadet) for cadet in list_of_cadets]


def get_list_of_cadets(object_store: ObjectStore) -> ListOfCadets:
    return object_store.get(object_definition_for_list_of_cadets)


def update_list_of_cadets(
    object_store: ObjectStore, updated_list_of_cadets: ListOfCadets
):
    object_store.update(
        new_object=updated_list_of_cadets,
        object_definition=object_definition_for_list_of_cadets,
    )
