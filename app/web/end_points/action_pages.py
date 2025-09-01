from typing import Union

from app.data_access.init_data import underling_data_api
from app.data_access.store.object_store import ObjectStore
from app.data_access.store.store import Store
from app.frontend.form_handler import FormHandler
from app.frontend.menu_define import get_functions_mapping_for_action_name
from app.objects.abstract_objects.abstract_form import File, Form, form_with_message, NewForm
from app.objects.utilities.exceptions import MissingMethod, UnexpectedNewForm
from app.web.flask.flask_interface import flaskInterface
from app.web.flask.security import get_access_group_for_current_user
from app.web.html.html_components import (
    Html,
)
from app.web.html.master_layout import get_master_layout
from app.web.html.process_abstract_form_to_html import (
    process_abstract_form_to_html,
)
from app.web.html.url_define import get_urls_of_interest
from flask import send_file, Response


### Returns HTML for an 'action', non menu page
def generate_action_page_html(action_name: str) -> Union[Html, Response]:
    print("getting html for %s" % action_name)

    abstract_form_for_action = get_abstract_form_for_specific_action(action_name=action_name)

    if type(abstract_form_for_action) is File:
        print("Generating file %s" % abstract_form_for_action.path_and_filename)
        return send_file(abstract_form_for_action.path_and_filename, as_attachment=True)

    html_code_for_action = from_abstract_to_laid_out_html(
        abstract_form_for_action=abstract_form_for_action, action_name=action_name
    )

    html_page_master_layout = get_master_layout(
        include_read_only_toggle=False,
        include_user_options=True,
        include_backup_option=False,
    )
    html_page_master_layout.body.append(html_code_for_action)

    return html_page_master_layout.as_html()


def from_abstract_to_laid_out_html(
    abstract_form_for_action: Form, action_name: str
) -> Html:
    urls_of_interest = get_urls_of_interest(action_name)
    html_code_for_action = process_abstract_form_to_html(
        abstract_form_for_action, urls_of_interest=urls_of_interest
    )

    return html_code_for_action


def get_abstract_form_for_specific_action(action_name: str) -> Union[File, Form]:
    try:
        form_handler = get_form_handler_for_specific_action(action_name=action_name)
    except MissingMethod:
        ## missing action
        return form_with_message(
            "Action %s not defined. Could be a bug or simply not written yet\n"
            % action_name
        )

    abstract_form_for_action = form_handler.get_form()

    if type(abstract_form_for_action) is NewForm:
        form_handler.interface.log_error("Not expecting 'NewForm: %s' here - you might have pressed buttons too quickly and confused me." % abstract_form_for_action.form_name)
        raise UnexpectedNewForm()

    return abstract_form_for_action


def get_form_handler_for_specific_action(action_name: str) -> FormHandler:
    form_mapping = get_functions_mapping_for_action_name(action_name)
    group = get_access_group_for_current_user()
    store = Store()
    object_store = ObjectStore(data_store=store, data_api=underling_data_api)
    interface = flaskInterface(
        action_name=action_name,
        user_group=group,
        display_and_post_form_function_maps=form_mapping,
        object_store=object_store,
    )

    return FormHandler(interface)


