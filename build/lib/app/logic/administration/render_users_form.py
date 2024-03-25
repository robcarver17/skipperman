from typing import Union

from app.objects.abstract_objects.abstract_form import Form, NewForm, textInput, passwordInput, dropDownInput
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.objects.abstract_objects.abstract_text import bold
from app.objects.abstract_objects.abstract_buttons import Button
from app.objects.users_and_security import ListOfSkipperManUsers, SkipperManUser, ADMIN_GROUP, ALL_GROUPS
from app.backend.data.security import load_all_users


BACK_BUTTON_LABEL = "Back (cancel changes)"
SAVE_ENTRY_BUTTON_LABEL =  "Save edits to existing or add new entry"

def display_form_edit_list_of_users(
    existing_list_of_users: ListOfSkipperManUsers
) -> Union[Form, NewForm]:

    header_text= "List of current skipperman users; edit name, enter new password, modify access, delete (carefully!) or add new user. Passwords are not shown, but can be changed by entering new values."
    existing_entries = rows_for_existing_list_of_users(existing_list_of_users)
    new_entries = row_for_new_user()
    warning = warning_text()
    footer_buttons = Line([Button(BACK_BUTTON_LABEL), Button(SAVE_ENTRY_BUTTON_LABEL)])

    return Form([
        ListOfLines([
            header_text,
            warning,
            _______________,
            existing_entries,
            new_entries,
            _______________,
            footer_buttons
        ])
    ])


new_user = user = SkipperManUser('', '', ADMIN_GROUP)

def warning_text():
    if no_admin_users():
        return bold("*** AT LEAST ONE USER MUST HAVE ADMIN RIGHTS - ADD A NEW USER OR EDIT AN EXISTING USER TO REFLECT THIS ***")
    else:
        return ""

def row_for_new_user():

    return Line(
        [ "Add new user: ", text_box_for_username(user), text_box_for_password(user),text_box_for_password(user, True),  dropdown_for_group(user),
            ],
    )


def rows_for_existing_list_of_users(existing_list_of_users: ListOfSkipperManUsers) -> ListOfLines:

    return ListOfLines([
        get_row_for_existing_user(user) for user in existing_list_of_users
    ])


def get_row_for_existing_user(user: SkipperManUser) -> Line:
    return Line(
        [ "Username: "+user.username, text_box_for_password(user),text_box_for_password(user, True),  dropdown_for_group(user), button_for_deletion(user)
            ],
    )


USERNAME = "username"
PASSWORD = "password"
PASSWORD_CONFIRM = "password_confirm"
GROUP = "group"
DELETION = "delete"


def text_box_for_username(user: SkipperManUser)-> textInput:
    return textInput(value=user.username,
                     input_label="User name",
                     input_name=name_for_user_and_input_type(user, USERNAME))


def text_box_for_password(user: SkipperManUser, confirm = False)-> textInput:
    if confirm:
        name = PASSWORD_CONFIRM
        label = "Confirm password"
    else:
        name = PASSWORD
        label = "New password"
    return textInput(value='',
                     input_label=label,
                     input_name=name_for_user_and_input_type(user, name))


def dropdown_for_group(user: SkipperManUser) -> dropDownInput:
    return dropDownInput(
    default_label=user.group.name,
        dict_of_options=user_group_options_as_dict,
        input_name=name_for_user_and_input_type(user,GROUP),
        input_label="Access group "
    )


user_group_options_as_dict = dict([(group.name, group.name) for group in ALL_GROUPS])


def button_for_deletion(user: SkipperManUser)-> Button:
    return Button(button_name_for_deletion(user))


def button_name_for_deletion(user: SkipperManUser):
    return "Delete %s" % user.username

def username_from_deletion_button(button_name: str) -> str:
    splitter=button_name.split(" ")
    return "".join(splitter[1:])

def name_for_user_and_input_type(user: SkipperManUser, input_type: str):
    return user.username+"_"+input_type

def list_of_deletion_buttons_names():
    existing_list_of_users = load_all_users()
    return [button_for_deletion(user) for user in existing_list_of_users]

def no_admin_users():
    all_users = load_all_users()
    return not all_users.at_least_one_admin_user()
