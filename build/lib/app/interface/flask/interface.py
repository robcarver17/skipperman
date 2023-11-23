from app.logic.abstract_interface import abstractInterface
from app.interface.flask.flash import flash_log, flash_error

from app.interface.flask.session_data_for_action import (
    SessionDataForAction,
    clear_session_data_for_action,
    clear_session_data_for_all_actions,
)
from app.interface.html.forms import HTML_BUTTON_NAME, html_as_date
from app.interface.html.url import get_action_url
from app.objects.constants import NoFileUploaded
from dataclasses import dataclass
from flask import request


class flaskInterface(abstractInterface):
    def __init__(self, action_name: str):
        self._action_name = action_name

    def log_error(self, error_message: str):
        flash_error(error_message)

    def log_message(self, log_message: str):
        flash_log(log_message)

    def get_persistent_value(self, key):
        return self.session_data.get_value(key)

    def set_persistent_value(self, key, value):
        self.session_data.set_value(key, value)


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

    @property
    def is_posted_form(self) -> bool:
        return is_website_post()

    def value_from_form(self, key: str):
        value = get_value_from_form(key)
        if "date" in key:
            value = html_as_date(value)

        return value

    def last_button_pressed(self) -> str:
        return get_last_button_pressed()

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

    @property
    def action_name(self) -> str:
        return self._action_name



def is_website_post() -> bool:
    return request.method == "POST"


def get_value_from_form(key: str):
    return request.form[key]

NO_BUTTON_PRESSED=""
def get_last_button_pressed() -> str:
    try:
        return request.form[HTML_BUTTON_NAME]
    except:
        return NO_BUTTON_PRESSED


def uploaded_file(input_name: str = "file"):
    print("inside uploaded file")
    print(request.files.keys())
    file = request.files.get(input_name, None)
    if file is None:
        print("no file")

        raise NoFileUploaded()
    return file
