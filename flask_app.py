import secrets
from pathlib import Path

from werkzeug.middleware.profiler import ProfilerMiddleware

from app.web.documentation.documentation_pages import generate_help_page_html
from app.web.flask.flash import flash_error
from app.web.flask.session_data_for_action import clear_session_data_for_all_actions
from flask import session, Flask, redirect
from flask_login import login_required, LoginManager
from werkzeug import Request

from app.web.flask.security import get_all_flask_users, authenticated_user
from app.web.flask.login_and_out_pages import (
    login_page,
    process_logout,
    login_link_page,
    change_password_page,
)
from app.web.html.make_backup import make_backup_from_menu
from app.web.html.read_only import toggle_read_only
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
)
from app.data_access.configuration.configuration import MAX_FILE_SIZE

Request.max_form_parts = 5000  # avoid large forms crashing


PROFILE = False

#### SETUP


## Do not move these functions out of this file or things break
def prepare_flask_app(max_file_size: int, profile: bool = False) -> Flask:
    ## Secret key
    app = Flask(__name__)
    if profile:
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app)

    SECRET_FILE_PATH = Path(".flask_secret")
    try:
        with SECRET_FILE_PATH.open("r") as secret_file:
            app.secret_key = secret_file.read()
    except FileNotFoundError:
        # Let's create a cryptographically secure code in that file
        with SECRET_FILE_PATH.open("w") as secret_file:
            app.secret_key = secrets.token_hex(32)
            secret_file.write(app.secret_key)

    app.config["SECRET_KEY"] = app.secret_key

    ## Avoid overload
    app.config["MAX_CONTENT_LENGTH"] = max_file_size

    return app


def prepare_login_manager(app: Flask) -> LoginManager:
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_message = "You need to security to use skipperman"

    return login_manager


app = prepare_flask_app(max_file_size=MAX_FILE_SIZE, profile=PROFILE)


login_manager = prepare_login_manager(app)


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
def set_read_only():
    toggle_read_only()
    ## only possible from menu page
    return generate_menu_page_html()


@app.route("/%s/" % MAKE_BACKUP, methods=["GET"])
def make_backup():
    make_backup_from_menu()
    ## only possible from menu page
    return generate_menu_page_html()


@app.route("/%s/" % "link_login", methods=["GET"])
def link_login():
    return login_link_page()


@app.route("/%s/" % LOGOUT_URL)
@login_required
def logout():
    return process_logout()


@app.route(INDEX_URL)
def home():
    clear_session_data_for_all_actions()
    return generate_menu_page_html()


@app.route("/%s/<action_option>" % ACTION_PREFIX, methods=["GET", "POST"])
@login_required
def action(action_option):
    if not authenticated_user():
        ## belt and braces on security
        print("USER NOT LOGGED IN")
        return generate_menu_page_html()

    return generate_action_page_html(action_option)


@app.route("/%s/<help_page_name>" % HELP_PREFIX, methods=["GET", "POST"])
@login_required
def help(help_page_name):
    return generate_help_page_html(help_page_name)


@app.errorhandler(500)
def generic_web_error(e):
    flash_error("Some kind of error - contact support (%s)" % str(e))
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
