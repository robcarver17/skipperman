import random
import string
from typing import List

from app.objects.constants import arg_not_passed

from app.data_access.storage_layer.api import DataLayer

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.data_access.data import DEPRECATED_data
from app.objects.users_and_security import ListOfSkipperManUsers, SkipperManUser


class UserData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def get_user_given_username(self, username: str) -> SkipperManUser:
        list_of_users = self.get_list_of_users()
        return list_of_users.get_user_given_username(username=username)

    def get_list_of_users(self) -> ListOfSkipperManUsers:
        list_of_users_could_be_empty = self.get_list_of_users_could_be_empty()
        return list_of_users_could_be_empty.list_of_users() ## will contain default if nothing else

    def get_list_of_users_could_be_empty(self) -> ListOfSkipperManUsers:
        return ListOfSkipperManUsers(self.data_api.get_list_of_users())

    def save_list_of_users(self, list_of_users: ListOfSkipperManUsers):
        self.data_api.save_list_of_users(list_of_users)


from app.data_access.data import data_api as default_data_api

def load_all_users(interface: abstractInterface = arg_not_passed)-> ListOfSkipperManUsers:
    if interface is arg_not_passed:
        data = default_data_api
    else:
        data = interface.data

    user_data = UserData(data)
    return user_data.get_list_of_users()

def save_all_users(list_of_users: ListOfSkipperManUsers, interface: abstractInterface = arg_not_passed):
    return DEPRECATED_data.data_list_of_users.write(list_of_users)


def add_user(user: SkipperManUser):
    ## check uniqueness
    all_users = load_all_users()
    all_users.add(user)
    save_all_users(all_users)

def already_in_list(user: str):
    all_users = load_all_users()
    return all_users.already_in_list(user)


def delete_username_from_user_list(username:str, interface: abstractInterface = arg_not_passed):
    all_users = load_all_users()
    all_users.delete(username)
    save_all_users(all_users)


def  change_password_for_user(username: str, new_password: str, interface: abstractInterface = arg_not_passed):

    all_users = load_all_users(interface)
    all_users.change_password_for_user(username, new_password=new_password)
    save_all_users(all_users)


def DEPRECATE_modify_user_group(username: str, new_group:str, interface: abstractInterface = arg_not_passed):
    all_users = load_all_users(interface)
    all_users.modify_user_group(username, new_group=new_group)
    save_all_users(all_users)

def generate_reset_link( username: str, interface: abstractInterface = arg_not_passed):
    ## generate randomness
    new_password = get_random_string(15)
    change_password_for_user(interface=interface, username=username, new_password=new_password)
    url_list = interface.url_for_password_reset(username=username, new_password=new_password)
    print("Changed password for %s, link is %s" % (username, str(url_list)))
    return url_list


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


SUPERUSER = "_superuser_"
def get_volunteer_id_of_logged_in_user_or_superuser(interface: abstractInterface) -> str:
    user = get_logged_in_skipperman_user(interface)

    if user.is_skipper_or_admin():
        return SUPERUSER
    else:
        return user.volunteer_id

def get_logged_in_skipperman_user(interface: abstractInterface) -> SkipperManUser:
    username = interface.get_current_logged_in_username()
    user_data = UserData(interface.data)

    return user_data.get_user_given_username(username)
