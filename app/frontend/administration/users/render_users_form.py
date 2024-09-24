from typing import Union, List

from app.data_access.configuration.fixed import SAVE_KEYBOARD_SHORTCUT
from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface

from app.OLD_backend.volunteers.volunteers import (
    EPRECATE_get_volunteer_name_from_id,
    get_sorted_list_of_volunteers,
)

from app.OLD_backend.data.volunteers import SORT_BY_FIRSTNAME

from app.objects_OLD.abstract_objects.abstract_form import (
    Form,
    NewForm,
    textInput,
    dropDownInput,
    emailInput,
)
from app.objects_OLD.abstract_objects.abstract_tables import RowInTable, Table
from app.objects.abstract_objects.abstract_lines import (
    Line,
    ListOfLines,
    _______________,
)
from app.objects_OLD.abstract_objects.abstract_text import bold, Heading
from app.objects_OLD.abstract_objects.abstract_buttons import (
    Button,
    ButtonBar,
    cancel_menu_button,
)
from app.objects_OLD.users_and_security import (
    ListOfSkipperManUsers,
    SkipperManUser,
    ADMIN_GROUP,
    ALL_GROUPS,
    NO_VOLUNTEER_ID,
)
from app.OLD_backend.data.security import load_all_users

SAVE_ENTRY_BUTTON_LABEL = "Save edits to existing or add new entry"


def display_form_edit_list_of_users(
    interface: abstractInterface, existing_list_of_users: ListOfSkipperManUsers
) -> Union[Form, NewForm]:
    header_text = Heading(
        "List of current skipperman users; edit name, enter new password, modify access, delete (carefully!) or add new user. Passwords are not shown, but can be changed by entering new values.",
        centred=False,
        size=4,
    )
    warning = warning_text(interface)
    user_table = table_for_users(
        interface=interface, existing_list_of_users=existing_list_of_users
    )
    nav_buttons = ButtonBar([cancel_menu_button])
    footer_buttons = ButtonBar(
        [
            Button(
                SAVE_ENTRY_BUTTON_LABEL,
                nav_button=True,
                shortcut=SAVE_KEYBOARD_SHORTCUT,
            )
        ]
    )

    return Form(
        [
            ListOfLines(
                [
                    nav_buttons,
                    header_text,
                    warning,
                    _______________,
                    user_table,
                    _______________,
                    footer_buttons,
                ]
            )
        ]
    )


def warning_text(interface: abstractInterface):
    if no_admin_users(interface):
        return Line(
            bold(
                "*** AT LEAST ONE USER MUST HAVE ADMIN RIGHTS - ADD A NEW USER OR EDIT AN EXISTING USER TO REFLECT THIS ***"
            )
        )
    else:
        return ""


new_user = user = SkipperManUser(
    "", "", ADMIN_GROUP, email_address="", volunteer_id=NO_VOLUNTEER_ID
)


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
            text_box_for_username(user),
            text_box_for_password(user),
            text_box_for_password(user, True),
            dropdown_for_group(user),
            "",
            # NOT CURRENTLY USING EMAILS
            # text_box_for_email(user),
            dropdown_for_volunteer(interface=interface, user=user),
        ],
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
    return RowInTable(
        [
            "",
            existing_user.username,
            text_box_for_password(existing_user),
            text_box_for_password(existing_user, True),
            dropdown_for_group(existing_user),
            button_for_deletion(existing_user),
            # NOT CURRENTLY USING EMAILS
            # text_box_for_email(existing_user),
            dropdown_for_volunteer(interface=interface, user=existing_user),
            # NOT CURRENTLY USING EMAILS
            send_email_button(existing_user),
        ],
    )


USERNAME = "username"
PASSWORD = "password"
EMAIL = "email"
PASSWORD_CONFIRM = "password_confirm"
GROUP = "group"
DELETION = "delete"
VOLUNTEER = "volunteer"
SEND_EMAIL = "Reset password"


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


#### not used
def text_box_for_email(user: SkipperManUser) -> emailInput:
    return emailInput(
        value=user.username,
        input_label="Email address",
        input_name=name_for_user_and_input_type(user, EMAIL),
    )


def dropdown_for_volunteer(
    interface: abstractInterface, user: SkipperManUser
) -> dropDownInput:
    volunteers = get_sorted_list_of_volunteers(
        data_layer=interface.data, sort_by=SORT_BY_FIRSTNAME
    )
    dict_of_volunteers = dict(
        [(volunteer.name, volunteer.name) for volunteer in volunteers]
    )
    try:
        name = EPRECATE_get_volunteer_name_from_id(
            interface=interface, volunteer_id=user.volunteer_id
        )
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


def send_email_button(user: SkipperManUser) -> Button:
    return Button(label="Reset password", value=button_name_for_email_send(user))


def button_for_deletion(user: SkipperManUser) -> Button:
    return Button(label="Delete", value=button_name_for_deletion(user))


def button_name_for_deletion(user: SkipperManUser):
    return "Delete_%s" % user.username


def button_name_for_email_send(user: SkipperManUser):
    return "Reset_%s" % user.username


def username_from_deletion_button(button_name: str) -> str:
    splitter = button_name.split("_")
    return splitter[1]


def username_from_email_button(button_name: str) -> str:
    splitter = button_name.split("_")
    return splitter[1]


def name_for_user_and_input_type(user: SkipperManUser, input_type: str):
    return user.username + "_" + input_type


def list_of_deletion_buttons_names(interface: abstractInterface):
    existing_list_of_users = load_all_users(interface=interface)
    return [button_name_for_deletion(user) for user in existing_list_of_users]


def list_of_email_send_buttons_names(interface: abstractInterface):
    existing_list_of_users = load_all_users(interface)
    return [button_name_for_email_send(user) for user in existing_list_of_users]


def no_admin_users(interface: abstractInterface):
    all_users = load_all_users(interface)
    return not all_users.at_least_one_admin_user()
