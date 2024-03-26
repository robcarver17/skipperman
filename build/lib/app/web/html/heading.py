from app.web.flask.security import authenticated_user
from app.web.html.components import Html
from app.web.html.login_and_out import get_login_link_html_code, get_logout_link_html_code

def get_html_header():
    login_or_out_code = login_or_out()
    html_header = """
    <header class="w3-container w3-theme w3-padding" id="myHeader">
      <div class="w3-center">
      <h4>Blackwater Sailing Club</h4>
      <h1 class="w3-xxxlarge w3-animate-bottom">SKIPPERMAN</h1>
        %s
      </div>
    </header>""" % login_or_out_code

    return html_header


def login_or_out() -> Html:

    if authenticated_user():
        return get_logout_link_html_code()
    else:
        return get_login_link_html_code()
