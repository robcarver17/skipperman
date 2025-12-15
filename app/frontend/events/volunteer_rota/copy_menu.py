from typing import Union

from app.frontend.events.volunteer_rota.copying import (
    update_if_copy_first_role_to_empty_roles_button_pressed,
    update_if_copy_first_role_and_overwrite_button_pressed,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.frontend.shared.events_state import get_event_from_state

from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    HelpButton,
    back_menu_button,
)
from app.objects.abstract_objects.abstract_lines import (
    ListOfLines,
    _______________,
    Line,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_text import Heading


def display_form_volunteer_copy_menu(interface: abstractInterface):
    navbar = ButtonBar([back_menu_button, help_button])
    event = get_event_from_state(interface)
    contents_of_form = ListOfLines(
        [
            navbar,
            _______________,
            Heading(
                "Copying volunteer roles for %s " % event.event_name, centred=False
            ),
            _______________,
            "Both options will copy from the earliest role (and group if allocated) a volunteer holds in an event, and will only copy into days when the volunteer is marked as available",
            _______________,
            _______________,
            copy_all_roles_from_first_role_button,
            _______________,
            copy_and_overwrite_all_roles_from_first_role_button,
        ]
    ).add_Lines()

    return Form(contents_of_form)


help_button = HelpButton("copy_menu_rota_help")


def post_form_volunteer_copy_menu(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()

    
    if back_menu_button.pressed(button_pressed):
        pass
    elif copy_all_roles_from_first_role_button.pressed(button_pressed):
        update_if_copy_first_role_to_empty_roles_button_pressed(interface=interface)

    elif copy_and_overwrite_all_roles_from_first_role_button.pressed(button_pressed):
        update_if_copy_first_role_and_overwrite_button_pressed(interface=interface)
    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.DEPRECATE_flush_and_clear()

    return interface.get_new_display_form_for_parent_of_function(
        post_form_volunteer_copy_menu
    )


COPY_ALL_ROLES_FROM_FIRST_ROLE_BUTTON_LABEL = "Click to copy earliest role into any days when the volunteer does not have a role allocated"
COPY_AND_OVERWRITE_FROM__FIRST_ROLE_BUTTON_LABEL = "Click to copy earliest role and also overwrite all existing allocations (CAREFUL! CAN'T BE UNDONE)"

copy_all_roles_from_first_role_button = Button(
    COPY_ALL_ROLES_FROM_FIRST_ROLE_BUTTON_LABEL, nav_button=False
)
copy_and_overwrite_all_roles_from_first_role_button = Button(
    COPY_AND_OVERWRITE_FROM__FIRST_ROLE_BUTTON_LABEL, nav_button=False
)
