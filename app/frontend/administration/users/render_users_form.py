from typing import Union, List

from app.data_access.configuration.fixed import (
    SAVE_KEYBOARD_SHORTCUT,
    ADD_KEYBOARD_SHORTCUT,
)
from app.objects.abstract_objects.abstract_interface import abstractInterface

from app.backend.volunteers.list_of_volunteers import (
    get_sorted_list_of_volunteers,
    get_volunteer_from_id,
)

from app.backend.volunteers.list_of_volunteers import SORT_BY_FIRSTNAME

from app.objects.abstract_objects.abstract_form import (
    Form,
    NewForm,
    textInput,
    dropDownInput,
)
from app.objects.abstract_objects.abstract_tables import RowInTable, Table
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects.abstract_objects.abstract_text import bold, Heading
from app.objects.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    cancel_menu_button,
    HelpButton,
)
from app.objects.users_and_security import (
    ListOfSkipperManUsers,
    SkipperManUser,
    ALL_GROUPS,
    new_blank_user,
)
from app.backend.security.list_of_users import get_list_of_users, list_of_admin_users
from app.frontend.shared.buttons import (
    get_button_value_given_type_and_attributes,
    is_button_of_type,
    get_attributes_from_button_pressed_of_known_type,
)

SAVE_ENTRY_BUTTON_LABEL = "Save edits to existing"
ADD_ENTRY_BUTTON_LABEL = "Add a new user"


def display_form_edit_list_of_users(
    interface: abstractInterface, existing_list_of_users: ListOfSkipperManUsers
) -> Union[Form, NewForm]:
    header_text = Heading(
        "List of current skipperman users",
        centred=True,
        size=4,
    )
    instructions = ListOfLines(
        [
            "Edit name, enter new password, modify access, delete (carefully!) or add new user.",
            " Passwords are not shown, but can be changed by entering new values and clicking 'Save edits' or clicking 'Reset password to random value' to create an arbitrary password.",
        ]
    ).add_Lines()
    warning = warning_text(interface)
    user_table = table_for_users(
        interface=interface, existing_list_of_users=existing_list_of_users
    )
    nav_buttons = ButtonBar([cancel_menu_button, save_entry_button, help_button])
    footer_buttons = ButtonBar([cancel_menu_button, save_entry_button])

    return Form(
        [
            ListOfLines(
                [
                    nav_buttons,
                    header_text,
                    _______________,
                    instructions,
                    _______________,
                    warning,
                    _______________,
                    user_table,
                    _______________,
                    footer_buttons,
                ]
            )
        ]
    )


help_button = HelpButton("list_of_users_help")
save_entry_button = Button(
    SAVE_ENTRY_BUTTON_LABEL,
    nav_button=True,
    shortcut=SAVE_KEYBOARD_SHORTCUT,
)

add_entry_button = Button(ADD_ENTRY_BUTTON_LABEL, shortcut=ADD_KEYBOARD_SHORTCUT)


def warning_text(interface: abstractInterface):
    admin_users = list_of_admin_users(interface.object_store)
    if len(admin_users) == 0:
        return Line(
            bold(
                "*** AT LEAST ONE USER MUST HAVE ADMIN RIGHTS - ADD A NEW USER OR EDIT AN EXISTING USER TO REFLECT THIS ***"
            )
        )
    elif len(admin_users) == 1:
        single_admin_user = admin_users[0]
        return bold(
            "Only one admin user (%s)- you will not be able to delete that user or change their access group unless you add another"
            % single_admin_user.username
        )
    else:
        return ""


def table_for_users(
    interface: abstractInterface, existing_list_of_users: ListOfSkipperManUsers
) -> Table:
    existing_entries = rows_for_existing_list_of_users(
        interface=interface, existing_list_of_users=existing_list_of_users
    )
    new_entries = row_for_new_user(interface=interface)

    return Table(existing_entries + [new_entries])


def row_for_new_user(interface: abstractInterface) -> RowInTable:
    return RowInTable(
        [
            "Add new user: ",
            text_box_for_username(new_blank_user),
            text_box_for_password(new_blank_user),
            text_box_for_password(new_blank_user, True),
            dropdown_for_group(new_blank_user),
            "",
            dropdown_for_volunteer(interface=interface, user=new_blank_user),
            add_entry_button,
        ]
    )


