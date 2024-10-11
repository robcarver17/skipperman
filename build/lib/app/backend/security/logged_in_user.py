from app.backend.security.list_of_users import get_list_of_users

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.users_and_security import SkipperManUser

SUPERUSER = "_superuser_"


def get_volunteer_id_of_logged_in_user_or_superuser_CHANGE_TO_VOLUNTEER(
    interface: abstractInterface,
) -> str:
    user = get_logged_in_skipperman_user(interface)

    if user.is_skipper_or_admin():
        return SUPERUSER
    else:
        return user.volunteer_id


def get_logged_in_skipperman_user(interface: abstractInterface) -> SkipperManUser:
    username = interface.get_current_logged_in_username()
    list_of_users = get_list_of_users(interface.object_store)

    return list_of_users.get_user_given_username(username)
