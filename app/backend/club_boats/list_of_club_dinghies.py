from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import (
    object_definition_for_list_of_club_dinghies,
)
from app.objects.club_dinghies import ListOfClubDinghies, ClubDinghy


def add_new_club_dinghy_given_string(
    object_store: ObjectStore, name_of_entry_to_add: str
):
    list_of_boats = get_list_of_boat_classes(object_store)
    list_of_boats.add(name_of_entry_to_add)
    update_list_of_boat_classes(
        object_store=object_store, updated_list_of_boat_classes=list_of_boats
    )


def modify_club_dinghy(
    object_store: ObjectStore, existing_object: ClubDinghy, new_object: ClubDinghy
):
    list_of_boats = get_list_of_boat_classes(object_store)
    list_of_boats.replace(
        existing_club_dinghy=existing_object, new_club_dinghy=new_object
    )
    try:
        list_of_boats.check_for_duplicated_names()
    except:
        raise Exception("Duplicated names")

    update_list_of_boat_classes(
        object_store=object_store, updated_list_of_boat_classes=list_of_boats
    )


def get_list_of_boat_classes(object_store: ObjectStore) -> ListOfClubDinghies:
    return object_store.get(object_definition_for_list_of_club_dinghies)


def update_list_of_boat_classes(
    object_store: ObjectStore, updated_list_of_boat_classes: ListOfClubDinghies
):
    object_store.update(
        new_object=updated_list_of_boat_classes,
        object_definition=object_definition_for_list_of_club_dinghies,
    )
