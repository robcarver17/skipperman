from typing import List
import pandas as pd
from interface.api.generic_api import GenericInterfaceApi
from interface.cli.interactive_cli_menu import InteractiveCliMenu, EXIT, print_menu_and_get_desired_option
from interface.cli.input import get_input_from_user_and_convert_to_type, true_if_answer_is_yes
from interface.menus.menu_define import menu_definition


class CliInterfaceApi(GenericInterfaceApi):
    def __init__(self):
        self._main_menu = InteractiveCliMenu(menu_definition)

    def message(self, message_to_display: str):
        print("\n%s\n" % message_to_display)

    def display_df(self, df: pd.DataFrame):
        print("\n")
        print(df)
        print("\n")

    def get_menu_item(self) -> str:
        menu_item = self.main_menu.get_selected_menu_item_from_user()
        if menu_item is EXIT:
            self.set_to_exit_state()

        return menu_item

    def get_input_from_user_and_convert_to_type(
        self,
        prompt: str,
        type_expected=int,
        allow_default: bool = True,
        default_value=0,
        default_str: str = None,
        check_type: bool = True,
    ):

        input = get_input_from_user_and_convert_to_type(
            prompt=prompt,
            default_str=default_str,
            default_value=default_value,
            type_expected=type_expected,
            allow_default=allow_default,
            check_type=check_type,
        )

        return input

    def get_generic_input_from_user(self, prompt: str):
        print("\n")
        result = input(prompt+":")
        print("\n")

        return result

    def get_choice_from_adhoc_menu(self, list_of_options: List[str]) -> str:
        option = print_menu_and_get_desired_option(list_of_options)
        return option

    def return_true_if_answer_is_yes(self, prompt: str) -> bool:
        input = true_if_answer_is_yes(prompt)
        return input


    @property
    def main_menu(self) -> InteractiveCliMenu:
        return self._main_menu
