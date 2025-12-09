from typing import Union

from app.frontend.shared.add_manual_registration import (
    display_add_unregistered_form,
    post_form_add_unregistered_cadet,
)
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface


def display_add_unregistered_cadet_from_registration_form(
    interface: abstractInterface,
) -> Form:
    return display_add_unregistered_form(interface)


def post_form_add_unregistered_cadet_from_registration_form(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    return post_form_add_unregistered_cadet(
        interface=interface,
        calling_function=post_form_add_unregistered_cadet_from_registration_form,
    )
