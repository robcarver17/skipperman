from dataclasses import dataclass

from app.backend.security.list_of_users import get_list_of_users

from app.objects.volunteers import Volunteer

from app.backend.volunteers.list_of_volunteers import (
    get_volunteer_from_list_of_given_str_of_volunteer,
)

from app.backend.security.modify_user import (
    change_password_for_user,
    modify_user_group,
    modify_volunteer_for_user,
    generate_reset_message,
)
from app.backend.security.list_of_users import (
    delete_user_from_user_list,
    add_user,
    already_in_list,
)

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.frontend.administration.users.render_users_form import (
    USERNAME,
    PASSWORD,
    PASSWORD_CONFIRM,
    GROUP,
    name_for_user_and_input_type,
    new_user,
    username_from_deletion_button,
    VOLUNTEER,
    username_from_reset_button,
)
from app.objects.users_and_security import SkipperManUser, UserGroup


@dataclass
class SkipperManUserFromForm:
    username: str
    password: str
    confirm_password: str
    group: UserGroup
    volunteer: Volunteer
    email: str = ""


def delete_selected_user_from_user_list(interface: abstractInterface, last_button: str):
    username = username_from_deletion_button(last_button)
    print("deleting %s" % username)
    delete_user_from_user_list(object_store=interface.object_store, username=username)


def generate_reset_message_for_user_name(
    last_button: str, interface: abstractInterface
):
    username = username_from_reset_button(last_button)
    return generate_reset_message(
        username=username, object_store=interface.object_store
    )


def add_new_user_if_present(interface: abstractInterface):
    user_values = get_user_values_from_values_in_form(
        interface=interface, user=new_user, username_field_present=True
    )
    if is_user_empty(user_values):
        return
    add_new_user(interface, user_values)


def add_new_user(interface: abstractInterface, user_values: SkipperManUserFromForm):
    invalid_text = is_user_valid_text(interface=interface, user_values=user_values)
    if len(invalid_text) == 0:
        try:
            add_user_with_values_from_form(interface=interface, user_values=user_values)
        except Exception as e:
            invalid_text = "error message %s" % str(e)

    if len(invalid_text) > 0:
        interface.log_error("Cannot add user, reasons %s: " % invalid_text)


def add_user_with_values_from_form(
    interface: abstractInterface, user_values: SkipperManUserFromForm
):
    try:
        assert user_values.password == user_values.confirm_password
    except:
        ## should already be checked
        raise Exception("Passwords don't match")

    print(
        "Trying to add new user %s password %s group %s"
        % (user_values.username, user_values.password, user_values.group)
    )

    user = SkipperManUser.create(
        username=user_values.username,
        password=user_values.password,
        group=user_values.group,
        email_address=user_values.email,
        volunteer=user_values.volunteer,
    )

    add_user(object_store=interface.object_store, user=user)


def save_changes_to_existing_users(interface: abstractInterface):
    try:
        existing_list_of_users = get_list_of_users(object_store=interface.object_store)
        for user in existing_list_of_users:
            save_change_to_user_from_form(interface=interface, user=user)
    except Exception as e:
        interface.log_error("Error updating users %s" % str(e))
        interface.clear_cache()


def save_change_to_user_from_form(interface: abstractInterface, user: SkipperManUser):
    user_values_from_form = get_user_values_from_values_in_form(
        interface=interface, user=user, username_field_present=False
    )
    modify_password_if_changed(
        interface=interface, user=user, user_values_from_form=user_values_from_form
    )
    modify_group_if_changed(
        interface=interface, user=user, user_values_from_form=user_values_from_form
    )
    modify_volunteer_if_changed(
        interface=interface, user=user, user_values_from_form=user_values_from_form
    )


def modify_password_if_changed(
    interface: abstractInterface,
    user: SkipperManUser,
    user_values_from_form: SkipperManUserFromForm,
):
    if (
        len(user_values_from_form.password) == 0
        and len(user_values_from_form.confirm_password) == 0
    ):
        return

    if user_values_from_form.password != user_values_from_form.confirm_password:
        interface.log_error("Cannot change password as fields don't match!")
        return

    change_password_for_user(
        object_store=interface.object_store,
        username=user.username,
        new_password=user_values_from_form.password,
    )
    interface.log_error("Changed password for %s" % user.username)


def modify_group_if_changed(
    interface: abstractInterface,
    user: SkipperManUser,
    user_values_from_form: SkipperManUserFromForm,
):
    if user.group == user_values_from_form.group:
        return

    modify_user_group(
        object_store=interface.object_store,
        username=user.username,
        new_group=user_values_from_form.group,
    )


def modify_volunteer_if_changed(
    interface: abstractInterface,
    user: SkipperManUser,
    user_values_from_form: SkipperManUserFromForm,
):
    if user.volunteer_id == user_values_from_form.volunteer.id:
        return

    modify_volunteer_for_user(
        object_store=interface.object_store,
        username=user.username,
        volunteer=user_values_from_form.volunteer,
    )


def get_user_values_from_values_in_form(
    interface: abstractInterface,
    user: SkipperManUser,
    username_field_present: bool = False,
) -> SkipperManUserFromForm:
    group_str = interface.value_from_form(name_for_user_and_input_type(user, GROUP))
    group = UserGroup[group_str]
    if username_field_present:
        username = interface.value_from_form(
            name_for_user_and_input_type(user, USERNAME)
        )
    else:
        username = user.username
    # email = interface.value_from_form(name_for_user_and_input_type(user, EMAIL))
    volunteer_name = interface.value_from_form(
        name_for_user_and_input_type(user, VOLUNTEER)
    )
    volunteer = get_volunteer_from_list_of_given_str_of_volunteer(
        object_store=interface.object_store, volunteer_as_str=volunteer_name
    )

    return SkipperManUserFromForm(
        username=username,
        password=interface.value_from_form(
            name_for_user_and_input_type(user, PASSWORD)
        ),
        confirm_password=interface.value_from_form(
            name_for_user_and_input_type(user, PASSWORD_CONFIRM)
        ),
        group=group,
        volunteer=volunteer,
    )


def is_user_valid_text(
    interface: abstractInterface, user_values: SkipperManUserFromForm
):
    valid_error = ""
    if len(user_values.username) < 3:
        valid_error += "Username is too short (3 character min). "
    if len(user_values.password) < 3:
        valid_error += "Password too short (3 character min). "
    if user_values.password != user_values.confirm_password:
        valid_error += "Passwords don't match. "
    if already_in_list(
        object_store=interface.object_store, username=user_values.username
    ):
        valid_error += "Username is not unique. "
    return valid_error


def is_user_empty(user_values: SkipperManUserFromForm):
    if len(user_values.username) == 0:
        return True
