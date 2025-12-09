from app.data_access.store.object_store import ObjectStore

from app.backend.cadets.list_of_cadets import get_list_of_cadets, update_list_of_cadets

from app.objects.cadets import Cadet, ListOfCadets


def set_all_current_members_to_temporary_unconfirmed(object_store: ObjectStore):
    list_of_cadets = get_list_of_cadets(object_store)
    list_of_cadets.set_all_current_members_to_temporary_unconfirmed_status()
    update_list_of_cadets(
        object_store=object_store, updated_list_of_cadets=list_of_cadets
    )


def confirm_cadet_is_member(object_store: ObjectStore, cadet: Cadet):

    list_of_cadets = get_list_of_cadets(object_store)
    list_of_cadets.confirm_cadet_as_member(cadet)
    update_list_of_cadets(
        object_store=object_store, updated_list_of_cadets=list_of_cadets
    )



def set_all_temporary_unconfirmed_members_to_lapsed_and_return_list(
    object_store: ObjectStore,
) -> ListOfCadets:
    list_of_cadets = get_list_of_cadets(object_store)
    lapsed_members = (
        list_of_cadets.set_all_temporary_unconfirmed_members_to_lapsed_and_return_list()
    )
    update_list_of_cadets(
        object_store=object_store, updated_list_of_cadets=list_of_cadets
    )

    return lapsed_members


def set_all_user_unconfirmed_members_to_non_members_and_return_list(
    object_store: ObjectStore,
) -> ListOfCadets:
    list_of_cadets = get_list_of_cadets(object_store)
    lapsed_members = (
        list_of_cadets.set_all_user_unconfirmed_members_to_non_members_and_return_list()
    )
    update_list_of_cadets(
        object_store=object_store, updated_list_of_cadets=list_of_cadets
    )

    return lapsed_members
