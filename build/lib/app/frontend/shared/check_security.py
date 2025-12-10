from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.users_and_security import group_is_admin_or_skipper

def is_admin_or_skipper(interface: abstractInterface):
    return group_is_admin_or_skipper(interface.user_group)

