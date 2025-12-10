from typing import Dict

from flask_login import UserMixin, current_user

from app.backend.security.list_of_users import get_list_of_users
from app.data_access.init_data import  object_store
from app.objects.users_and_security import (
    SkipperManUser,
    ListOfSkipperManUsers,
    UserGroup,
    CAN_DO_BACKUPS,
)


def get_access_group_for_current_user() -> UserGroup:
    group_name = current_user.group_name
    return UserGroup[group_name]


def get_username():
    return current_user.username



def authenticated_user():
    try:
        return current_user.is_authenticated
    except:
        return False


class FlaskUser(UserMixin):
    def __init__(self, username, password_hash, group: UserGroup):
        self.username = username
        self.password_hash = password_hash
        self.group_name = group.name

    def check_password(self, password):
        return check_password(self, password)

    def get_id(self):
        return self.username


def as_flask_user(skipper_man_user: SkipperManUser) -> FlaskUser:
    return FlaskUser(
        skipper_man_user.username,
        password_hash=skipper_man_user.password_hash,
        group=skipper_man_user.group,
    )


def check_password(flask_user: FlaskUser, password: str):
    skipperman_user = skipperman_user_from_flask_user(flask_user)
    return skipperman_user.check_password(password)


def as_dict_of_flask_users(
    list_of_users: ListOfSkipperManUsers,
) -> Dict[str, FlaskUser]:
    users = list_of_users.list_of_users()

    return dict([(user.username, as_flask_user(user)) for user in users])


def get_all_flask_users():
    all_skipperman_users_from_data = get_list_of_users(object_store)
    all_flask_users = as_dict_of_flask_users(all_skipperman_users_from_data)

    return all_flask_users



def skipperman_user_from_flask_user(flask_user: FlaskUser) -> SkipperManUser:
    return SkipperManUser(
        username=flask_user.username,
        password_hash=flask_user.password_hash,
        group=UserGroup[flask_user.group_name],
        email_address="",
        volunteer_id="",
    )


def allow_user_to_make_snapshots():
    if not authenticated_user():
        return False

    access_group = get_access_group_for_current_user()

    return access_group in CAN_DO_BACKUPS

