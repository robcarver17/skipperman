import os.path
import secrets
from pathlib import Path

from werkzeug.middleware.profiler import ProfilerMiddleware

from app.data_access.init_data import home_directory
from app.web.documentation.documentation_pages import generate_help_page_html
from app.web.flask.flash import flash_error
from app.web.flask.session_data_for_action import (
    clear_all_action_state_data_from_session,
)
from app.web.html.config_html import PROFILE

from flask import session, Flask, redirect, url_for
from flask_login import login_required, LoginManager
from werkzeug import Request

from app.web.flask.security import get_all_flask_users, authenticated_user
from app.web.flask.login_and_out_pages import (
    login_page,
    process_logout,
    login_link_page,
    change_password_page,
)
from app.web.html.login_and_out import is_admin_user
from app.web.html.make_backup import make_backup_from_menu
from app.web.html.read_only import toggle_read_only_local, toggle_read_only_global
from app.web.menus.menu_pages import generate_menu_page_html
from app.web.actions.action_pages import generate_action_page_html
from app.web.html.url_define import (
    INDEX_URL,
    ACTION_PREFIX,
    LOGIN_URL,
    LOGOUT_URL,
    CHANGE_PASSWORD,
    TOGGLE_READ_ONLY,
    HELP_PREFIX,
    MAKE_BACKUP,
    MAIN_MENU_URL,
    TOGGLE_READ_ONLY_GLOBAL,
    LINK_LOGIN,
)
from app.data_access.configuration.configuration import MAX_FILE_SIZE, SUPPORT_EMAIL

MEGABYTE = (2**10) ** 2


## Do not move these functions out of this file or things break


def prepare_flask_app(max_file_size: int, profile: bool = False) -> Flask:
    ## Secret key
    app = Flask(__name__)
    if profile:
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app)

    secret_key = get_secret_key_from_file_creating_if_required
    app.config["SECRET_KEY"] = app.secret_key = secret_key

    ## Avoid overload
    app.config["MAX_CONTENT_LENGTH"] = max_file_size * MEGABYTE
    app.config["MAX_FORM_MEMORY_SIZE"] = None  ## avoids large forms breaking
    app.config["MAX_FORM_PARTS"] = None  ## avoids large forms breaking

    return app


def get_secret_key_from_file_creating_if_required():
    SECRET_FILE = os.path.join(home_directory, ".flask_secret")

    try:
        with open(SECRET_FILE, "r") as secret_file:
            secret_key = secret_file.read()
    except FileNotFoundError:
        # Let's create a cryptographically secure code in that file
        with open(SECRET_FILE, "w") as secret_file:
            secret_key = secrets.token_hex(32)
            secret_file.write(app.secret_key)

    return secret_key


def prepare_request(max_file_size):
    Request.max_form_parts = None  # avoid large forms crashing
    Request.max_form_memory_size = None
    Request.max_content_length = max_file_size * MEGABYTE


def prepare_login_manager(app: Flask) -> LoginManager:
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_message = "You need to security to use skipperman"

    return login_manager


###SETUP
prepare_request(max_file_size=MAX_FILE_SIZE)
app = prepare_flask_app(max_file_size=MAX_FILE_SIZE, profile=PROFILE)
app.secret_key = "a;lsjfd;lkasdfiawers"

login_manager = prepare_login_manager(app)


## @APP MAGIC


## ensures cookies persists between sessions
@app.before_request
def setup():
    session.permanent = True


## login manager
@login_manager.user_loader
def load_user(user_id):
    all_flask_users = get_all_flask_users()
    return all_flask_users.get(user_id)


### ENTRY POINTS
@app.route("/%s/" % LOGIN_URL, methods=["GET", "POST"])
def login():
    return login_page()


@app.route("/%s/" % CHANGE_PASSWORD, methods=["GET", "POST"])
def change_password():
    return change_password_page()


@app.route("/%s/" % TOGGLE_READ_ONLY, methods=["GET"])
def set_read_only_local():
    toggle_read_only_local()
    ## only possible from menu page
    return generate_menu_page_html()


@app.route("/%s/" % TOGGLE_READ_ONLY_GLOBAL, methods=["GET"])
def set_read_only_global():
    if is_admin_user():
        toggle_read_only_global()
    ## only possible from menu page
    return generate_menu_page_html()


@app.route("/%s/" % MAKE_BACKUP, methods=["GET"])
@login_required
def make_backup():
    make_backup_from_menu()
    ## only possible from menu page
    return generate_menu_page_html()


@app.route("/%s/" % LINK_LOGIN, methods=["GET"])
def link_login():
    return login_link_page()


@app.route("/%s/" % LOGOUT_URL)
@login_required
def logout():
    return process_logout()


@app.route("/%s/<action_option>" % ACTION_PREFIX, methods=["GET", "POST"])
@login_required
def action(action_option):
    if not authenticated_user():
        ## belt and braces on security
        print("USER NOT LOGGED IN")
        return generate_menu_page_html()
    else:
        return generate_action_page_html(action_option)


@app.route(MAIN_MENU_URL, methods=["GET", "POST"])
def main_menu():
    clear_all_action_state_data_from_session()
    return generate_menu_page_html()


@app.route("/%s/<help_page_name>" % HELP_PREFIX, methods=["GET", "POST"])
@login_required
def help(help_page_name):
    return generate_help_page_html(help_page_name)


@app.errorhandler(500)
def generic_web_error(e):
    flash_error(
        "Some kind of error (%s) contact support: %s " % (str(e), SUPPORT_EMAIL)
    )
    return generate_menu_page_html()


@app.errorhandler(404)
def generic_missing_page_error(e):
    flash_error(
        "Missing page error (%s) contact support: %s " % (str(e), SUPPORT_EMAIL)
    )
    return generate_menu_page_html()


## We do this otherwise the index url gets randomly called and changes state
@app.route(INDEX_URL)
def home():
    return redirect(MAIN_MENU_URL)


if __name__ == "__main__":
    app.run(debug=True)
