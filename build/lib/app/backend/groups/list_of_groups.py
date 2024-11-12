from app.data_access.store.object_store import ObjectStore

from app.data_access.store.object_definitions import (
    object_definition_for_list_of_groups,
)
from app.objects.groups import ListOfGroups, Group


def add_new_sailing_group_given_name(
    object_store: ObjectStore, name_of_entry_to_add: str
):
    list_of_groups = get_list_of_groups(object_store)
    list_of_groups.add(name_of_entry_to_add)
    update_list_of_groups(
        object_store=object_store, updated_list_of_groups=list_of_groups
    )


def modify_sailing_group(
    object_store: ObjectStore, existing_object: Group, new_object: Group
):
    list_of_groups = get_list_of_groups(object_store)
    list_of_groups.replace(existing_group=existing_object, new_group=new_object)
    try:
        list_of_groups.check_for_duplicated_names()
    except Exception:
        raise Exception("Duplicate names - each group must have a unique name")

    update_list_of_groups(
        object_store=object_store, updated_list_of_groups=list_of_groups
    )


def get_list_of_groups(object_store: ObjectStore) -> ListOfGroups:
    return object_store.get(object_definition_for_list_of_groups)


def update_list_of_groups(
    object_store: ObjectStore, updated_list_of_groups: ListOfGroups
):
    object_store.update(
        new_object=updated_list_of_groups,
        object_definition=object_definition_for_list_of_groups,
    )


def order_list_of_groups(object_store: ObjectStore, list_of_groups: ListOfGroups):
    all_groups = get_list_of_groups(object_store)
    return ListOfGroups.subset_from_list_of_ids(all_groups, list_of_groups.list_of_ids)
