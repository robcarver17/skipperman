from flask import Flask
from flask_login import LoginManager, login_required

from app.web.flask.security import get_all_flask_users, authenticated_user
from app.web.flask.login_and_out_pages import display_login_form, login_page, process_logout, USERNAME, PASSWORD
from app.web.menu_pages import generate_menu_page_html
from app.web.action_pages import generate_action_page_html
from app.web.html.url import INDEX_URL, ACTION_PREFIX, MENU_PREFIX, LOGIN_URL, LOGOUT_URL
from app.data_access.configuration.configuration import SECRET_KEY, MAX_FILE_SIZE

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

app.secret_key = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = "You need to security to use skipperman"


@login_manager.user_loader
def load_user(user_id):
    all_flask_users = get_all_flask_users()
    return all_flask_users.get(user_id)


@app.route("/%s/" % LOGIN_URL, methods=["GET", "POST"])
def login():
    return login_page()


@app.route("/%s/" % LOGOUT_URL)
@login_required
def logout():
    return process_logout()


## Two types of entry point:
@app.route(INDEX_URL)
def home():
    return generate_menu_page_html()


@app.route("/%s/<action_option>" % ACTION_PREFIX, methods=["GET", "POST"])
@login_required
def action(action_option):
    if not authenticated_user():
        ## belt and braces on security
        print("USER NOT LOGGED IN")
        return generate_menu_page_html()

    return generate_action_page_html(action_option)


if __name__ == "__main__":
    app.run(debug=True)
