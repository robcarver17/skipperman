from typing import Dict
import random
import string

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.data_access.data import DEPRECATED_data
from app.objects.users_and_security import ListOfSkipperManUsers, SkipperManUser


def load_all_users()-> ListOfSkipperManUsers:
    return DEPRECATED_data.data_list_of_users.read()

def save_all_users(list_of_users: ListOfSkipperManUsers):
    return DEPRECATED_data.data_list_of_users.write(list_of_users)


def add_user(user: SkipperManUser):
    ## check uniqueness
    all_users = load_all_users()
    all_users.add(user)
    save_all_users(all_users)

def already_in_list(user: str):
    all_users = load_all_users()
    return all_users.already_in_list(user)


def delete_username_from_user_list(username:str):
    all_users = load_all_users()
    all_users.delete(username)
    save_all_users(all_users)


def  change_password_for_user(username: str, new_password: str):
    all_users = load_all_users()
    all_users.change_password_for_user(username, new_password=new_password)
    save_all_users(all_users)


def modify_user_group(username: str, new_group:str):
    all_users = load_all_users()
    all_users.modify_user_group(username, new_group=new_group)
    save_all_users(all_users)

def generate_reset_link(interface: abstractInterface, username: str):
    ## generate randomness
    new_password = get_random_string(15)
    change_password_for_user(username, new_password=new_password)
    url_list = interface.url_for_password_reset(username=username, new_password=new_password)
    print("Changed password for %s, link is %s" % (username, str(url_list)))
    return url_list


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str