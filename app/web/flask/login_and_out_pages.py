from flask import request, render_template

from flask_login import login_user, logout_user

from app.backend.security.modify_user import change_password_for_user
from app.objects.users_and_security import (
    default_admin_user_if_none_defined,
    ADMIN_GROUP,
    SKIPPER_GROUP,
)
from app.web.flask.flash import flash_error, flash_log
from app.web.flask.security import (
    get_all_flask_users,
    get_username,
    get_access_group_for_current_user,
)
from app.web.menus.menu_pages import generate_menu_page_html


# If using template these need to match
USERNAME = "username"
PASSWORD = "password"
PASSWORD2 = "password2"


def login_page():
    if request.method == "GET":
        return display_login_form()
    else:
        username = request.form[USERNAME]
        password = request.form[PASSWORD]

        return process_login(username=username, password=password)


def change_password_page():
    if request.method == "GET":
        return display_change_password_page()
    else:
        password = request.form[PASSWORD]
        confirm_password = request.form[PASSWORD2]
        return change_password(password, confirm_password)


def change_password(password, confirm_password):
    if password != confirm_password:
        flash_error("Passwords dont match!")
        return generate_menu_page_html()

    username = get_username()
    try:
        change_password_for_user(username, new_password=password)
        flash_error("Password changed")
    except Exception as e:
        flash_error("Couldn't change password error %s" % str(e))
    return generate_menu_page_html()


def display_change_password_page():
    return render_template("change_password.html")


def login_link_page():
    username = request.args.get("username")
    password = request.args.get("password")
    flash_log("CHANGE YOUR PASSWORD NOW %s!" % get_username())
    return process_login(username=username, password=password)


def display_login_form():
    return render_template("login_page.html")


def display_login_form_on_user_error():
    return render_template("login_page_user_error.html")


def display_login_form_on_password_error():
    return render_template("login_page_password_error.html")


"""
    print("login page")
    message = html_line_wrapper.wrap_around(get_html_of_flashed_messages())
    username = html_line_wrapper.wrap_around(html_form_text_input(input_label="Username", input_name=USERNAME))
    password = html_line_wrapper.wrap_around(html_form_password_input(input_label="Password", input_name=PASSWORD))
    button = html_line_wrapper.wrap_around(html_button("Log in"))

    return login_html_wrapper.wrap_around(message+username+password+button)

login_html_wrapper = HtmlWrapper(
    html_container_wrapper.wrap_around(Html("%s"))
            )
"""


def process_login(username: str, password: str):
    all_flask_users = get_all_flask_users()
    if username not in all_flask_users:
        print("User %s not known in %s" % (username, str(all_flask_users)))
        return display_login_form_on_user_error()

    user = all_flask_users[username]

    if not user.check_password(password):
        print("Password for user %s not recognised" % password)
        return display_login_form_on_password_error()

    login_user(user)

    if username == default_admin_user_if_none_defined.username:
        flash_error(
            "USING DEFAULT ADMIN USER BECAUSE NO SECURITY FILE CREATED YET - ADD A PROPER ADMIN USER ASAP!! (Use Administration Menu)"
        )

    flash_log(welcome_message_for_user())

    return generate_menu_page_html()


def welcome_message_for_user():
    usernmae = get_username()
    access_group = get_access_group_for_current_user()

    if access_group == SKIPPER_GROUP:
        return (
            "Welcome skipper %s! (well, skipper or not you have skipper access privileges)"
            % usernmae
        )
    elif access_group == ADMIN_GROUP:
        return "Welcome oh mighty admin user %s!" % usernmae
    else:
        return


def process_logout():
    logout_user()

    return generate_menu_page_html()
