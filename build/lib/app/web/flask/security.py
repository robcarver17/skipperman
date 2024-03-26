from typing import Dict

from flask_login import UserMixin, current_user


from app.backend.data.security import load_all_users
from app.objects.users_and_security import SkipperManUser, ListOfSkipperManUsers, UserGroup

USERNAME = 'var078' ### can be anything


def get_access_group_for_current_user()-> UserGroup:
    group_name = current_user.group_name
    return UserGroup[group_name]

def get_username():
    return current_user.username

no_user = ''


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
    return FlaskUser(skipper_man_user.username, password_hash=skipper_man_user.password_hash, group=skipper_man_user.group)

def check_password(flask_user: FlaskUser, password: str):
    skipperman_user = SkipperManUser(username=flask_user.username, password_hash=flask_user.password_hash, group=UserGroup[flask_user.group_name])
    return skipperman_user.check_password(password)

def as_dict_of_flask_users(list_of_users: ListOfSkipperManUsers) -> Dict[str, FlaskUser]:
    users = list_of_users.list_of_users()

    return dict(
        [
            (user.username, as_flask_user(user))
            for user in users
        ]
    )

def get_all_flask_users():
    all_users_from_data = load_all_users()
    all_flask_users = as_dict_of_flask_users(all_users_from_data)

    return all_flask_users

all_flask_users=""