from typing import Union

from app.backend.security.list_of_users import get_list_of_users
from app.frontend.administration.users.parse_user_form import (
    delete_selected_user_from_user_list,
    generate_reset_message_for_user_name,
    save_changes_to_existing_users,
    add_new_user_if_present,
)
from app.frontend.administration.users.render_users_form import (
    display_form_edit_list_of_users,
    list_of_deletion_buttons_names,
    list_of_reset_buttons_names,
    add_entry_button,
    save_entry_button,
)
from app.frontend.form_handler import button_error_and_back_to_initial_state_form
from app.objects.abstract_objects.abstract_form import Form, NewForm
from app.objects.abstract_objects.abstract_buttons import cancel_menu_button
from app.objects.abstract_objects.abstract_interface import abstractInterface


def display_form_security(interface: abstractInterface) -> Union[Form, NewForm]:
    existing_list_of_users = get_list_of_users(interface.object_store)

    return display_form_edit_list_of_users(
        interface=interface, existing_list_of_users=existing_list_of_users
    )


def post_form_security(interface: abstractInterface) -> Union[Form, NewForm]:
    deleted_buttons = list_of_deletion_buttons_names(interface)
    reset_buttons = list_of_reset_buttons_names(interface)

    last_button = interface.last_button_pressed()

    if cancel_menu_button.pressed(last_button):
        interface.clear_cache()
        return interface.get_new_display_form_for_parent_of_function(post_form_security)
    elif save_entry_button.pressed(last_button):
        save_changes_to_existing_users(interface)
    elif add_entry_button.pressed(last_button):
        add_new_user_if_present(interface)
    elif last_button in deleted_buttons:
        delete_selected_user_from_user_list(
            interface=interface, last_button=last_button
        )
    elif last_button in reset_buttons:
        reset_link = generate_reset_message_for_user_name(
            last_button=last_button, interface=interface
        )
        interface.log_error(reset_link)
    else:
        return button_error_and_back_to_initial_state_form(interface)

    interface.flush_cache_to_store()

    return display_form_security(interface)
