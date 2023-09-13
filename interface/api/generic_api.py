import pandas as pd


class GenericInterfaceApi(object):
    def message(self, message_to_display: str):
        raise NotImplemented

    def display_df(self, df: pd.DataFrame):
        raise NotImplemented

    def get_menu_item(self) -> str:
        raise NotImplemented

    def get_generic_input_from_user(self, prompt: str):
        raise NotImplemented

    def get_choice_from_adhoc_menu(self, list_of_options):
        raise NotImplemented

    def return_true_if_answer_is_yes(self, prompt: str) -> bool:
        raise NotImplemented

    def get_input_from_user_and_convert_to_type(
        self,
        prompt: str,
    ):
        raise NotImplemented

    ## Following boring methods to flag if user has chosen to leave
    def set_to_exit_state(self):
        self._exit_state = True

    def user_selected_exit_state(self):
        exit_state = getattr(self, "_exit_state", False)
        return exit_state
