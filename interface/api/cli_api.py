from typing import List
import pandas as pd
from interface.api.generic_api import GenericInterfaceApi
from interface.cli.interactive_cli_menu import (
    InteractiveCliMenu,
    EXIT,
)
from interface.cli.input import (
    get_input_from_user_and_convert_to_type,
    true_if_answer_is_yes, print_menu_and_get_desired_option,
)
from interface.cli.file_selector import interactive_file_selector
from interface.menus.menu_define import menu_definition

main_menu = InteractiveCliMenu(menu_definition)

class CliInterfaceApi(GenericInterfaceApi):
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
        allow_default: bool = False,
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
        result = input(prompt + ":")
        print("\n")

        return result

    def get_choice_from_adhoc_menu(self, list_of_options: List[str]) -> str:
        option = print_menu_and_get_desired_option(list_of_options)
        return option

    def return_true_if_answer_is_yes(self, prompt: str) -> bool:
        ans = true_if_answer_is_yes(prompt)
        return ans

    def select_file(self, message_to_display: str):
        starting_directory_for_up_download = self.starting_directory_for_up_download
        filename = interactive_file_selector(message_to_display,
                                             starting_directory_for_up_download=starting_directory_for_up_download)

        return filename

    @property
    def main_menu(self) -> InteractiveCliMenu:
        return main_menu

