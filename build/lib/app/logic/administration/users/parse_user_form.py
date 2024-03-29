from dataclasses import dataclass

from app.backend.data.security import add_user, already_in_list, delete_username_from_user_list, load_all_users, \
    change_password_for_user, modify_user_group
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.logic.administration.users.render_users_form import USERNAME, PASSWORD, PASSWORD_CONFIRM, GROUP, name_for_user_and_input_type, \
    new_user, username_from_deletion_button
from app.objects.users_and_security import SkipperManUser, UserGroup


@dataclass
class SkipperManUserFromForm:
    username: str
    password: str
    confirm_password: str
    group: UserGroup



def delete_user_from_user_list(last_button: str):
    username = username_from_deletion_button(last_button)

    delete_username_from_user_list(username)


def save_changes_in_security_form(interface: abstractInterface):
    save_changes_to_existing_users(interface)
    add_new_user_if_present(interface)


def add_new_user_if_present(interface: abstractInterface):
    user_values = get_user_values_from_values_in_form(interface=interface, user=new_user, username_field_present=True)
    if is_user_empty(user_values):
        return
    add_new_user(interface, user_values)

def add_new_user(interface: abstractInterface, user_values: SkipperManUserFromForm):
    invalid_text = is_user_valid_text(user_values)
    if len(invalid_text)==0:
        try:
            add_user_with_values_from_form(user_values)
        except Exception as e:
            invalid_text = "error message %s" % str(e)

    if len(invalid_text)>0:
        interface.log_error("Cannot add user, reasons %s: " % invalid_text)

def add_user_with_values_from_form(user_values: SkipperManUserFromForm):
    try:
        assert user_values.password == user_values.confirm_password
    except:
        raise Exception("passwords don't match")

    print("Trying to add new user %s password %s group %s" % (user_values.username, user_values.password, user_values.group))
    user = SkipperManUser.create(
        username=user_values.username,
        password=user_values.password,
        group=user_values.group
    )

    add_user(user)

def save_changes_to_existing_users(interface: abstractInterface):
    existing_list_of_users = load_all_users()
    for user in existing_list_of_users:
        save_change_to_user_from_form(interface=interface, user=user)

def save_change_to_user_from_form(interface: abstractInterface, user: SkipperManUser):
    user_values_from_form =  get_user_values_from_values_in_form(interface=interface, user=user, username_field_present=False)
    modify_password_if_changed(interface=interface, user=user, user_values_from_form=user_values_from_form)
    modify_group_if_changed(user=user, user_values_from_form=user_values_from_form)

def modify_password_if_changed(interface: abstractInterface, user: SkipperManUser, user_values_from_form: SkipperManUserFromForm):
    if len(user_values_from_form.password)==0 and len(user_values_from_form.confirm_password)==0:
        return

    if user_values_from_form.password!=user_values_from_form.confirm_password:
        interface.log_error("Cannot change password as fields don't match!")

    change_password_for_user(user.username, new_password = user_values_from_form.password)
    interface.log_error("Changed password for %s" % user.username)

def modify_group_if_changed( user: SkipperManUser, user_values_from_form: SkipperManUserFromForm):
    if user.group == user_values_from_form.group:
        return

    modify_user_group(user.username, new_group=user_values_from_form.group)


def get_user_values_from_values_in_form(interface: abstractInterface, user: SkipperManUser, username_field_present: bool = False) -> SkipperManUserFromForm:
    group_str = interface.value_from_form(name_for_user_and_input_type(user, GROUP))
    group = UserGroup[group_str]
    if username_field_present:
        username = interface.value_from_form(name_for_user_and_input_type(user, USERNAME))
    else:
        username = user.username

    return SkipperManUserFromForm(
        username = username,
        password = interface.value_from_form(name_for_user_and_input_type(user, PASSWORD)),
        confirm_password = interface.value_from_form(name_for_user_and_input_type(user, PASSWORD_CONFIRM)),
        group =  group
    )

def is_user_valid_text(user_values: SkipperManUserFromForm):
    valid_error = ""
    if len(user_values.username)<3:
        valid_error+="Username is too short (3 character min). "
    if len(user_values.password)<3:
        valid_error+="Password too short (3 character min). "
    if user_values.password!=user_values.confirm_password:
        valid_error+="Passwords don't match. "
    if already_in_list(user_values.username):
        valid_error+="Username is not unique. "
    return valid_error

def is_user_empty(user_values: SkipperManUserFromForm):
    if len(user_values.username)==0:
        return True


