from app.web.html.url import LOGIN_URL,LOGOUT_URL
from app.web.flask.security import get_username

def get_login_link_html_code():
    return '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">Login</a>' % LOGIN_URL

def get_logout_link_html_code():
    return '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">Logout</a>' % LOGOUT_URL

def get_username_banner():
    try:
        return "Logged in as: %s" % get_username()
    except:
        return 'Login to see menus'
