from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.patrol_boats import ListOfPatrolBoats, PatrolBoat


def add_new_patrol_boat(interface: abstractInterface, name_of_entry_to_add: str):
    try:
        interface.update(
        interface.object_store.data_api.data_list_of_patrol_boats.add_new_patrol_boat,
        patrol_boat_name= name_of_entry_to_add
    )
    except Exception as e:
        interface.log_error("Error: %s when adding boat %s" % (str(e), name_of_entry_to_add))



def modify_patrol_boat(
        interface: abstractInterface, existing_object: PatrolBoat, new_object: PatrolBoat
):
    try:
        interface.update(
        interface.object_store.data_api.data_list_of_patrol_boats.modify_patrol_boat,
        existing_patrol_boat_id = existing_object.id,
        new_patrol_boat=new_object
    )
    except Exception as e:
        interface.log_error("Error: %s when updating boat %s" % (str(e), new_object))


def get_list_of_patrol_boats(object_store: ObjectStore) -> ListOfPatrolBoats:
    return object_store.get(
        object_store.data_api.data_list_of_patrol_boats.read
    )


def update_list_of_patrol_boats(
    interface: abstractInterface, updated_list_of_patrol_boats: ListOfPatrolBoats
):
    interface.update(
        interface.object_store.data_api.data_list_of_patrol_boats.write,
        list_of_boats = updated_list_of_patrol_boats
    )


def from_patrol_boat_name_to_boat(
    object_store: ObjectStore, boat_name: str
) -> PatrolBoat:
    patrol_boat_data = get_list_of_patrol_boats(object_store)
    return patrol_boat_data.boat_given_name(boat_name)


def get_patrol_boat_from_id(
    object_store: ObjectStore, boat_id: str, default=arg_not_passed
) -> PatrolBoat:
    patrol_boat_data = get_list_of_patrol_boats(object_store)
    return patrol_boat_data.boat_given_id(boat_id, default=default)
