

from app.data_access.configuration.configuration import HOMEPAGE

from app.objects.constants import arg_not_passed

from app.data_access.storage_layer.api import DataLayer

from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.objects.users_and_security import ListOfSkipperManUsers, SkipperManUser, get_random_string


class UserData:
    def __init__(self, data_api: DataLayer):
        self.data_api = data_api

    def already_in_list(self, username: str):
        list_of_users = self.get_list_of_users()
        return list_of_users.already_in_list(username=username)

    def modify_user_group(self, username: str, new_group: str):
        list_of_users = self.get_list_of_users()
        list_of_users.modify_user_group(username=username, new_group=new_group)
        self.save_list_of_users(list_of_users)

    def modify_volunteer_id_for_user(self, username: str, new_volunteer_id: str):
        list_of_users = self.get_list_of_users()
        list_of_users.modify_volunteer_id(username=username, new_id=new_volunteer_id)
        self.save_list_of_users(list_of_users)

    def change_password_for_user(self, username: str, new_password: str):
        list_of_users = self.get_list_of_users()
        list_of_users.change_password_for_user(username, new_password=new_password)
        self.save_list_of_users(list_of_users)

    def add_user(self, user: SkipperManUser):
        list_of_users = self.get_list_of_users()
        list_of_users.add(user)
        self.save_list_of_users(list_of_users)

    def delete_username_from_user_list(self, username: str):
        list_of_users = self.get_list_of_users()
        list_of_users.delete(username)
        self.save_list_of_users(list_of_users)

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

def regenerate_password_hash(user: SkipperManUser, user_entered_password: str, interface: abstractInterface = arg_not_passed):
    user_data = UserData(interface.data)
    user_data.change_password_for_user(username=user.username, new_password=user_entered_password)

def add_user(interface: abstractInterface, user: SkipperManUser):
    user_data =UserData(interface.data)
    user_data.add_user(user)

def already_in_list(interface: abstractInterface, username: str) -> bool:
    user_data =UserData(interface.data)
    return user_data.already_in_list(username)


def  change_password_for_user(username: str, new_password: str, interface: abstractInterface = arg_not_passed):
    if interface is arg_not_passed:
        interface = abstractInterface(default_data_api)

    user_data = UserData(interface.data)
    user_data.change_password_for_user(username=username, new_password=new_password)



def modify_user_group(username: str, new_group:str, interface: abstractInterface):
    user_data = UserData(interface.data)
    user_data.modify_user_group(username=username, new_group=new_group)

def modify_volunteer_id_for_user(username: str, new_volunteer_id:str, interface: abstractInterface):
    user_data = UserData(interface.data)
    user_data.modify_volunteer_id_for_user(username=username, new_volunteer_id=new_volunteer_id)



def generate_reset_message(username: str, interface: abstractInterface) -> str:
    ## generate randomness
    new_password = get_random_string(6)
    change_password_for_user(interface=interface, username=username, new_password=new_password)
    return "Message: Login to %s using username: %s password: %s" % (HOMEPAGE, username, new_password)




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
