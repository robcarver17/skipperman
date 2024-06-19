HOME = "Home"
INDEX_URL = "/"
ACTION_PREFIX = "action"
HELP_PREFIX = "help"
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LINK_LOGIN= 'link_login'
CHANGE_PASSWORD = 'change_password'
TOGGLE_READ_ONLY = 'toggle_read_only'
STATIC_DIRECTORY = 'static'
def get_action_url(action_name: str):
    return "/%s/%s" % (ACTION_PREFIX, action_name)

def get_help_url(help_page_name: str):
    if len(help_page_name)==0:
        return ''
    return "/%s/%s" % (HELP_PREFIX, help_page_name)
