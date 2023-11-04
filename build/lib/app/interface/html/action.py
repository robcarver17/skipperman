from app.data_access.data import data

from app.logic.cadets.view_cadets import get_list_of_cadets_as_str
from app.logic.events.view_events import get_list_of_events_as_str

from app.interface.html.html import Html
from app.interface.html.master_layout import master_layout_html
from app.interface.html.components import go_home_html
from app.interface.cadets.generate_page import generate_cadet_pages


### Returns HTML for an 'action', non menu page
def action_html(action_option: str) -> Html:
    html_code_for_action = action_html_inner_code(action_option)
    html_code_for_action_in_layout = add_standard_layout_and_buttons_to_action_code(
        html_code_for_action
    )

    return html_code_for_action_in_layout

def action_html_inner_code(action_option: str) -> Html:
    html_actions = HtmlActions(data)
    try:
        html_code_for_action_method = getattr(html_actions, action_option)
    except:
        ## missing action
        html_code_for_action = Html("Action %s not defined. Could be a bug or simply not written yet\n" % action_option)
    else:
        try:
            html_code_for_action = html_code_for_action_method()
        except Exception as e:
            ## broken action
            html_code_for_action = Html(
                "Action %s went wrong - exception code %s\n" % (action_option, str(e)))

    return html_code_for_action


def add_standard_layout_and_buttons_to_action_code(html_code_for_action: Html) -> Html:
    html_code_for_action_with_go_home = html_code_for_action.prefix_with(go_home_html)
    html_code_for_action_in_layout = html_code_for_action_with_go_home.wrap_with(master_layout_html)

    return html_code_for_action_in_layout

class HtmlActions():
    def __init__(self, data):
        self.data = data

    def view_master_list_of_cadets(self) -> str:
        df_of_cadets = get_list_of_cadets_as_str(self.data)
        return generate_cadet_pages(df_of_cadets)

