from app.objects.exceptions import arg_not_passed
from app.data_access.init_data import object_store as default_object_store
from app.data_access.store.object_definitions import object_definition_for_list_of_users
from app.data_access.store.object_store import ObjectStore
from app.objects.users_and_security import ListOfSkipperManUsers, SkipperManUser


def add_user(object_store: ObjectStore, user: SkipperManUser):
    list_of_users = get_list_of_users(object_store)
    list_of_users.add(user)
    update_list_of_users(object_store=object_store, list_of_users=list_of_users)


def delete_user_from_user_list(object_store: ObjectStore, username: str):
    list_of_users = get_list_of_users_could_be_empty(object_store)
    list_of_users.delete(username)
    update_list_of_users(object_store=object_store, list_of_users=list_of_users)


def already_in_list(object_store: ObjectStore, username: str) -> bool:
    list_of_users = get_list_of_users(object_store)
    return list_of_users.already_in_list(username=username)


def get_list_of_users(
    object_store: ObjectStore = arg_not_passed,
) -> ListOfSkipperManUsers:
    if object_store is arg_not_passed:
        object_store = default_object_store
    list_of_users = get_list_of_users_could_be_empty(object_store)

    return list_of_users.list_of_users()


def no_admin_users(object_store: ObjectStore):
    all_users = get_list_of_users(object_store)
    return not all_users.at_least_one_admin_user()


def get_list_of_users_could_be_empty(
    object_store: ObjectStore,
) -> ListOfSkipperManUsers:
    return object_store.get(object_definition_for_list_of_users)


def update_list_of_users(
    object_store: ObjectStore, list_of_users: ListOfSkipperManUsers
):
    object_store.update(
        object_definition=object_definition_for_list_of_users, new_object=list_of_users
    )
