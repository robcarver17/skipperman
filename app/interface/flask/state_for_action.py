from app.objects.constants import missing_data
from app.interface.html.forms import HTML_BUTTON_NAME
from app.interface.html.url import get_action_url
from dataclasses import dataclass, field
from flask import session
from flask import request


ACTION_STATES_STORAGE = 'action_state'
INITIAL_STAGE = 'initial_stage'


class SessionDataForAction(object):
    def __init__(self, action_name: str):
        self._action_name = action_name

    @property
    def is_initial_stage(self) -> bool:
        return self.stage==INITIAL_STAGE

    def get_value(self, key):
        return self.other_data.get(key, missing_data)

    def set_value(self, key, value):
        other_data = self.other_data
        other_data[key] = value
        self.other_data = other_data

    @property
    def other_data(self)->dict:
        return self.state_data_as_dict_from_session.get('other_data', {})

    @other_data.setter
    def other_data(self, new_other_data):
        state_data_as_dict_from_session = self.state_data_as_dict_from_session
        state_data_as_dict_from_session['other_data'] = new_other_data
        self.update_session_dict_for_action(state_data_as_dict_from_session)

    @property
    def stage(self):
        return self.state_data_as_dict_from_session.get('stage', INITIAL_STAGE)

    @stage.setter
    def stage(self, new_stage:str):
        state_data_as_dict_from_session = self.state_data_as_dict_from_session
        state_data_as_dict_from_session['stage'] = new_stage
        self.update_session_dict_for_action(state_data_as_dict_from_session)

    def update_session_dict_for_action(self, new_dict: dict):
        _update_session_dict_for_action(action_name=self.action_name, new_dict=new_dict)

    @property
    def state_data_as_dict_from_session(self) ->dict:
        return _get_session_data_dict_for_action(action_name=self.action_name)

    @property
    def action_name(self)->str:
        return self._action_name

def _get_session_data_dict_for_action(action_name:str) -> dict:
    all_action_state_data = _get_all_action_state_data_from_session()
    if action_name not in all_action_state_data:
        all_action_state_data[action_name] = {}

    return all_action_state_data[action_name]

def _update_session_dict_for_action(action_name:str, new_dict: dict):
    all_action_state_data = _get_session_data_dict_for_action(action_name)
    all_action_state_data = new_dict
    session.modified = True

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
        self.session_data.stage=INITIAL_STAGE

    @property
    def stage(self) -> str:
        return self.session_data.stage

    @stage.setter
    def stage(self, new_stage):
        self.session_data.stage = new_stage

    @property
    def session_data(self) -> SessionDataForAction: ## pipe through to current session object
        return SessionDataForAction(self.action_name)

    ## things unrelated to session data
    @property
    def is_post(self) ->bool:
        return is_website_post()

    def value_from_form(self, key:str):
        return get_value_from_form(key)

    def last_button_pressed(self) -> str:
        return get_last_button_pressed()

    @property
    def current_url(self) ->str:
        return get_action_url(self.action_name)




def get_state_data_for_action(action_name: str) -> StateDataForAction:
    return StateDataForAction(action_name=action_name)

def clear_state_data_for_action(action_name: str):
    all_action_state_data = _get_all_action_state_data_from_session()
    try:
        del(all_action_state_data[action_name])
    except KeyError:
        pass


def clear_state_data_for_all_actions():
    try:
        del(session[ACTION_STATES_STORAGE])
    except KeyError:
        pass


def _get_all_action_state_data_from_session()-> dict:
    if ACTION_STATES_STORAGE not in session:
        session[ACTION_STATES_STORAGE] = {}

    return session[ACTION_STATES_STORAGE]

def is_website_post() ->bool:
    return request.method=="POST"

def get_value_from_form(key:str):
    return request.form[key]

def get_last_button_pressed()-> str:
    return request.form[HTML_BUTTON_NAME]