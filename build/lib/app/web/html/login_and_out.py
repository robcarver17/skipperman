from app.web.html.url import LOGIN_URL,LOGOUT_URL, CHANGE_PASSWORD
from app.web.flask.security import get_username

def get_login_link_html_code():
    return '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">Login</a>' % LOGIN_URL

def get_logout_and_chanage_password_link_html_code():
    logout = '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">Logout</a>' % LOGOUT_URL
    change_password = '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">Change password</a>' % CHANGE_PASSWORD
    return logout+change_password

def get_username_banner():
    try:
        return "Logged in as: %s" % get_username()
    except:
        return 'Login to see menus'
