from werkzeug.security import generate_password_hash

from app.data_access.configuration.configuration import HOMEPAGE
from app.data_access.init_data import object_store as default_object_store
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.users_and_security import ListOfSkipperManUsers, SkipperManUser, get_random_string
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.volunteers import Volunteer
from app.web.html.url_define import LINK_LOGIN




def already_in_list(object_store: ObjectStore, username: str) -> bool:
    list_of_users = get_list_of_users(object_store)
    return list_of_users.already_in_list(username=username)


def get_list_of_users(
    object_store: ObjectStore
) -> ListOfSkipperManUsers:

    list_of_users = get_list_of_users_could_be_empty(object_store)

    return list_of_users.list_of_users()


def list_of_admin_users(object_store: ObjectStore) -> ListOfSkipperManUsers:
    all_users = get_list_of_users(object_store)
    return all_users.list_of_admin_users()


def get_list_of_users_could_be_empty(
    object_store: ObjectStore,
) -> ListOfSkipperManUsers:
    return object_store.get(
        object_store.data_api.data_list_of_users.read
    )


def change_password_for_user(
      username: str, new_password: str, interface: abstractInterface = arg_not_passed
):
    password_hash = generate_password_hash(new_password)
    if interface is arg_not_passed:
        ## If called from change password web page
        change_password_for_user_from_home_page(
            username=username, new_password_hash=password_hash
        )
    else:
        change_password_for_user_from_inside_SM(interface=interface,
                                                username=username,
                                                new_password_hash = password_hash)


def change_password_for_user_from_home_page(
        username: str, new_password_hash: str
):
    object_store = default_object_store

    ## UNIQUELY READ ONLY CAN'T AFFECT PASSWORD CHANGES
    object_store.data_api.data_list_of_users.change_password_for_user(username=username, new_password_hash=new_password_hash)

def change_password_for_user_from_inside_SM(
        interface: abstractInterface, username: str, new_password_hash: str
):
    ## USES STANDARD INTERFACE SO READ ONLY CAN HAPPEN
    interface.update(
        interface.object_store.data_api.data_list_of_users.change_password_for_user,
        username=username,
        new_password_hash = new_password_hash
    )

def add_user(interface: abstractInterface, user: SkipperManUser):
    interface.update(
        interface.object_store.data_api.data_list_of_users.add_user,
        user=user
    )


def delete_user_from_user_list(interface: abstractInterface, username: str):
    interface.update(
        interface.object_store.data_api.data_list_of_users.delete_user,
        username=username
    )

def modify_user_group(interface: abstractInterface, username: str, new_group: str):
    interface.update(
        interface.object_store.data_api.data_list_of_users.modify_user_group,
        username=username,
        new_group = new_group
    )


def modify_volunteer_for_user(
    interface: abstractInterface, username: str, volunteer: Volunteer
):
    interface.update(
        interface.object_store.data_api.data_list_of_users.modify_volunteer_for_user,
        username=username,
        volunteer_id = volunteer.id
    )


def generate_reset_message(interface: abstractInterface, username: str) -> str:
    ## generate randomness
    new_password = get_random_string(6)
    change_password_for_user(
        interface=interface, username=username, new_password=new_password
    )
    return (
        "Message to send to user: Login with %s/%s/?username=%s&password=%s AND THEN CHANGE YOUR PASSWORD!!!"
        % (
            HOMEPAGE,
            LINK_LOGIN,
            username,
            new_password,
        )
    )
