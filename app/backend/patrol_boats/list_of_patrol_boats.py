from app.data_access.store.object_store import ObjectStore
from app.objects.patrol_boats import ListOfPatrolBoats, PatrolBoat
from app.data_access.store.object_definitions import (
    object_definition_for_list_of_patrol_boats,
)


def add_new_patrol_boat(object_store: ObjectStore, name_of_entry_to_add: str):
    list_of_patrol_boats = get_list_of_patrol_boats(object_store)
    list_of_patrol_boats.add(name_of_entry_to_add)
    update_list_of_patrol_boats(
        object_store=object_store, updated_list_of_patrol_boats=list_of_patrol_boats
    )


def modify_patrol_boat(
    object_store: ObjectStore, existing_object: PatrolBoat, new_object: PatrolBoat
):
    list_of_patrol_boats = get_list_of_patrol_boats(object_store)
    list_of_patrol_boats.replace(
        existing_patrol_boat=existing_object, new_patrol_boat=new_object
    )
    try:
        list_of_patrol_boats.check_for_duplicated_names()
    except:
        raise Exception("Duplicate names")
    update_list_of_patrol_boats(
        object_store=object_store, updated_list_of_patrol_boats=list_of_patrol_boats
    )


def get_list_of_patrol_boats(object_store: ObjectStore) -> ListOfPatrolBoats:
    return object_store.get(object_definition_for_list_of_patrol_boats)


def update_list_of_patrol_boats(
    object_store: ObjectStore, updated_list_of_patrol_boats: ListOfPatrolBoats
):
    object_store.update(
        new_object=updated_list_of_patrol_boats,
        object_definition=object_definition_for_list_of_patrol_boats,
    )
