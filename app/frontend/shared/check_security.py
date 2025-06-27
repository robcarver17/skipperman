from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.users_and_security import ADMIN_GROUP, SKIPPER_GROUP


def is_admin_or_skipper(interface: abstractInterface):
    return interface.user_group in [ADMIN_GROUP, SKIPPER_GROUP]

