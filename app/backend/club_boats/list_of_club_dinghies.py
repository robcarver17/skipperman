from app.data_access.store.object_store import ObjectStore

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.club_dinghies import ListOfClubDinghies, ClubDinghy
from app.objects.utilities.exceptions import arg_not_passed


def get_club_dinghy_from_id(
    object_store: ObjectStore, club_dinghy_id: str, default=arg_not_passed
) -> ClubDinghy:
    return \
        object_store.data_api.data_List_of_club_dinghies.get_club_dinghy_from_id(
        club_dinghy_id=club_dinghy_id,
        default = default
    )


def get_club_dinghy_with_name(
    object_store: ObjectStore, boat_name: str, default=arg_not_passed
) -> ClubDinghy:
    return \
        object_store.data_api.data_List_of_club_dinghies.get_club_dinghy_with_name(
        dinghy_name=boat_name,
        default = default
    )


def add_new_club_dinghy_given_string(
    interface: abstractInterface,  name_of_entry_to_add: str
):
    try:
        interface.update(
            interface.object_store.data_api.data_List_of_club_dinghies.add_new_club_dinghy_with_name,
            dinghy_name=name_of_entry_to_add
        )
    except Exception as e:
        interface.log_error("Can't add club dinghy %s, %s" % (name_of_entry_to_add, str(e)))

    club_dinghy_id = interface.object_store.data_api.data_List_of_club_dinghies.get_club_dinghy_with_name(name_of_entry_to_add).id
    try:
        interface.update(
            interface.object_store.data_api.data_List_of_club_dinghy_limits.add_generic_limit_for_club_dinghy,
            club_dinghy_id=club_dinghy_id
        )
    except Exception as e:
        interface.log_error("Problem %s adding limit for %s" % (str(e), name_of_entry_to_add))


def modify_club_dinghy(
    interface: abstractInterface, existing_object: ClubDinghy, new_object: ClubDinghy
):
    try:
        interface.update(
            interface.object_store.data_api.data_List_of_club_dinghies.modify_club_dinghy,
            existing_club_dinghy_id = existing_object.id,
            new_club_dinghy = new_object
        )
    except Exception as e:
        interface.log_error("Can't modify club dinghy %s, %s" % (str(existing_object), str(e)))



def get_list_of_club_dinghies(object_store: ObjectStore) -> ListOfClubDinghies:
    return object_store.get(object_store.data_api.data_List_of_club_dinghies.read)


def update_list_of_club_dinghies(
    interface: abstractInterface, updated_list_of_club_dinghies: ListOfClubDinghies
):
    interface.update(
        interface.object_store.data_api.data_List_of_club_dinghies.write,
        list_of_boats = updated_list_of_club_dinghies
    )

def get_list_of_visible_club_dinghies(object_store: ObjectStore):

    return object_store.get(object_store.data_api.data_List_of_club_dinghies.get_list_of_visible_club_dinghies)

    #visible_dinghies = ListOfClubDinghies(
    #    [dinghy for dinghy in visible_dinghies if len(dinghy.name) > 0]
    #)  ##FIXME exists because of weird bug

    #return visible_dinghies
