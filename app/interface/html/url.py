HOME = 'Home'
INDEX_URL = "/"
MENU_PREFIX="menu"
ACTION_PREFIX = "action"

def get_action_url(action_name: str):
    return '/%s/%s' % (ACTION_PREFIX, action_name)

def get_menu_url(menu_name: str):
    return '/%s/%s' % (MENU_PREFIX, menu_name)
