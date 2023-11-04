from app.interface.flask.session_data_for_action import (
    SessionDataForAction,
    clear_session_data_for_action,
    clear_session_data_for_all_actions,
)
from app.interface.html.forms import HTML_BUTTON_NAME
from app.interface.html.url import get_action_url
from app.objects.constants import NoFileUploaded
from dataclasses import dataclass
from flask import request


@dataclass
class StateDataForAction:
    action_name: str

    def get_value(self, key):
        return self.session_data.get_value(key)

    def set_value(self, key, value):
        self.session_data.set_value(key, value)

    @property
    def is_initial_stage(self) -> bool:
        return self.session_data.is_initial_stage

    def reset_to_initial_stage(self):
        self.session_data.reset_to_initial_stage()

    @property
    def stage(self) -> str:
        return self.session_data.stage

    @stage.setter
    def stage(self, new_stage):
        self.session_data.stage = new_stage

    def clear_session_data_for_all_actions(self):
        clear_session_data_for_all_actions()

    def clear_session_data_for_action_and_reset_stage(self):
        self.reset_to_initial_stage()  ## this should happen anyway, but belt and braces
        clear_session_data_for_action(self.action_name)

    @property
    def session_data(
        self,
    ) -> SessionDataForAction:  ## pipe through to current session object
        return SessionDataForAction(self.action_name)

    ## things unrelated to session data
    @property
    def is_post(self) -> bool:
        return is_website_post()

    def value_from_form(self, key: str):
        return get_value_from_form(key)

    def last_button_pressed(self) -> str:
        return get_last_button_pressed()

    @property
    def current_url(self) -> str:
        return get_action_url(self.action_name)

    def uploaded_file(self, input_name: str = "file"):
        print("inside state")
        return uploaded_file(input_name)


def get_state_data_for_action(action_name: str) -> StateDataForAction:
    return StateDataForAction(action_name=action_name)


def is_website_post() -> bool:
    return request.method == "POST"


def get_value_from_form(key: str):
    return request.form[key]


def get_last_button_pressed() -> str:
    return request.form[HTML_BUTTON_NAME]


def uploaded_file(input_name: str = "file"):
    print("inside uploaded file")
    print(request.files.keys())
    file = request.files.get(input_name, None)
    if file is None:
        print("no file")

        raise NoFileUploaded()
    return file
