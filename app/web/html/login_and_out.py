from app.web.html.read_only import read_only_or_not_html

from app.web.html.url import LOGIN_URL, LOGOUT_URL, CHANGE_PASSWORD
from app.web.flask.security import get_username


def get_login_link_html_code():
    return (
        '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">Login</a>'
        % LOGIN_URL
    )


def get_read_write_logout_and_chanage_password_link_html_code(
    include_read_only_toggle: bool,
):
    if include_read_only_toggle:
        read_only_html_string = read_only_or_not_html()
    else:
        ## don't offer the option or will get messed up
        read_only_html_string = ""

    return read_only_html_string + logout_html_string + change_password_html_string


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
