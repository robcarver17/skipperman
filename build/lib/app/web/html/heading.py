from app.web.flask.flash import get_html_of_flashed_messages
from app.web.flask.security import authenticated_user
from app.web.html.components import Html, html_joined_list_as_lines, horizontal_line
from app.web.html.login_and_out import get_login_link_html_code, get_logout_link_html_code, get_username_banner


def get_html_header():
    login_or_out_code = login_or_out()
    username = get_username_banner()
    html_header = """
    <header class="w3-container w3-padding w3-orange" id="myHeader">
      <div class="w3-center">
      <h4>Blackwater Sailing Club - Cadet Skipper Management System</h4>
      <h1 class="w3-xxxlarge ">'SKIPPER-MAN'</h1>
      <h5>%s</h5>
        %s
      </div>
    </header>""" % (username, login_or_out_code)

    return html_header


def login_or_out() -> Html:

    if authenticated_user():
        return get_logout_link_html_code()
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