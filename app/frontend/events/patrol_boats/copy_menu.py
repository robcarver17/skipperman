from typing import Union

from app.backend.patrol_boats.copying import copy_patrol_boat_labels_across_event
from app.frontend.events.patrol_boats.copying import (
    copy_across_all_boats,
    copy_across_all_boats_and_roles,
    overwrite_allocation_across_all_boats,
    overwrite_copy_across_all_boats_and_roles, copy_and_overwrite_labels, copy_labels,
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
from app.objects.abstract_objects.abstract_text import Heading, bold


def display_form_patrol_boat_copy_menu(interface: abstractInterface):
    navbar = ButtonBar([back_menu_button, help_button])
    event = get_event_from_state(interface)
    contents_of_form = ListOfLines(
        [
            navbar,
            _______________,
            Heading(
                "Copying volunteer patrol boats and optionally roles for %s "
                % event.event_name,
                centred=False,
            ),
            _______________,
            "All options will copy from the earliest patrol boat and/or role (and group if allocated) a volunteer has in an event, and will only copy into days when the volunteer is marked as available",
            _______________,
            _______________,
            copy_all_boats_button,
            _______________,
            copy_all_boats_and_roles_button,
            _______________,
            copy_all_designation_button,
            _______________,
            bold(
                "Warning: These options overwrite existing data. Be careful, consider snapshotting data first. "
            ),
            _______________,
            copyover_all_boats_button,
            _______________,
            copyover_all_boats_and_roles_button,
            _______________,
            copyover_designation_button
        ]
    ).add_Lines()

    return Form(contents_of_form)


help_button = HelpButton("copy_menu_patrol_boat_help")


def post_form_patrol_boat_copy_menu(
    interface: abstractInterface,
) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()

    if back_menu_button.pressed(button_pressed):
        pass
    elif copy_all_boats_button.pressed(button_pressed):
        copy_across_all_boats(interface)

    elif copy_all_boats_and_roles_button.pressed(button_pressed):
        copy_across_all_boats_and_roles(interface)

    elif copy_all_designation_button.pressed(button_pressed):
        copy_labels(interface)


    elif copyover_all_boats_button.pressed(button_pressed):
        overwrite_allocation_across_all_boats(interface)

    elif copyover_all_boats_and_roles_button.pressed(button_pressed):
        overwrite_copy_across_all_boats_and_roles(interface)

    elif copyover_designation_button.pressed(button_pressed):
        copy_and_overwrite_labels(interface)

    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return interface.get_new_display_form_for_parent_of_function(
        display_form_patrol_boat_copy_menu
    )


COPY_ALL_BOATS_BUTTON_LABEL = (
    "Copy and fill any empty boat allocations from earliest day when allocated"
)
COPYOVER_ALL_BOATS_BUTTON_LABEL = "Copy and overwrite all other boat allocations from earliest day when allocated: CAREFUL CAN'T BE UNDONE!"
COPY_BOATS_AND_ROLES_BUTTON_LABEL = "Copy and fill any empty boat allocations, plus roles (and allocated group if relevant) from earliest day when allocated"
COPYOVER_BOATS_AND_ROLES_BUTTON_LABEL = "Copy and overwrite all other empty boat allocations, plus roles (and allocated group if relevant) from earliest day when allocated: CAREFUL CAN'T BE UNDONE"
COPY_DESIGNATION_BUTTON_LABEL = "Copy and fill any empty designations from earliest day when labelled"
COPYOVER_DESIGNATION_BUTTON_LABEL = "Copy and overwrite any empty designations from earliest day when labelled: CAREFUL CAN'T BE UNDONE"

copy_all_boats_button = Button(COPY_ALL_BOATS_BUTTON_LABEL)
copyover_all_boats_button = Button(COPYOVER_ALL_BOATS_BUTTON_LABEL)
copy_all_boats_and_roles_button = Button(COPY_BOATS_AND_ROLES_BUTTON_LABEL)
copyover_all_boats_and_roles_button = Button(COPYOVER_BOATS_AND_ROLES_BUTTON_LABEL)
copy_all_designation_button = Button(COPY_DESIGNATION_BUTTON_LABEL)
copyover_designation_button = Button(COPYOVER_DESIGNATION_BUTTON_LABEL)