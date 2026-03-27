from typing import Union

from app.backend.security.audit_logs import (
    get_list_of_audit_logs_for_event_newest_first,
)
from app.frontend.events.import_data.wa_import_gateway import (
    display_form_WA_import_gateway,
)

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.audit_log import get_audit_log_to_display_for_event
from app.frontend.shared.events_state import get_event_from_state
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    main_menu_button,
    Button,
    ButtonBar,
    back_menu_button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    Line,
    MainMenuBar,
    _______________,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface

IMPORT_FROM_WA = "Import from Wild Apricot"
wa_import_button = Button(IMPORT_FROM_WA, tile=True)
help_button = HelpButton("import_registration_data_help")

nav_buttons = ButtonBar([main_menu_button, back_menu_button, help_button])
option_buttons = Line([wa_import_button])


def display_form_choose_import_source(interface: abstractInterface) -> Form:
    audit_log = get_audit_log_to_display_for_event(interface)
    main_menu = [MainMenuBar("Events"), _______________]
    if len(audit_log) == 0:
        audit_lines = ["No imports done"]
    else:
        audit_lines = ["Imports:", audit_log]
    lines_inside_form = ListOfLines(
        main_menu + [nav_buttons, option_buttons] + audit_lines
    )

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
