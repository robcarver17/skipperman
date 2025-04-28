from app.web.flask.flash import get_html_of_flashed_messages
from app.web.flask.security import authenticated_user
from app.web.html.html_components import (
    Html,
    html_joined_list_as_lines,
    html_email,
)
from app.web.html.login_and_out import (
    get_login_link_html_code,
    get_read_write_logout_and_change_password_link_html_code,
    get_username_banner,
)
from app.data_access.configuration.configuration import SUPPORT_EMAIL
from app.web.html.url_define import HELP_PREFIX, MAIN_HELP_PAGE


def get_html_header(
    include_read_only_toggle: bool = False,
    include_title: str = "'SKIPPER-MAN'",
    include_user_options: bool = True,
    include_backup_option: bool = False,
    include_support_email_and_global_help: bool = False,
):
    if include_user_options:
        user_options_line = html_code_depending_on_whether_logged_in(
            include_read_only_toggle=include_read_only_toggle,
            include_backup_option=include_backup_option,
        )
        username_banner = get_username_banner()
    else:
        user_options_line = username_banner = ""

    if include_support_email_and_global_help:
        support_email = Html("For support email: %s" % (html_email(SUPPORT_EMAIL)))
        help_link = HELP_PREFIX+"/"+MAIN_HELP_PAGE
        print(help_link)
        global_help = Html('<a href="/%s" class="w3-bar-item w3-button w3-padding-16">Click here for general help</a>' % help_link)
        support_email_and_global_help = html_joined_list_as_lines([support_email, global_help])
    else:
        support_email_and_global_help = ""

    html_header = """
    <header class="w3-container w3-padding w3-orange" id="myHeader">
      <div class="w3-center">
      <h4>Blackwater Sailing Club - Cadet Skipper Management System</h4>
      <h1 class="w3-xxxlarge ">%s</h1>
      
      <h5>%s</h5>
        %s 
          %s
      </div>
    </header>""" % (
        include_title,
        username_banner,
        user_options_line,
        support_email_and_global_help,
    )

    return html_header


def html_code_depending_on_whether_logged_in(
    include_read_only_toggle: bool, include_backup_option: bool = False
) -> Html:
    if authenticated_user():
        return get_read_write_logout_and_change_password_link_html_code(
            include_read_only_toggle=include_read_only_toggle,
            include_backup_option=include_backup_option,
        )
    else:
        return get_login_link_html_code()


def get_flash_block():
    try:
        messages = get_html_of_flashed_messages()
    except:
        messages = []
    if len(messages) == 0:
        return ""

    messages = html_joined_list_as_lines(messages)

    return (
        """
    <div class="w3-padding w3-black w3-display-container">
      <span onclick="this.parentElement.style.display='none'" class="w3-button w3-display-topright"><i class="fa fa-remove"></i></span>
      <p>%s</p>
    </div>
    
    """
        % messages
    )
