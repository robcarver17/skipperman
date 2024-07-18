from flask import session

from app.objects.exceptions import missing_data

ACTION_STATES_STORAGE = "action_state"
INITIAL_STAGE = "initial_stage"


class SessionDataForAction(object):
    def __init__(self, action_name: str):
        self._action_name = action_name

    def reset_to_initial_stage(self):
        self.stage = INITIAL_STAGE
        print("stage now %s" % INITIAL_STAGE)

    @property
    def is_initial_stage(self) -> bool:
        return self.stage == INITIAL_STAGE

    def get_value(self, key, default=missing_data):
        result = self.other_data.get(key, default)

        return result

    def set_value(self, key, value):
        other_data = self.other_data
        other_data[key] = value
        self.other_data = other_data

    def delete_persistent_value(self, key):
        other_data = self.other_data
        try:
            other_data.pop(key)
        except:
            print("%s not in persistent storage" % key)

    def list_of_keys_with_persistent_values(self) -> list:
        other_data = self.other_data
        return list(other_data.keys())

    @property
    def other_data(self) -> dict:
        return self.state_data_as_dict_from_session.get("other_data", {})

    @other_data.setter
    def other_data(self, new_other_data):
        state_data_as_dict_from_session = self.state_data_as_dict_from_session
        state_data_as_dict_from_session["other_data"] = new_other_data
        self.update_session_dict_for_action(state_data_as_dict_from_session)

    @property
    def stage(self):
        stage = self.state_data_as_dict_from_session.get("stage", INITIAL_STAGE)
        return stage

    @stage.setter
    def stage(self, new_stage: str):
        state_data_as_dict_from_session = self.state_data_as_dict_from_session

        state_data_as_dict_from_session["stage"] = new_stage
        self.update_session_dict_for_action(state_data_as_dict_from_session)

    def update_session_dict_for_action(self, new_dict: dict):
        _update_session_dict_for_action(action_name=self.action_name, new_dict=new_dict)

    @property
    def state_data_as_dict_from_session(self) -> dict:
        return _get_session_data_dict_for_action(action_name=self.action_name)

    @property
    def action_name(self) -> str:
        return self._action_name


def _update_session_dict_for_action(action_name: str, new_dict: dict):
    ## ignore IDE warning that code doesn't appear to do anything, it does
    all_action_state_data = _get_session_data_dict_for_action(action_name)
    all_action_state_data = new_dict
    session.modified = True


def _get_session_data_dict_for_action(action_name: str) -> dict:
    all_action_state_data = _get_all_action_state_data_from_session()
    if action_name not in all_action_state_data:
        all_action_state_data[action_name] = {}
    return all_action_state_data[action_name]


def _get_all_action_state_data_from_session() -> dict:
    if ACTION_STATES_STORAGE not in session:
        session[ACTION_STATES_STORAGE] = {}

    return session[ACTION_STATES_STORAGE]


def clear_session_data_for_action(action_name: str):
    all_action_state_data = _get_all_action_state_data_from_session()
    try:
        del all_action_state_data[action_name]
    except KeyError:
        pass


def clear_session_data_for_all_actions():
    try:
        del session[ACTION_STATES_STORAGE]
    except KeyError:
        pass
