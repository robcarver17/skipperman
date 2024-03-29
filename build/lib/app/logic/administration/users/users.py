from typing import Union

from app.logic.administration.users.parse_user_form import delete_user_from_user_list, save_changes_in_security_form, \
    generate_reset_link_for_user_name
from app.logic.administration.users.render_users_form import display_form_edit_list_of_users, list_of_deletion_buttons_names, BACK_BUTTON_LABEL, list_of_email_send_buttons_names
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.backend.data.security import load_all_users



def display_form_security(interface: abstractInterface) -> Union[Form, NewForm]:
    existing_list_of_users = load_all_users()

    return display_form_edit_list_of_users(existing_list_of_users)


def post_form_security(interface: abstractInterface) -> Union[Form, NewForm]:
    last_button = interface.last_button_pressed()
    if last_button==BACK_BUTTON_LABEL:
        return interface.get_new_display_form_for_parent_of_function(post_form_security)

    if last_button in deleted_buttons:
        delete_user_from_user_list(last_button)
    if last_button in email_buttons:
        print("Email button pressed %s" % last_button)
        reset_link = generate_reset_link_for_user_name(last_button=last_button, interface=interface)
        interface.log_error("Reset link for user is %s" % reset_link)

    ## need to be careful here not to try updating deleted user
    save_changes_in_security_form(interface)

    return display_form_security(interface)

deleted_buttons =list_of_deletion_buttons_names()
email_buttons = list_of_email_send_buttons_names()

#http://127.0.0.1:5000/link_login/?username=robc&password=w123