def rows_for_existing_list_of_users(
    interface: abstractInterface, existing_list_of_users: ListOfSkipperManUsers
) -> List[RowInTable]:
    return [
        get_row_for_existing_user(interface=interface, existing_user=user)
        for user in existing_list_of_users
    ]


def get_row_for_existing_user(
    interface: abstractInterface, existing_user: SkipperManUser
) -> RowInTable:
    list_of_users = get_list_of_users(interface.object_store)
    if list_of_users.only_one_admin_user_and_it_is_the_passed_user(existing_user):
        delete_button = "Cannot delete"
        group_dropdown = "Cannot change access"
    else:
        delete_button = button_for_deletion(existing_user)
        group_dropdown = dropdown_for_group(existing_user)

    return RowInTable(
        [
            "",
            existing_user.username,
            text_box_for_password(existing_user),
            text_box_for_password(existing_user, True),
            group_dropdown,
            delete_button,
            dropdown_for_volunteer(interface=interface, user=existing_user),
            button_to_reset_password(existing_user),
        ]
    )


USERNAME = "username"
PASSWORD = "password"
EMAIL = "email"
PASSWORD_CONFIRM = "password_confirm"
GROUP = "group"
DELETION = "delete"
VOLUNTEER = "volunteer"
GENERATE_NEW_PASSWORD = "Generate new password"


def text_box_for_username(user: SkipperManUser) -> textInput:
    return textInput(
        value=user.username,
        input_label="",
        input_name=name_for_user_and_input_type(user, USERNAME),
    )


def text_box_for_password(user: SkipperManUser, confirm=False) -> textInput:
    if confirm:
        name = PASSWORD_CONFIRM
        label = "   Confirm password"
    else:
        name = PASSWORD
        label = "   New password"
    return textInput(
        value="", input_label=label, input_name=name_for_user_and_input_type(user, name)
    )


def dropdown_for_volunteer(
    interface: abstractInterface, user: SkipperManUser
) -> dropDownInput:
    volunteers = get_sorted_list_of_volunteers(
        object_store=interface.object_store, sort_by=SORT_BY_FIRSTNAME
    )
    dict_of_volunteers = dict(
        [(volunteer.name, volunteer.name) for volunteer in volunteers]
    )
    try:
        volunteer = get_volunteer_from_id(
            object_store=interface.object_store, volunteer_id=user.volunteer_id
        )
        name = volunteer.name
    except:
        name = ""

    return dropDownInput(
        default_label=name,
        dict_of_options=dict_of_volunteers,
        input_name=name_for_user_and_input_type(user, VOLUNTEER),
        input_label="Associated volunteer:",
    )


def dropdown_for_group(user: SkipperManUser) -> dropDownInput:
    return dropDownInput(
        default_label=user.group.name,
        dict_of_options=user_group_options_as_dict,
        input_name=name_for_user_and_input_type(user, GROUP),
        input_label="   Access group ",
    )


user_group_options_as_dict = dict([(group.name, group.name) for group in ALL_GROUPS])


def button_to_reset_password(user: SkipperManUser) -> Button:
    return Button(
        label="Reset password to random value",
        value=button_name_for_reset_password(user),
    )


def button_for_deletion(user: SkipperManUser) -> Button:
    return Button(label="Delete", value=button_name_for_deletion(user))


button_type_reset_password = "resetPassword"
button_type_deletion = "deleteUser"


def button_name_for_deletion(user: SkipperManUser):
    return get_button_value_given_type_and_attributes(
        button_type_deletion, user.username
    )


def button_name_for_reset_password(user: SkipperManUser):
    return get_button_value_given_type_and_attributes(
        button_type_reset_password, user.username
    )


def is_delete_button(button_value: str):
    return is_button_of_type(
        value_of_button_pressed=button_value, type_to_check=button_type_deletion
    )


def is_reset_button(button_value: str):
    return is_button_of_type(
        value_of_button_pressed=button_value, type_to_check=button_type_reset_password
    )


def username_from_deletion_button(button_name: str) -> str:
    return get_attributes_from_button_pressed_of_known_type(
        type_to_check=button_type_deletion, value_of_button_pressed=button_name
    )


def username_from_reset_button(button_name: str) -> str:
    return get_attributes_from_button_pressed_of_known_type(
        type_to_check=button_type_reset_password, value_of_button_pressed=button_name
    )


def name_for_user_and_input_type(user: SkipperManUser, input_type: str):
    return user.username + "_" + input_type
