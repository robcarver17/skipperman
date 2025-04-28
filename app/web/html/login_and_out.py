from app.web.html.read_only import is_read_only, is_local_read_only, is_global_read_only

from app.web.html.url_define import (
    LOGIN_URL,
    LOGOUT_URL,
    CHANGE_PASSWORD,
    TOGGLE_READ_ONLY,
    MAKE_BACKUP, TOGGLE_READ_ONLY_GLOBAL,
)
from app.web.flask.security import get_username, get_access_group_for_current_user


def get_login_link_html_code():
    return (
        '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">Login</a>'
        % LOGIN_URL
    )


from app.objects.users_and_security import UserGroup, ADMIN_GROUP


def get_read_write_logout_and_change_password_link_html_code(
    include_read_only_toggle: bool, include_backup_option: bool = False
):
    read_only_html_string = read_only_or_not_html(include_read_only_toggle)

    if include_backup_option:
        backup_html_string = make_backup_html()
    else:
        backup_html_string = ""

    return (
        backup_html_string
        + read_only_html_string
        + logout_html_string
        + change_password_html_string
    )


logout_html_string = (
    '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">Logout</a>' % LOGOUT_URL
)
change_password_html_string = (
    '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">Change password</a>'
    % CHANGE_PASSWORD
)


def get_username_banner():
    try:
        group = get_access_group_for_current_user()
        return "Logged in as: %s (%s)" % (get_username(), group.name)
    except:
        return ""


def read_only_or_not_html(include_read_only_toggle: bool):
    if include_read_only_toggle:
        return read_only_or_not_when_can_be_set()
    else:
        return read_only_or_not_when_cannot_be_set()

def read_only_or_not_when_can_be_set():
    if is_admin_user():
        return read_only_or_not_when_can_be_set_and_admin_user()
    else:
        return read_only_or_not_when_can_be_set_and_non_admin_user()

def read_only_or_not_when_can_be_set_and_admin_user():
    if is_read_only():
        if is_global_read_only():
            return unset_global_message()
        elif is_local_read_only():
            return unset_local_message()
        else:
            raise Exception
    else:
        return set_global_message()+"    "+set_local_message_for_admin()


def read_only_or_not_when_can_be_set_and_non_admin_user():
    if is_local_read_only():
        return unset_local_message()
    else:
        return set_local_message_for_non_admin()

def read_only_or_not_when_cannot_be_set():
    if is_global_read_only():
        return read_only_global_message
    elif is_local_read_only():
        return read_only_local_message
    elif not is_read_only():
        return ""
    else:
        raise Exception("Weird read only state")

read_only_global_message = "SKIPPERMAN READ ONLY MODE SET BY ADMIN USER - contact support - saves will not be changed."
read_only_local_message = "Read only - changes will not be saved"



def is_admin_user():
    access_group = get_access_group_for_current_user()
    return access_group == ADMIN_GROUP



def set_global_message():
    inner_text = "Click for GLOBAL read only - will affect all Skipperman users"

    return '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">%s</a>' % (
        TOGGLE_READ_ONLY_GLOBAL,
        inner_text,
    )

def unset_global_message():
    inner_text = "GLOBAL READ ONLY MODE - applies to all users - click to turn off"

    return '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">%s</a>' % (
        TOGGLE_READ_ONLY_GLOBAL,
        inner_text,
    )

def set_local_message_for_admin():
    inner_text = "Click for read only (your user session only)"

    return '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">%s</a>' % (
        TOGGLE_READ_ONLY,
        inner_text,
    )

def set_local_message_for_non_admin():
    inner_text = "Click for read only"

    return '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">%s</a>' % (
        TOGGLE_READ_ONLY,
        inner_text,
    )

def unset_local_message():
    inner_text = "Read only: Click to change"

    return '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">%s</a>' % (
        TOGGLE_READ_ONLY,
        inner_text,
    )

def make_backup_html():
    return '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">%s</a>' % (
        MAKE_BACKUP,
        "Snapshot data",
    )
