
from flask import request, render_template

from flask_login import login_user, logout_user

from app.objects.users_and_security import default_admin_user_if_none_defined
from app.web.flask.flash import flash_error, flash_log, get_html_of_flashed_messages
from app.web.flask.security import get_all_flask_users, get_username
from app.web.html.forms import html_form_text_input, html_form_password_input, html_button
from app.web.html.components import html_line_wrapper, HtmlWrapper, html_container_wrapper, Html
from app.web.menu_pages import generate_menu_page_html


# If using template these need to match
USERNAME='username'
PASSWORD = 'password'


def login_page():
    if request.method == "GET":
        return display_login_form()
    else:
        return process_login()


def display_login_form():
    return render_template("login_page.html")
    #return render_template("test.html")

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

def process_login():

    username = request.form[USERNAME]
    password = request.form[PASSWORD]
    all_flask_users = get_all_flask_users()
    if username not in all_flask_users:
        print("User %s not known in %s" % (username, str(all_flask_users)))
        flash_error("User %s not known" % username)
        return display_login_form()

    user = all_flask_users[username]

    if not user.check_password(password):
        flash_error("Password for user %s not recognised" % password)
        return display_login_form()

    login_user(user)

    if username ==default_admin_user_if_none_defined.username:
        flash_error("USING DEFAULT ADMIN USER BECAUSE NO SECURITY FILE CREATED YET - ADD A PROPER ADMIN USER ASAP!! (Use Administration Menu)")

    flash_log("Welcome %s!" % get_username())

    return generate_menu_page_html()


def process_logout():
    logout_user()

    return generate_menu_page_html()
