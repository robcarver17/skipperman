from app.objects.volunteers import Volunteer

from app.backend.security.list_of_users import get_list_of_users, update_list_of_users

from app.data_access.store.object_store import ObjectStore

from app.data_access.configuration.configuration import HOMEPAGE
from app.data_access.data import object_store as default_object_store
from app.objects.exceptions import arg_not_passed
from app.objects.users_and_security import get_random_string


def change_password_for_user(
    username: str, new_password: str, object_store: ObjectStore = arg_not_passed
):
    if object_store is arg_not_passed:
        ## If called from change password web page
        object_store = default_object_store

    list_of_users = get_list_of_users(object_store)
    list_of_users.change_password_for_user(username, new_password=new_password)
    update_list_of_users(object_store=object_store, list_of_users=list_of_users)


def modify_user_group(username: str, new_group: str, object_store: ObjectStore):
    list_of_users = get_list_of_users(object_store)
    list_of_users.modify_user_group(username=username, new_group=new_group)
    update_list_of_users(object_store=object_store, list_of_users=list_of_users)


def modify_volunteer_for_user(
    username: str, volunteer: Volunteer, object_store: ObjectStore
):
    list_of_users = get_list_of_users(object_store)
    list_of_users.modify_volunteer_for_user(username=username, volunteer=volunteer)
    update_list_of_users(object_store=object_store, list_of_users=list_of_users)


def generate_reset_message(username: str, object_store: ObjectStore) -> str:
    ## generate randomness
    new_password = get_random_string(6)
    change_password_for_user(
        object_store=object_store, username=username, new_password=new_password
    )
    return "Message: Login to %s using username: %s password: %s" % (
        HOMEPAGE,
        username,
        new_password,
    )
