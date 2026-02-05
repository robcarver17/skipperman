from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import (
    object_definition_for_list_of_groups,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.groups import ListOfGroups, Group


def add_new_sailing_group_given_name(
        interface: abstractInterface, name_of_entry_to_add: str
):
    try:
        interface.update(
            interface.object_store.data_api.data_list_of_groups.add_new_group,
            group_name = name_of_entry_to_add
        )
    except Exception as e:
        interface.log_error("Error: %s, when adding group %s" % (str(e), name_of_entry_to_add))


def modify_sailing_group(
        interface: abstractInterface, existing_object: Group, new_object: Group
):
    try:
        interface.update(interface.object_store.data_api.data_list_of_groups.modify_sailing_group,
            existing_group_id =existing_object.id,
        new_group = new_object
        )
    except Exception as e:
        interface.log_error("Error: %s, when modifying %s to %s" % (str(e), existing_object, new_object))

def get_group_with_id(    object_store: ObjectStore, group_id:str, default=arg_not_passed) -> Group:
    return object_store.get(
        object_store.data_api.data_list_of_groups.get_group_with_id,
        group_id=group_id,
        default=default

    )

def get_group_with_name(
    object_store: ObjectStore, group_name: str, default=arg_not_passed
) -> Group:
    return object_store.get(
        object_store.data_api.data_list_of_groups.get_group_with_name,
        group_name=group_name,
        default=default
    )


def get_list_of_groups(object_store: ObjectStore) -> ListOfGroups:
    return object_store.get(object_store.data_api.data_list_of_groups.read)


def update_list_of_groups(
    interface: abstractInterface, updated_list_of_groups: ListOfGroups
):
    interface.update(
        interface.object_store.data_api.data_list_of_groups.write,
        list_of_groups = updated_list_of_groups
    )


def order_list_of_groups(object_store: ObjectStore, list_of_groups: ListOfGroups):
    all_groups = get_list_of_groups(object_store)
    return all_groups.subset_from_list_of_ids_retaining_order(
        list_of_groups.list_of_ids
    )
