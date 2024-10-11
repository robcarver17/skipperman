from app.web.html.read_only import  is_read_only

from app.web.html.url_define import LOGIN_URL, LOGOUT_URL, CHANGE_PASSWORD, TOGGLE_READ_ONLY, MAKE_BACKUP
from app.web.flask.security import get_username


def get_login_link_html_code():
    return (
        '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">Login</a>'
        % LOGIN_URL
    )


def get_read_write_logout_and_change_password_link_html_code(
    include_read_only_toggle: bool,
    include_backup_option: bool = False
):
    if include_read_only_toggle:
        read_only_html_string = read_only_or_not_html()
    else:
        ## don't offer the option or will get messed up
        read_only_html_string = ""

    if include_backup_option:
        backup_html_string = make_backup_html()
    else:
        backup_html_string = ""

    return backup_html_string + read_only_html_string + logout_html_string + change_password_html_string


logout_html_string = (
    '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">Logout</a>' % LOGOUT_URL
)
change_password_html_string = (
    '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">Change password</a>'
    % CHANGE_PASSWORD
)


def get_username_banner():
    try:
        return "Logged in as: %s" % get_username()
    except:
        return "Login to see menus"


def read_only_or_not_html():
    if is_read_only():
        inner_text = "Read only: Click to change"
    else:
        inner_text = "Click for read only"

    return '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">%s</a>' % (
        TOGGLE_READ_ONLY,
        inner_text,
    )

def make_backup_html():

    return '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">%s</a>' % (
        MAKE_BACKUP,
        "Snapshot data",
    )