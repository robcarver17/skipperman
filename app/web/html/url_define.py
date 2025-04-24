from app.objects.abstract_objects.abstract_interface import UrlsOfInterest
from app.objects.utilities.exceptions import arg_not_passed

HOME = "Home"
INDEX_URL = "/"
ACTION_PREFIX = "action"
HELP_PREFIX = "help"
LOGIN_URL = "login"
LOGOUT_URL = "logout"
LINK_LOGIN = "link_login"
CHANGE_PASSWORD = "change_password"
TOGGLE_READ_ONLY = "toggle_read_only"
STATIC_DIRECTORY = "static"
MAKE_BACKUP = "make_backup"
MAIN_MENU_URL = '/main/'


def get_action_url(action_name: str):
    return "/%s/%s" % (ACTION_PREFIX, action_name)


def get_help_url(help_page_name: str):
    if len(help_page_name) == 0:
        return ""
    return "/%s/%s" % (HELP_PREFIX, help_page_name)


def get_urls_of_interest(action_name: str = arg_not_passed) -> UrlsOfInterest:
    return UrlsOfInterest(
        current_url_for_action=get_current_url_from_action_name(action_name),
        image_directory=get_image_directory_url(),
    )


def get_current_url_from_action_name(action_name: str = arg_not_passed) -> str:
    if action_name is arg_not_passed:
        return INDEX_URL

    return get_action_url(action_name)


def get_image_directory_url():
    return "/" + STATIC_DIRECTORY
