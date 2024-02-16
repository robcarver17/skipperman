from app.logic.abstract_logic_api import LogicApi, INITIAL_STATE

from app.logic.configuration.view_main_config_page import display_form_main_config_page, post_form_main_config_page
from app.logic.configuration.constants import *

class ConfigLogicApi(LogicApi):
    @property
    def display_form_name_function_mapping(self) -> dict:
        return {
            INITIAL_STATE: display_form_main_config_page
        }

    @property
    def post_form_name_function_mapping(self) -> dict:
        return {
            INITIAL_STATE: post_form_main_config_page
        }