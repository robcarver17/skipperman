from typing import Dict

from app.data_access.data import data
from app.objects.users_and_security import ListOfSkipperManUsers, SkipperManUser


def load_all_users()-> ListOfSkipperManUsers:
    return data.data_list_of_users.read()

def save_all_users(list_of_users: ListOfSkipperManUsers):
    return data.data_list_of_users.write(list_of_users)


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
