from typing import Union

from app.objects.abstract_objects.abstract_form import Form, NewForm

from app.objects.abstract_objects.abstract_interface import abstractInterface


def display_form_config_volunteer_roles(interface: abstractInterface) -> Form:
    pass


def post_form_config_volunteer_roles(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    pass

