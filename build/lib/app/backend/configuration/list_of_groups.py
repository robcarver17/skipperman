from app.data_access.store.object_store import ObjectStore


from app.data_access.store.object_definitions import object_definition_for_list_of_groups
from app.objects.groups import ListOfGroups


def get_list_of_groups(object_store: ObjectStore) -> ListOfGroups:
    return object_store.get(object_definition_for_list_of_groups )

def update_list_of_boat_classes(object_store: ObjectStore, updated_list_of_groups: ListOfGroups):
    object_store.update(new_object=updated_list_of_groups, object_definition=object_definition_for_list_of_groups)

