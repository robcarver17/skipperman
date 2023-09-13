from interface.api.generic_api import GenericInterfaceApi

## place holder for web api, assuming that is how we do GUI
class WebInterfaceApi(GenericInterfaceApi):
    def __init__(self):
        pass

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
