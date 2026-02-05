from app.data_access.store.object_store import ObjectStore

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.boat_classes import ListOfBoatClasses, BoatClass, no_boat_class


def get_boat_class_from_name(
    object_store: ObjectStore, boat_class_name: str, default=no_boat_class
) -> BoatClass:
    list_of_boats = get_list_of_boat_classes(object_store)
    return list_of_boats.get_boat_with_name(boat_class_name, default=default)

def add_new_boat_class_given_string(
    interface: abstractInterface, name_of_entry_to_add: str
):
    interface.update(interface.object_store.data_api.data_list_of_dinghies.add_new_boat_class_given_string,
                       name_of_entry_to_add=name_of_entry_to_add)


def modify_boat_class(
    interface: abstractInterface,  existing_object: BoatClass, new_object: BoatClass
):
    interface.update(interface.object_store.data_api.data_list_of_dinghies.modify_boat_class,
                       existing_boat =existing_object,
                     new_boat = new_object)



def get_list_of_boat_classes(object_store: ObjectStore) -> ListOfBoatClasses:
    return object_store.get(object_store.data_api.data_list_of_dinghies.read)


def update_list_of_boat_classes(
    interface: abstractInterface, updated_list_of_boat_classes: ListOfBoatClasses
):
    interface.update(interface.object_store.data_api.data_list_of_dinghies.write,
                        list_of_boats = updated_list_of_boat_classes)
