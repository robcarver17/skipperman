from copy import copy
from dataclasses import dataclass

from werkzeug.exceptions import RequestEntityTooLarge

from app.objects.abstract_objects.abstract_interface import (
    abstractInterface,
)
from app.web.flask.flash import flash_error
from app.web.flask.security import get_username

from app.web.html.forms import html_as_date
from app.web.html.abstract_components_to_html import HTML_BUTTON_NAME
from app.web.end_points.read_only import is_read_only
from app.objects.utilities.exceptions import (
    NoFileUploaded,
    arg_not_passed,
)
from flask import request


@dataclass
class flaskInterface(abstractInterface):
    def log_error(self, error_message: str):
        flash_error(error_message)

    @property
    def is_posted_form(self) -> bool:
        return is_website_post()

    def value_from_form(
        self, key: str, default=arg_not_passed,  value_is_date: bool = False
    ):
        try:
            value = get_value_from_form(key)
        except:
            print("%s missing from form, only have keys %s" % (key, str(all_keys_in_form())))
            if default is arg_not_passed:
                raise Exception("Value %s not found in form" % key)
            else:
                return default

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

    def last_button_pressed(self) -> str:
        return get_last_button_pressed()


    def uploaded_file(self, input_name: str = "file"):
        return uploaded_file(input_name)

    def get_current_logged_in_username(self) -> str:
        return get_username()

    @property
    def local_read_only(self):
        return is_read_only()


def is_website_post() -> bool:
    return request.method == "POST"


def get_value_from_form(key: str):
    return request.form[key]

def all_keys_in_form():
    return list(request.form.keys())

def get_list_from_form(key: str):
    return request.form.getlist(key)


def get_last_button_pressed() -> str:
    try:
        return request.form.get(HTML_BUTTON_NAME, "")
    except RequestEntityTooLarge:
        raise RequestEntityTooLarge


def uploaded_file(input_name: str = "file"):
    file = request.files.get(input_name, None)
    if file is None:
        print("no file")

        raise NoFileUploaded()
    return file
