from dataclasses import dataclass
from enum import Enum

from werkzeug.security import generate_password_hash, check_password_hash

from app.objects.generic import GenericSkipperManObject, GenericListOfObjects

UserGroup = Enum('UserGroup', ['admin','skipper','instructor', 'public'])
ADMIN_GROUP = UserGroup.admin
SKIPPER_GROUP = UserGroup.skipper
INSTRUCTOR_GROUP = UserGroup.instructor
PUBLIC_GROUP = UserGroup.public

ALL_GROUPS = [ADMIN_GROUP, SKIPPER_GROUP, INSTRUCTOR_GROUP, PUBLIC_GROUP]



@dataclass
class SkipperManUser(GenericSkipperManObject):
    username: str
    password_hash: str
    group: UserGroup
    email_address: str
    volunteer_id: str

    @classmethod
    def create(cls, username: str, password: str, group: UserGroup, email_address: str, volunteer_id: str):
        hash = generate_password_hash(password)
        return cls(username=username, password_hash=hash, group=group,email_address=email_address, volunteer_id=volunteer_id)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
#
#


NO_VOLUNTEER_ID = '-1'
default_admin_user_if_none_defined = SkipperManUser('default', generate_password_hash('default'), group=ADMIN_GROUP, email_address='',
                                                    volunteer_id=NO_VOLUNTEER_ID)
default_user_if_not_logged_in = SkipperManUser('public', 'public', group=PUBLIC_GROUP,email_address='', volunteer_id=NO_VOLUNTEER_ID)

class ListOfSkipperManUsers(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return SkipperManUser

    def already_in_list(self, username: str) -> bool:
        existing_usernames = self.list_of_usernames_excludes_default()
        return username in existing_usernames


    def add(self, user: SkipperManUser):
        try:
            assert not self.already_in_list(user.username)
        except:
            raise Exception("Can't have duplicate usernames")

        self.append(user)

    def change_password_for_user(self, username: str, new_password: str):
        user = self.get_user_given_username(username)
        user.password_hash = generate_password_hash(new_password)

    def modify_user_group(self, username: str, new_group:str):
        user = self.get_user_given_username(username)
        user.group = new_group

    def delete(self, username: str):
        try:
            assert self.already_in_list(username)
        except:
            raise Exception("can't delete non existent user")

        user = self.get_user_given_username(username)
        self.remove(user)

    def get_user_given_username(self, username: str) -> SkipperManUser:
        users = self.list_of_users()
        matching = [user for user in users if user.username ==username]
        if len(matching)>1:
            raise Exception("Can't have duplicate users")
        if len(matching)==0:
            return default_user_if_not_logged_in

        return matching[0]


    def list_of_usernames_excludes_default(self):
        return [user.username for user in self]

    def list_of_users(self):
        if len(self)>0:
            return self
        else:
            return [default_admin_user_if_none_defined, default_user_if_not_logged_in]

    def at_least_one_admin_user(self):
        ## doesn't use list of users
        admin = [user for user in self if user.group ==ADMIN_GROUP]
        return len(admin)>0



