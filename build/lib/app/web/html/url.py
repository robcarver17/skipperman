HOME = "Home"
INDEX_URL = "/"
MENU_PREFIX = "menu"
ACTION_PREFIX = "action"
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LINK_LOGIN= 'link_login'
CHANGE_PASSWORD = 'change_password'
def get_action_url(action_name: str):
    return "/%s/%s" % (ACTION_PREFIX, action_name)


def get_menu_url(menu_name: str):
    return "/%s/%s" % (MENU_PREFIX, menu_name)

