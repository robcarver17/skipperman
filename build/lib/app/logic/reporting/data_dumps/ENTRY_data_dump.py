import os
from typing import Union

from app.objects.abstract_objects.abstract_text import Heading


from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_form import (
    Form,
    File, NewForm, )
from app.objects.abstract_objects.abstract_lines import ListOfLines
from app.objects.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL, Button, ButtonBar, main_menu_button, \
    cancel_menu_button


def display_form_for_data_dump_report(interface: abstractInterface):


    title = Heading("Under construction", centred=True, size=4)
    contents_of_form = ListOfLines(
        [
            ButtonBar([main_menu_button, cancel_menu_button]),
            title,
        ]
    )

    return Form(contents_of_form)



def post_form_for_data_dump_report(
    interface: abstractInterface,
) -> Union[File, Form, NewForm]:
    last_button = interface.last_button_pressed()
    if cancel_menu_button.pressed(last_button):
        return previous_form(interface)

def previous_form(interface: abstractInterface) -> NewForm:
    return interface.get_new_display_form_for_parent_of_function(display_form_for_data_dump_report)
