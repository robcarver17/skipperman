from random import choice
import string
from dataclasses import dataclass
from enum import Enum

from app.objects.utilities.exceptions import arg_not_passed, missing_data
from app.objects.volunteers import Volunteer
from werkzeug.security import generate_password_hash, check_password_hash

from app.objects.utilities.generic_list_of_objects import (
    GenericListOfObjects,
    get_unique_object_with_attr_in_list,
    get_idx_of_unique_object_with_attr_in_list,
)
from app.objects.utilities.generic_objects import GenericSkipperManObject

UserGroup = Enum("UserGroup", ["admin", "skipper", "instructor", "RO", "public"])
ADMIN_GROUP = UserGroup.admin
SKIPPER_GROUP = UserGroup.skipper
INSTRUCTOR_GROUP = UserGroup.instructor
PUBLIC_GROUP = UserGroup.public
RACE_OFFICER_GROUP = UserGroup.RO

ALL_GROUPS = [
    ADMIN_GROUP,
    SKIPPER_GROUP,
    INSTRUCTOR_GROUP,
    RACE_OFFICER_GROUP,
    PUBLIC_GROUP,
]


@dataclass
class SkipperManUser(GenericSkipperManObject):
    username: str
    password_hash: str
    group: UserGroup
    email_address: str  ## not currently used
    volunteer_id: str

    @property
    def no_volunteer(self):
        return self.volunteer_id == NO_VOLUNTEER_ID

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
DEFAULT_ADMIN_USER = "default"  ### OK to have in cleartext here as only used if no user security file exists at first login or on test machine
DEFAULT_ADMIN_PASSWORD = "default"  ### OK to have in clear text here as only used if no user security file exists

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

    def replace_user(self, username: str, user: SkipperManUser):
        idx = self.idx_of_user(username, default=missing_data)
        if idx is missing_data:
            raise Exception("Can't replace non existent user %s" % username)

        self[idx] = user

    def idx_of_user(self, username: str, default=arg_not_passed):
        return get_idx_of_unique_object_with_attr_in_list(
            self, attr_name="username", attr_value=username, default=default
        )

    def already_in_list(self, username: str) -> bool:
        existing_usernames = self.list_of_usernames_excludes_default()
        return username in existing_usernames

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


def list_of_users_or_default_if_empty(
    list_of_users: ListOfSkipperManUsers,
) -> ListOfSkipperManUsers:
    ## Ensures at least one user exists
    if len(list_of_users) > 0:
        return list_of_users
    else:
        return ListOfSkipperManUsers([default_admin_user_if_none_defined])


def get_random_string(length: int) -> str:
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = "".join(choice(letters) for i in range(length))
    return result_str


CAN_DO_BACKUPS = [ADMIN_GROUP, SKIPPER_GROUP]


def group_is_admin_or_skipper(group):
    return group in [ADMIN_GROUP, SKIPPER_GROUP]
