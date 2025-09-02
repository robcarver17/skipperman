from app.data_access.backups.find_and_restore_backups import (
    dict_of_backups_with_datetimes,
    restore_backup,
)

from typing import Union

from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
)
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    back_menu_button,
    HelpButton,
)
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.abstract_objects.abstract_text import Heading


def display_form_view_of_snapshots(interface: abstractInterface) -> Form:
    list_of_buttons = list_of_snapshot_buttons(interface)

    form_contents = ListOfLines(
        [
            ButtonBar([back_menu_button, help_button]),
            _______________,
            Line(
                [
                    Heading("Click on any snapshot to restore", size=4),
                    Heading(
                        "WILL OVERWRITE ALL CHANGES MADE SINCE THEN - THERE IS NO 'ARE YOU SURE' DIALOG",
                        size=2,
                    ),
                    Heading(
                        "Can only be undone by going to a more recent snapshot or restoring data from local machine",
                        size=3,
                    ),
                    Heading("Click 'Back' if unsure about doing this", size=4),
                ]
            ),
            _______________,
            list_of_buttons,
        ]
    )

    form = Form(form_contents)

    return form


help_button = HelpButton("data_backup_help")


def post_form_view_of_snapshots(interface: abstractInterface) -> Union[Form, NewForm]:
    button_pressed = interface.last_button_pressed()
    if back_menu_button.pressed(button_pressed):
        return interface.get_new_display_form_for_parent_of_function(
            post_form_view_of_snapshots
        )
    elif button_pressed in get_all_snapshot_labels(interface):
        return restore_snapshot_given_button_pressed(
            interface=interface, button_pressed=button_pressed
        )
    else:
        return button_error_and_back_to_initial_state_form(interface)


def list_of_snapshot_buttons(interface: abstractInterface):
    all_labels = get_all_snapshot_labels(interface)
    return ListOfLines([Line(Button(name)) for name in all_labels])


def get_all_snapshot_labels(interface: abstractInterface):
    dict_of_snapshots = dict_of_backups_with_datetimes(
        interface.object_store.backup_data_path
    )
    return [
        "%d Backed up on %s" % (backupid, str(backup_datetime))
        for backupid, backup_datetime in dict_of_snapshots.items()
    ]


def from_button_name_to_backup_id(button_pressed: str) -> int:
    splitter = button_pressed.split(" ")
    return int(splitter[0])


def restore_snapshot_given_button_pressed(
    button_pressed: str, interface: abstractInterface
) -> NewForm:
    backup_id = from_button_name_to_backup_id(button_pressed)
    try:
        restore_backup(
            interface=interface,
            backup_diff=backup_id,
            datapath=interface.object_store.backup_data_path,
        )
        ## otherwise backup won't be seen
        interface.clear_persistent_cache()

    except Exception as e:
        interface.log_error("Can't restore backup, error %s" % str(e))

    return interface.get_new_display_form_for_parent_of_function(
        post_form_view_of_snapshots
    )
