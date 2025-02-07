from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import (
    object_definition_for_list_of_boat_classes,
)
from app.objects.boat_classes import ListOfBoatClasses, BoatClass, no_boat_class


def get_boat_class_from_name(
    object_store: ObjectStore, boat_class_name: str, default=no_boat_class
) -> BoatClass:
    list_of_boat_classes = get_list_of_boat_classes(object_store)
    return list_of_boat_classes.boat_class_given_name(boat_class_name, default=default)


def add_new_boat_class_given_string(
    object_store: ObjectStore, name_of_entry_to_add: str
):
    list_of_boats = get_list_of_boat_classes(object_store)
    list_of_boats.add(name_of_entry_to_add)
    update_list_of_boat_classes(
        object_store=object_store, updated_list_of_boat_classes=list_of_boats
    )


def modify_boat_class(
    object_store: ObjectStore, existing_object: BoatClass, new_object: BoatClass
):
    list_of_boats = get_list_of_boat_classes(object_store)
    list_of_boats.replace(existing_boat_class=existing_object, new_boat_class=new_object)
    try:
        list_of_boats.check_for_duplicated_names()
    except:
        raise Exception("Duplicated names - classes must be unique")

    update_list_of_boat_classes(
        object_store=object_store, updated_list_of_boat_classes=list_of_boats
    )


def get_list_of_boat_classes(object_store: ObjectStore) -> ListOfBoatClasses:
    return object_store.get(object_definition_for_list_of_boat_classes)


def update_list_of_boat_classes(
    object_store: ObjectStore, updated_list_of_boat_classes: ListOfBoatClasses
):
    object_store.update(
        new_object=updated_list_of_boat_classes,
        object_definition=object_definition_for_list_of_boat_classes,
    )
