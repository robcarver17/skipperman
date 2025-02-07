from typing import Union

from app.objects.volunteers import Volunteer
from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id
from app.backend.security.list_of_users import get_list_of_users

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.users_and_security import SkipperManUser

## possible vunerability if a user with name superuser created, but only someone with admin rights who is a superuser could do this
SUPERUSER = Volunteer("****SUPERUSE****", "****")


def get_volunteer_for_logged_in_user_or_superuser(
    interface: abstractInterface,
) -> Union[Volunteer, object]:
    user = get_logged_in_skipperman_user(interface)

    if user.is_skipper_or_admin():
        return SUPERUSER
    volunteer = get_volunteer_from_id(
        object_store=interface.object_store, volunteer_id=user.volunteer_id
    )

    return volunteer




def get_logged_in_skipperman_user(interface: abstractInterface) -> SkipperManUser:
    username = interface.get_current_logged_in_username()
    list_of_users = get_list_of_users(interface.object_store)

    return list_of_users.get_user_given_username(username)
