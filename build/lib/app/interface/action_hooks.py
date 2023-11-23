from typing import Callable
from app.interface.html.html import Html
from app.interface.flask.flash import html_error ### seems a weird place to put it

from app.interface.html.process_abstract_form_to_html import process_abstract_form_to_html
from app.logic.cadets.cadets_logic_api import CadetLogicApi
from app.logic.events.events_logic_api import EventLogicApi

from app.interface.flask.interface import flaskInterface
from app.logic.abstract_form import Form, Line, form_with_message
from app.logic.abstract_logic_api import AbstractLogicApi

DEBUG = True

class MissingMethod(Exception):
    pass

class SiteActions:

    def get_html_for_action(self, action_name: str) -> Html:
        interface = flaskInterface(action_name)
        abstract_form_for_action = self.get_abstract_form_for_specific_action(action_name)
        html_code_for_action = process_abstract_form_to_html(abstract_form_for_action, interface=interface)

        return html_code_for_action

    def get_abstract_form_for_specific_action(self, action_name) -> Form:
        try:
            api = self.get_api_for_specific_action(action_name)
        except MissingMethod:
            ## missing action
            return form_with_message(
                "Action %s not defined. Could be a bug or simply not written yet\n"
                % action_name
            )

        if DEBUG:
            abstract_form_for_action = api.get_form()
        else:
            try:
                abstract_form_for_action = api.get_form()

            except Exception as e:
                ## broken action
                return form_with_message(
                    "Action %s went wrong - exception code %s\n" % (action_name, str(e))
                )

        return abstract_form_for_action

    def get_api_for_specific_action(self, action_name)-> AbstractLogicApi:
        interface = flaskInterface(action_name)
        try:
            method_to_get_api = getattr(self, action_name)
        except AttributeError:
            raise MissingMethod

        return method_to_get_api(interface)

    ## TO ADD NEW ACTIONS SUBMIT A NEW METHOD HERE
    ## These are values from the dict in menu_define
    ## ALL METHODS MUST TAKE interface and only that as an argument


    def view_master_list_of_cadets(self, interface: flaskInterface) -> AbstractLogicApi:
        return CadetLogicApi(interface)

    def view_list_of_events(self, interface: flaskInterface) -> AbstractLogicApi:
        return EventLogicApi(interface)
