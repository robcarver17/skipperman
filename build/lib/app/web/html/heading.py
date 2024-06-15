from app.data_access.data import data_api

from app.web.flask.flask_interface import flaskInterface

from app.web.flask.flash import get_html_of_flashed_messages
from app.web.flask.security import authenticated_user
from app.web.html.components import Html, html_joined_list_as_lines, horizontal_line
from app.web.html.login_and_out import get_login_link_html_code, get_read_write_logout_and_chanage_password_link_html_code, get_username_banner


def get_html_header(include_read_only_toggle: bool = False, include_title: str = '', include_user_options: bool = True):
    if include_user_options:
        login_or_out_code = html_code_depending_on_whether_logged_in(include_read_only_toggle)
        username = get_username_banner()
    else:
        login_or_out_code = username = ''

    if len(include_title)==0:
        title_str = ''
    else:
        title_str = '<h3>%s</h3>' % include_title

    html_header = """
    <header class="w3-container w3-padding w3-orange" id="myHeader">
      <div class="w3-center">
      <h4>Blackwater Sailing Club - Cadet Skipper Management System</h4>
      <h1 class="w3-xxxlarge ">'SKIPPER-MAN'</h1>
      %s
      <h5>%s</h5>
        %s
      </div>
    </header>""" % (title_str, username, login_or_out_code)

    return html_header


def html_code_depending_on_whether_logged_in(include_read_only_toggle: bool) -> Html:

    if authenticated_user():
        return get_read_write_logout_and_chanage_password_link_html_code(include_read_only_toggle)
    else:
        return get_login_link_html_code()


def get_flash_block():
    try:
        messages = get_html_of_flashed_messages()
    except:
        messages=[]
    if len(messages)==0:
        return ""
    print(messages)
    messages = html_joined_list_as_lines(messages)

    return """
    <div class="w3-padding w3-black w3-display-container">
      <span onclick="this.parentElement.style.display='none'" class="w3-button w3-display-topright"><i class="fa fa-remove"></i></span>
      <p>%s</p>
    </div>
    
    """ % messages