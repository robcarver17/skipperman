from app.data_access.data_access import data

from app.logic.cadets.view_cadets import get_list_of_cadets_as_str
from app.logic.events.view_events import get_list_of_events_as_str
from app.interface.html.layout import layout_html, go_home_html
from app.interface.html.view_pd import view_df_as_html


### Returns HTML for an 'action', non menu page
def action_html(action_option: str) -> str:
    html_actions = HtmlActions(data)
    try:
        html_code_for_action_method = getattr(html_actions, action_option)
    except:
        return "Action %s not defined. Could be a bug or simply not written yet\n"+go_home_html % action_option

    html_code_for_action= html_code_for_action_method()

    return layout_html(go_home_html +html_code_for_action + go_home_html)


class HtmlActions():
    def __init__(self, data):
        self.data = data

    def view_master_list_of_cadets(self) -> str:
        df_of_cadets = get_list_of_cadets_as_str(self.data)
        return view_df_as_html(df_of_cadets)

    def view_list_of_events(self) -> str:
        df_of_events = get_list_of_events_as_str(self.data)
        return view_df_as_html(df_of_events)