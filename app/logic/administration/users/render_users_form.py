from typing import Union

from app.backend.volunteers.volunteers import DEPRECATED_get_volunteer_name_from_id

from app.backend.data.volunteers import DEPRECATED_get_sorted_list_of_volunteers, SORT_BY_FIRSTNAME

from app.objects.abstract_objects.abstract_form import Form, NewForm, textInput, passwordInput, dropDownInput, \
    emailInput
from app.objects.abstract_objects.abstract_lines import Line, ListOfLines, _______________
from app.objects.abstract_objects.abstract_text import bold, Heading
from app.objects.abstract_objects.abstract_buttons import Button, ButtonBar
from app.objects.users_and_security import ListOfSkipperManUsers, SkipperManUser, ADMIN_GROUP, ALL_GROUPS, \
    NO_VOLUNTEER_ID
from app.backend.data.security import load_all_users


BACK_BUTTON_LABEL = "Back (cancel changes)"
SAVE_ENTRY_BUTTON_LABEL =  "Save edits to existing or add new entry"

def display_form_edit_list_of_users(
    existing_list_of_users: ListOfSkipperManUsers
) -> Union[Form, NewForm]:

    header_text= Heading("List of current skipperman users; edit name, enter new password, modify access, delete (carefully!) or add new user. Passwords are not shown, but can be changed by entering new values.", centred=False, size=4)
    existing_entries = rows_for_existing_list_of_users(existing_list_of_users)
    new_entries = row_for_new_user()
    warning = warning_text()
    nav_buttons = ButtonBar([Button(BACK_BUTTON_LABEL, nav_button=True)])
    footer_buttons = ButtonBar([Button(SAVE_ENTRY_BUTTON_LABEL, nav_button=True)])

    return Form([
        ListOfLines([
            nav_buttons,
            header_text,
            warning,
            _______________,
            existing_entries,
            new_entries,
            _______________,
            footer_buttons
        ])
    ])


new_user = user = SkipperManUser('', '', ADMIN_GROUP, email_address='', volunteer_id=NO_VOLUNTEER_ID)

def warning_text():
    if no_admin_users():
        return Line(bold("*** AT LEAST ONE USER MUST HAVE ADMIN RIGHTS - ADD A NEW USER OR EDIT AN EXISTING USER TO REFLECT THIS ***"))
    else:
        return ""

def row_for_new_user():

    return Line(
        [ "Add new user: ", text_box_for_username(user), text_box_for_password(user),text_box_for_password(user, True),  dropdown_for_group(user),
          text_box_for_email(user),
          dropdown_for_volunteer(user)
            ],
    )


def rows_for_existing_list_of_users(existing_list_of_users: ListOfSkipperManUsers) -> ListOfLines:

    return ListOfLines([
        get_row_for_existing_user(user) for user in existing_list_of_users
    ])


def get_row_for_existing_user(existing_user: SkipperManUser) -> Line:
    return Line(
        [ "Username: %s  " % existing_user.username, text_box_for_password(existing_user),
          text_box_for_password(existing_user, True),  dropdown_for_group(existing_user), button_for_deletion(existing_user),
          text_box_for_email(existing_user),
          dropdown_for_volunteer(existing_user),
          send_email_button(existing_user)
            ],
    )


USERNAME = "username"
PASSWORD = "password"
EMAIL = "email"
PASSWORD_CONFIRM = "password_confirm"
GROUP = "group"
DELETION = "delete"
VOLUNTEER = "volunteer"
SEND_EMAIL = "Send email link to reset password"

def text_box_for_username(user: SkipperManUser)-> textInput:
    return textInput(value=user.username,
                     input_label="User name",
                     input_name=name_for_user_and_input_type(user, USERNAME))


def text_box_for_password(user: SkipperManUser, confirm = False)-> textInput:
    if confirm:
        name = PASSWORD_CONFIRM
        label = "   Confirm password"
    else:
        name = PASSWORD
        label = "   New password"
    return textInput(value='',
                     input_label=label,
                     input_name=name_for_user_and_input_type(user, name))

def text_box_for_email(user: SkipperManUser) -> textInput:
    return textInput(value=user.username,
                     input_label="Email address",
                     input_name=name_for_user_and_input_type(user, EMAIL))

def dropdown_for_volunteer(user: SkipperManUser) -> dropDownInput:
    volunteers = DEPRECATED_get_sorted_list_of_volunteers(SORT_BY_FIRSTNAME)
    dict_of_volunteers = dict([(volunteer.name, volunteer.name) for volunteer in volunteers])
    try:
        name = DEPRECATED_get_volunteer_name_from_id(user.volunteer_id)
    except:
        name = ''

    return dropDownInput(
        default_label=name,
        dict_of_options=dict_of_volunteers,
        input_name=name_for_user_and_input_type(user, VOLUNTEER),
        input_label="Associated volunteer:"
    )

def dropdown_for_group(user: SkipperManUser) -> dropDownInput:
    return dropDownInput(
    default_label=user.group.name,
        dict_of_options=user_group_options_as_dict,
        input_name=name_for_user_and_input_type(user,GROUP),
        input_label="   Access group "
    )


user_group_options_as_dict = dict([(group.name, group.name) for group in ALL_GROUPS])

def send_email_button(user: SkipperManUser) -> Button:
    return Button(button_name_for_email_send(user))

def button_for_deletion(user: SkipperManUser)-> Button:
    return Button(button_name_for_deletion(user))


def button_name_for_deletion(user: SkipperManUser):
    return "Delete %s" % user.username

def button_name_for_email_send(user: SkipperManUser):
    return "Reset password and return link for %s" % user.username

def username_from_deletion_button(button_name: str) -> str:
    splitter=button_name.split(" ")
    return " ".join(splitter[1:])

def username_from_email_button(button_name: str) -> str:
    splitter=button_name.split(" ")
    return " ".join(splitter[6:])

def name_for_user_and_input_type(user: SkipperManUser, input_type: str):
    return user.username+"_"+input_type

def list_of_deletion_buttons_names():
    existing_list_of_users = load_all_users()
    return [button_for_deletion(user) for user in existing_list_of_users]

def list_of_email_send_buttons_names():
    existing_list_of_users = load_all_users()
    return [button_name_for_email_send(user) for user in existing_list_of_users]

def no_admin_users():
    all_users = load_all_users()
    return not all_users.at_least_one_admin_user()
