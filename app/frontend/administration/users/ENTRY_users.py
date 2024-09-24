from typing import Union

from app.frontend.administration.users.parse_user_form import (
    delete_user_from_user_list,
    save_changes_in_security_form,
    generate_reset_message_for_user_name,
)
from app.frontend.administration.users.render_users_form import (
    display_form_edit_list_of_users,
    list_of_deletion_buttons_names,
    list_of_email_send_buttons_names,
)
from app.objects_OLD.abstract_objects.abstract_form import Form, NewForm
from app.objects_OLD.abstract_objects.abstract_buttons import CANCEL_BUTTON_LABEL
from app.objects_OLD.abstract_objects.abstract_interface import abstractInterface
from app.OLD_backend.data.security import load_all_users


def display_form_security(interface: abstractInterface) -> Union[Form, NewForm]:
    existing_list_of_users = load_all_users(interface)

    return display_form_edit_list_of_users(
        interface=interface, existing_list_of_users=existing_list_of_users
    )


def post_form_security(interface: abstractInterface) -> Union[Form, NewForm]:
    deleted_buttons = list_of_deletion_buttons_names(interface)
    email_buttons = list_of_email_send_buttons_names(interface)

    last_button = interface.last_button_pressed()

    if last_button == CANCEL_BUTTON_LABEL:
        return interface.get_new_display_form_for_parent_of_function(post_form_security)

    save_changes_in_security_form(interface)

    if last_button in deleted_buttons:
        delete_user_from_user_list(interface=interface, last_button=last_button)
    elif last_button in email_buttons:
        reset_link = generate_reset_message_for_user_name(
            last_button=last_button, interface=interface
        )
        interface.log_error(reset_link)

    interface.flush_cache_to_store()

    return display_form_security(interface)


# http://127.0.0.1:5000/link_login/?username=robc&password=w123
