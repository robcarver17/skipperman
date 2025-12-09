from app.objects.abstract_objects.form_function_mapping import HOME_PAGE_OF_ACTION
from app.objects.abstract_objects.abstract_interface import UrlsOfInterest
from app.objects.utilities.exceptions import arg_not_passed

INDEX_URL = "/"
ACTION_PREFIX = "action"
HELP_PREFIX = "help"
FILE_URL = "file"
LOGIN_URL = "login"
LOGOUT_URL = "logout"
LINK_LOGIN = "link_login"
CHANGE_PASSWORD = "change_password"
TOGGLE_READ_ONLY = "toggle_read_only"
TOGGLE_READ_ONLY_GLOBAL = "toggle_read_only_global"
STATIC_DIRECTORY = "static"
MAKE_BACKUP = "make_backup"
MAIN_MENU_URL = "/main/"
MAIN_HELP_PAGE = "main-menu"


def get_help_url(help_page_name: str):
    if len(help_page_name) == 0:
        return ""
    return "/%s/%s" % (HELP_PREFIX, help_page_name)


def get_urls_of_interest(action_name: str = arg_not_passed) -> UrlsOfInterest:
    return UrlsOfInterest(
        image_directory=get_image_directory_url(),
    )




def get_image_directory_url():
    return "/" + STATIC_DIRECTORY


def get_action_first_page_url(action_name: str):
    return get_action_url_for_form(action_name, HOME_PAGE_OF_ACTION)


def get_action_url_for_form(action_name: str, form_name:str):
    return "/%s/%s/%s" % (ACTION_PREFIX, action_name, form_name)
