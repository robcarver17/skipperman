from typing import Union

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface

def display_form_choose_level_for_group_at_event(interface: abstractInterface) -> Form:
    pass

def post_form_choose_level_for_group_at_event(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    pass

