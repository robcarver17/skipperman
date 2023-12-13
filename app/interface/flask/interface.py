from app.logic.forms_and_interfaces.abstract_form import ListOfLines
from app.logic.forms_and_interfaces.abstract_interface import abstractInterface
from app.interface.flask.flash import flash_error

from app.interface.flask.session_data_for_action import (
    SessionDataForAction,
    clear_session_data_for_action,
)
from app.interface.html.forms import HTML_BUTTON_NAME, html_as_date
from app.interface.html.url import get_action_url
from app.objects.constants import (
    NoFileUploaded,
    missing_data,
    arg_not_passed,
    NoButtonPressed,
)
from flask import request


class flaskInterface(abstractInterface):
    def __init__(self, action_name: str):
        self._action_name = action_name

    def log_error(self, error_message: str):
        flash_error(error_message)

    def log_message(self, log_message: str):
        logs = self.logs
        logs.append(log_message)
        self.logs = logs

    def print_logs(self) -> ListOfLines:
        return ListOfLines(self.logs)

    @property
    def logs(self) -> list:
        logs = self.get_persistent_value("_logs")
        if logs is missing_data:
            return []
        return logs

    @logs.setter
    def logs(self, logs: list):
        self.set_persistent_value("_logs", logs)

    def get_persistent_value(self, key, default=missing_data):
        return self.session_data.get_value(key, default=missing_data)

    def set_persistent_value(self, key, value):
        self.session_data.set_value(key, value)

    def delete_persistent_value(self, key):
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
            self.delete_persistent_value(key)

    @property
    def is_posted_form(self) -> bool:
        return is_website_post()

    def value_from_form(self, key: str):
        print("Getting value %s" % key)
        try:
            value = get_value_from_form(key)
        except:
            raise Exception("Value %s not found in form" % key)
        if "date" in key:
            value = html_as_date(value)
        print("Value is %s" % str(value))

        return value

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

    @property
    def action_name(self) -> str:
        return self._action_name


def is_website_post() -> bool:
    return request.method == "POST"


def get_value_from_form(key: str):
    return request.form[key]


def get_last_button_pressed(button_name: str = arg_not_passed) -> str:
    if button_name == arg_not_passed:
        button_name = HTML_BUTTON_NAME
    print("Testing press of %s" % button_name)
    try:
        return request.form[button_name]
    except:
        raise NoButtonPressed


def uploaded_file(input_name: str = "file"):
    print("inside uploaded file")
    print(request.files.keys())
    file = request.files.get(input_name, None)
    if file is None:
        print("no file")

        raise NoFileUploaded()
    return file
