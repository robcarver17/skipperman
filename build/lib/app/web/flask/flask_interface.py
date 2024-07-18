from dataclasses import dataclass

import flask
from werkzeug.exceptions import RequestEntityTooLarge

from app.data_access.data import data_api
from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
    UrlsOfInterest,
)
from app.web.flask.flash import flash_error
from app.web.flask.security import get_username

from app.web.flask.session_data_for_action import (
    SessionDataForAction,
    clear_session_data_for_action,
)
from app.web.html.forms import html_as_date
from app.web.html.components import HTML_BUTTON_NAME
from app.web.html.read_only import is_read_only
from app.web.html.url import get_action_url, LINK_LOGIN, STATIC_DIRECTORY, INDEX_URL
from app.objects.exceptions import (
    NoFileUploaded,
    missing_data,
    arg_not_passed,
    NoButtonPressed,
)
from flask import request


@dataclass
class flaskInterface(abstractInterface):
    def log_error(self, error_message: str):
        flash_error(error_message)

    def get_persistent_value(self, key, default=missing_data):
        return self.session_data.get_value(key, default=default)

    def set_persistent_value(self, key, value):
        self.session_data.set_value(key, value)

    def clear_persistent_value(self, key):
        self.session_data.delete_persistent_value(key)

    def list_of_keys_with_persistent_values(self) -> list:
        return self.session_data.list_of_keys_with_persistent_values()

    @property
    def is_initial_stage_form(self) -> bool:
        return self.session_data.is_initial_stage

    def reset_to_initial_stage_form(self):
        self.session_data.reset_to_initial_stage()

    @property
    def form_name(self) -> str:
        return self.session_data.stage

    @form_name.setter
    def form_name(self, new_stage):
        self.session_data.stage = new_stage

    def clear_persistent_data_for_action_and_reset_to_initial_stage_form(self):
        self.reset_to_initial_stage_form()  ## this should happen anyway, but belt and braces
        clear_session_data_for_action(self.action_name)

    def clear_persistent_data_except_specified_fields(self, specified_fields: list):
        all_keys = self.list_of_keys_with_persistent_values()
        for key in all_keys:
            if key in specified_fields:
                continue
            self.clear_persistent_value(key)

    @property
    def is_posted_form(self) -> bool:
        return is_website_post()

    def value_from_form(self, key: str, value_is_date: bool = False):
        try:
            value = get_value_from_form(key)
        except:
            raise Exception("Value %s not found in form" % key)
        if value_is_date:
            value = html_as_date(value)

        return value

    def value_of_multiple_options_from_form(
        self, key: str, default=arg_not_passed
    ) -> list:
        try:
            list_of_values = get_list_from_form(key)
        except:
            if default is arg_not_passed:
                raise Exception("Value %s not found in form" % key)
            else:
                return default

        return list_of_values

    def last_button_pressed(self, button_name=arg_not_passed) -> str:
        return get_last_button_pressed(button_name)

    @property
    def session_data(
        self,
    ) -> SessionDataForAction:  ## pipe through to current session object
        return SessionDataForAction(self.action_name)

    @property
    def current_url(self) -> str:
        return get_action_url(self.action_name)

    def uploaded_file(self, input_name: str = "file"):
        print("inside state")
        return uploaded_file(input_name)

    def url_for_password_reset(self, username: str, new_password: str):
        url = self.main_url()
        print(url)

        return "%s%s/?username=%s&password=%s" % (
            url,
            LINK_LOGIN,
            username,
            new_password,
        )

    def main_url(self):
        return flask.request.host_url

    def get_current_logged_in_username(self) -> str:
        return get_username()

    @property
    def read_only(self):
        return is_read_only()


READ_ONLY_KEY = "__read_only"


def is_website_post() -> bool:
    return request.method == "POST"


def get_value_from_form(key: str):
    return request.form[key]


def get_list_from_form(key: str):
    return request.form.getlist(key)


def get_last_button_pressed(button_name: str = arg_not_passed) -> str:
    if button_name == arg_not_passed:
        button_name = HTML_BUTTON_NAME
    print("Testing press of %s" % button_name)
    try:
        return request.form.get(button_name, "")
    except RequestEntityTooLarge:
        raise RequestEntityTooLarge

    raise NoButtonPressed


def uploaded_file(input_name: str = "file"):
    print("inside uploaded file")
    print(request.files.keys())
    file = request.files.get(input_name, None)
    if file is None:
        print("no file")

        raise NoFileUploaded()
    return file


def get_urls_of_interest(action_name: str = arg_not_passed) -> UrlsOfInterest:
    return UrlsOfInterest(
        current_url_for_action=get_current_url_from_action_name(action_name),
        image_directory=get_image_directory_url(),
    )


def get_current_url_from_action_name(action_name: str = arg_not_passed) -> str:
    if action_name is arg_not_passed:
        return INDEX_URL
    interface = flaskInterface(action_name=action_name, data=data_api)
    return interface.current_url


def get_image_directory_url():
    abstractInterface = flaskInterface(data=data_api)
    home_page = abstractInterface.main_url()
    return "/" + STATIC_DIRECTORY
