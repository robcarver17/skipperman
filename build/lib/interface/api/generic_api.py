from os.path import join, exists
from pathlib import Path
from objects.constants import arg_not_passed

import pandas as pd
import os

from data_access.configuration.configuration import REPORTING_SUBDIRECTORY


class GenericInterfaceApi(object):
    def __init__(self, starting_directory_for_up_download: str):
        self._starting_directory_for_up_download = starting_directory_for_up_download

    def select_file(self, message_to_display: str):
        raise NotImplemented

    def select_path(self, message_to_display: str):
        raise NotImplemented

    def message(self, message_to_display: str):
        raise NotImplemented

    def display_df(self, df: pd.DataFrame):
        raise NotImplemented

    def get_menu_item(self) -> str:
        raise NotImplemented

    def get_generic_input_from_user(self, prompt: str):
        raise NotImplemented

    def get_choice_from_adhoc_menu(self, list_of_options: list, prompt: str = ""):
        raise NotImplemented

    def put_items_in_order(self, items, prompt: str = ""):
        raise NotImplemented

    def create_nested_list_from_items(self, items, prompt: str = ""):
        raise NotImplemented

    def return_true_if_answer_is_yes(self, prompt: str) -> bool:
        raise NotImplemented

    def get_input_from_user_and_convert_to_type(
        self,
        prompt: str,
        type_expected=int,
        allow_default: bool = False,
        default_value=0,
        default_str: str = None,
        check_type: bool = True,
    ):
        raise NotImplemented

    def process_pdf_report(self, filename: str):
        raise NotImplemented

    ## Following boring methods to flag if user has chosen to leave
    def set_to_exit_state(self):
        self._exit_state = True

    def user_selected_exit_state(self):
        exit_state = getattr(self, "_exit_state", False)
        return exit_state

    @property
    def starting_directory_for_up_download(self) -> str:
        return self._starting_directory_for_up_download

    @property
    def starting_directory_for_reporting(self) -> str:
        path = join(self.starting_directory_for_up_download, REPORTING_SUBDIRECTORY)
        if not exists(path):
            path = Path(path)
            path.mkdir(parents=True)
        return path
