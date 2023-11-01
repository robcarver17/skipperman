from app.interface.cadets.generate_page import generate_cadet_pages
from app.interface.events.generate_page import generate_event_pages

from app.interface.flask.state_for_action import get_state_data_for_action, StateDataForAction
from app.interface.html.html import Html, html_error

DEBUG = True

class SiteActions():
    ## TO ADD NEW ACTIONS SUBMIT A NEW METHOD HERE
    ## These are values from the dict in menu_define
    ## ALL METHODS MUST TAKE state_data and only that as an argument
    def view_master_list_of_cadets(self, state_data: StateDataForAction) -> Html:
        return generate_cadet_pages(state_data)

    def view_list_of_events(self, state_data: StateDataForAction) -> Html:
        return generate_event_pages(state_data)

    def get_html_for_action(self, action_name: str) -> Html:
        try:
            method_to_get_html_code = getattr(self, action_name)
        except:
            ## missing action
            html_code_for_action = html_error(
                "Action %s not defined. Could be a bug or simply not written yet\n" % action_name)
        else:
            html_code_for_action = self._get_html_for_action_without_checking_for_method(
                action_name=action_name,
                method_to_get_html_code=method_to_get_html_code
            )

        return html_code_for_action

    def _get_html_for_action_without_checking_for_method(self, action_name: str, method_to_get_html_code) -> Html:
        if DEBUG:
            state_data = get_state_data_for_action(action_name=action_name)
            html_code_for_action = method_to_get_html_code(state_data=state_data)
        else:
            try:
                state_data = get_state_data_for_action(action_name=action_name)
                html_code_for_action = method_to_get_html_code(state_data=state_data)
            except Exception as e:
                ## broken action
                html_code_for_action = html_error(
                    "Action %s went wrong - exception code %s\n" % (action_name, str(e)))

        return html_code_for_action

