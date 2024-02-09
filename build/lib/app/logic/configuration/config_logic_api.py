from app.logic.abstract_logic_api import AbstractLogicApi, INITIAL_STATE

from app.logic.configuration.view_main_config_page import display_form_main_config_page, post_form_main_config_page

class ConfigLogicApi(AbstractLogicApi):
    @property
    def dict_of_display_forms(self) -> dict:
        return {
            INITIAL_STATE: display_form_main_config_page
        }

    @property
    def dict_of_posted_forms(self) -> dict:
        return {
            INITIAL_STATE: post_form_main_config_page
        }