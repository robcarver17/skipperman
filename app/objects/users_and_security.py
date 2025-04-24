from random import choice
import string
from dataclasses import dataclass
from enum import Enum

from app.objects.volunteers import Volunteer
from werkzeug.security import generate_password_hash, check_password_hash

from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,
    get_unique_object_with_attr_in_list,
)
from app.objects.utilities.generic_objects import GenericSkipperManObject

UserGroup = Enum("UserGroup", ["admin", "skipper", "instructor", "public"])
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
    email_address: str  ## not currently used
    volunteer_id: str

    @classmethod
    def create(
        cls,
        username: str,
        password: str,
        group: UserGroup,
        email_address: str,
        volunteer: Volunteer,
    ):
        hash = generate_password_hash(password)
        return cls(
            username=username,
            password_hash=hash,
            group=group,
            email_address=email_address,
            volunteer_id=volunteer.id,
        )

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_skipper_or_admin(self):
        return self.group in [SKIPPER_GROUP, ADMIN_GROUP]


#
#


NO_VOLUNTEER_ID = "-1"
DEFAULT_ADMIN_USER = "default"  ### OK to have in cleartext here as only used if no user security file exists
DEFAULT_ADMIN_PASSWORD = "default"

default_admin_user_if_none_defined = SkipperManUser(
    username=DEFAULT_ADMIN_USER,
    password_hash=generate_password_hash(DEFAULT_ADMIN_PASSWORD),
    group=ADMIN_GROUP,
    email_address="",
    volunteer_id=NO_VOLUNTEER_ID,
)

default_user_if_not_logged_in = SkipperManUser(
    username="public",
    password_hash="public",  ## irrelevant as not going to be logging in
    group=PUBLIC_GROUP,
    email_address="",
    volunteer_id=NO_VOLUNTEER_ID,
)


new_blank_user = SkipperManUser(
    "", "", ADMIN_GROUP, email_address="", volunteer_id=NO_VOLUNTEER_ID
)


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

    def modify_volunteer_for_user(self, username: str, volunteer: Volunteer):
        self.modify_volunteer_id(username=username, new_id=volunteer.id)

    def modify_volunteer_id(self, username: str, new_id: str):
        user = self.get_user_given_username(username)
        user.volunteer_id = new_id

    def modify_user_group(self, username: str, new_group: str):
        user = self.get_user_given_username(username)
        user.group = new_group

    def delete(self, username: str):
        try:
            assert self.already_in_list(username)
        except:
            raise Exception("can't delete non existent user")

        user = self.get_user_given_username(username)
        self.remove(user)

    def get_user_given_username(
        self, username: str, default=default_user_if_not_logged_in
    ) -> SkipperManUser:
        return get_unique_object_with_attr_in_list(
            some_list=self, attr_name="username", attr_value=username, default=default
        )

    def list_of_usernames_excludes_default(self):
        return [user.username for user in self]

    def list_of_users(self) -> "ListOfSkipperManUsers":
        return list_of_users_or_default_if_empty(self)

    def only_one_admin_user_and_it_is_the_passed_user(
        self, user: SkipperManUser
    ) -> bool:
        ## doesn't use list of users
        admin_users = self.list_of_admin_users()
        if len(admin_users) == 1:
            this_is_the_admin_user = admin_users[0] == user
            return this_is_the_admin_user
        else:
            return False

    def list_of_admin_users(self):
        admin = [user for user in self if user.group == ADMIN_GROUP]

        return ListOfSkipperManUsers(admin)

    def check_for_duplicated_names(self):
        list_of_names = self.list_of_usernames_excludes_default()
        assert len(list_of_names) == len(set(list_of_names))


def list_of_users_or_default_if_empty(
    list_of_users: ListOfSkipperManUsers,
) -> ListOfSkipperManUsers:
    if len(list_of_users) > 0:
        return list_of_users
    else:
        return ListOfSkipperManUsers(
            [default_admin_user_if_none_defined, default_user_if_not_logged_in]
        )


def get_random_string(length: int) -> str:
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = "".join(choice(letters) for i in range(length))
    return result_str
