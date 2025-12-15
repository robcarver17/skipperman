from copy import copy



from app.backend.cadets.list_of_cadets import update_list_of_cadets, \
    get_sorted_list_of_cadets_from_raw_data
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.cadets import Cadet, ListOfCadets
from app.objects.membership_status import current_member


def set_all_current_members_to_temporary_unconfirmed(interface: abstractInterface):

    list_of_cadets = get_sorted_list_of_cadets_from_raw_data(object_store=interface.object_store)
    list_of_cadets.set_all_current_members_to_temporary_unconfirmed_status()
    update_list_of_cadets(
        interface=interface, updated_list_of_cadets=list_of_cadets
    )



def confirm_cadet_is_member(interface: abstractInterface, cadet: Cadet):
    new_cadet = copy(cadet)
    new_cadet.membership_status = current_member
    interface.update(interface.object_store.data_api.data_list_of_cadets.modify_cadet, existing_cadet =cadet, new_cadet=new_cadet)



def set_all_temporary_unconfirmed_members_to_lapsed_and_return_list(
    interface: abstractInterface,
) -> ListOfCadets:
    list_of_cadets = get_sorted_list_of_cadets_from_raw_data(interface.object_store)
    lapsed_members = (
        list_of_cadets.set_all_temporary_unconfirmed_members_to_lapsed_and_return_list()
    )
    update_list_of_cadets(
        interface=interface, updated_list_of_cadets=list_of_cadets
    )

    return lapsed_members


def set_all_user_unconfirmed_members_to_non_members_and_return_list(
    interface: abstractInterface,
) -> ListOfCadets:
    list_of_cadets = get_sorted_list_of_cadets_from_raw_data(interface.object_store)
    lapsed_members = (
        list_of_cadets.set_all_user_unconfirmed_members_to_non_members_and_return_list()
    )
    update_list_of_cadets(
        interface=interface, updated_list_of_cadets=list_of_cadets
    )

    return lapsed_members
