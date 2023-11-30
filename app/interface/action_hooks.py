from app.logic.cadets.cadets_logic_api import CadetLogicApi
from app.logic.events.events_logic_api import EventLogicApi
from app.logic.reporting.reporting_logic_api import ReportingLogicApi

from app.interface.flask.interface import flaskInterface
from app.logic.forms_and_interfaces.abstract_form import Form,  form_with_message, File
from app.logic.abstract_logic_api import AbstractLogicApi


class MissingMethod(Exception):
    pass

class SiteActions:


    def get_abstract_form_for_specific_action(self, action_name) -> [File, Form]:
        try:
            api = self.get_api_for_specific_action(action_name)
        except MissingMethod:
            ## missing action
            return form_with_message(
                "Action %s not defined. Could be a bug or simply not written yet\n"
                % action_name
            )

        abstract_form_for_action = api.get_form()

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

    def view_possible_reports(self, interface: flaskInterface) -> AbstractLogicApi:
        return ReportingLogicApi(interface)