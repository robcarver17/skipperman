from typing import Union

from app.objects.volunteers import Volunteer, default_volunteer
from app.backend.volunteers.list_of_volunteers import get_volunteer_from_id
from app.backend.security.list_of_users import get_list_of_users

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.users_and_security import SkipperManUser

## possible vunerability if a user with name superuser created, but only someone with admin rights who is a superuser could do this
VOLUNTEER_IS_PRINCIPAL_CI_SKIPPER_ADMIN = Volunteer("****SUPERUSE****", "****")


def get_volunteer_for_logged_in_user_or_awarding_user(
    interface: abstractInterface,
) -> Union[Volunteer, object]:
    user = get_logged_in_skipperman_user(interface)

    if user.is_principal_ci_skipper_or_admin():
        return VOLUNTEER_IS_PRINCIPAL_CI_SKIPPER_ADMIN
    volunteer = get_volunteer_from_id(
        object_store=interface.object_store, volunteer_id=user.volunteer_id
    )

    return volunteer

def get_group_description_for_logged_in_user(interface: abstractInterface) -> str:
    user = get_logged_in_skipperman_user(interface)
    return user.describe_group()


def can_logged_in_volunteer_award_qualifications(interface: abstractInterface):
    user = get_logged_in_skipperman_user(interface)
    return user.can_award_qualifications()


def get_volunteer_name_for_logged_in_user(
    interface: abstractInterface,
) -> str:
    volunteer = get_loggged_in_volunteer(interface)

    return volunteer.name


def get_loggged_in_volunteer(interface: abstractInterface) -> Volunteer:
    user = get_logged_in_skipperman_user(interface)

    if user.no_volunteer:
        return default_volunteer

    volunteer = get_volunteer_from_id(
        object_store=interface.object_store, volunteer_id=user.volunteer_id
    )

    return volunteer


def get_logged_in_skipperman_user(interface: abstractInterface) -> SkipperManUser:
    username = interface.get_current_logged_in_username()
    list_of_users = get_list_of_users(interface.object_store)

    return list_of_users.get_user_given_username(username)
