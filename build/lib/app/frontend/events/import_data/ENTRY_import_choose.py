from typing import Union

from app.frontend.events.import_data.wa_import_gateway import (
    display_form_WA_import_gateway,
)

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    Button,
    ButtonBar,
    back_menu_button,
)
from app.objects.abstract_objects.abstract_lines import ListOfLines, Line
from app.objects.abstract_objects.abstract_interface import abstractInterface

IMPORT_FROM_WA = "Import from WA spreadsheet file"

wa_import_button = Button(IMPORT_FROM_WA, tile=True)

nav_buttons = ButtonBar([main_menu_button, back_menu_button])
option_buttons = Line([wa_import_button])


def display_form_choose_import_source(interface: abstractInterface) -> Form:
    lines_inside_form = ListOfLines([nav_buttons, option_buttons])

    return Form(lines_inside_form)


def post_form_choose_import_source(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if wa_import_button.pressed(button_pressed):
        return interface.get_new_form_given_function(display_form_WA_import_gateway)
    elif back_menu_button.pressed(button_pressed):
        return interface.get_new_display_form_for_parent_of_function(
            post_form_choose_import_source
        )
    else:
        return button_error_and_back_to_initial_state_form(interface)
