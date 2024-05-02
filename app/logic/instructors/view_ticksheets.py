from typing import Union

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface

def display_form_view_ticksheets_for_event_and_group(interface: abstractInterface) -> Form:
    ### options: print, edit, add qualifications (super users only)
    pass

def post_form_view_ticksheets_for_event_and_group(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    pass

