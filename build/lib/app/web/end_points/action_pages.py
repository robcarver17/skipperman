from typing import Union

from werkzeug.datastructures import MultiDict

from app.data_access.init_data import  object_store
from app.frontend.form_handler import FormHandler
from app.frontend.menu_define import get_functions_mapping_for_action_name
from app.objects.abstract_objects.abstract_form import File, Form, form_with_message, NewForm, NewFormWithRedirectInfo
from app.objects.utilities.exceptions import MissingMethod
from app.web.flask.flask_interface import flaskInterface
from app.web.flask.security import get_access_group_for_current_user
from app.web.html.html_components import (
    Html,
)
from app.web.html.master_layout import get_master_layout
from app.web.html.process_abstract_form_to_html import (
    process_abstract_form_to_html,
)
from app.web.html.url_define import get_urls_of_interest, ACTION_PREFIX
from flask import send_file, Response, redirect, url_for


def generate_action_page_html(action_name: str,
                              form_name: str,
                              args_passed:MultiDict) -> Union[Html, Response]:

    print("getting html for %s %s %s" % (action_name, form_name, str(args_passed)))

    args_passed=from_multidict_to_dict(args_passed)

    abstract_form_for_action = get_abstract_form_for_specific_action(action_name=action_name,
                                                                     form_name=form_name,
                                                                     args_passed=args_passed)

    if type(abstract_form_for_action) is File:
        print("Generating file %s" % abstract_form_for_action.path_and_filename)
        return send_file(abstract_form_for_action.path_and_filename, as_attachment=True)
    elif type(abstract_form_for_action) is NewFormWithRedirectInfo:
        print("Redirect %s" % str(abstract_form_for_action))
        return redirect_from_info(abstract_form_for_action)
    elif type(abstract_form_for_action) is Form:
        print("Form")
        return generate_action_page_html_from_abstract_form(abstract_form_for_action, action_name=action_name)
    else:
        raise Exception("type %s not recognised" % type(abstract_form_for_action))


# return

def from_multidict_to_dict(some_multi_dict: MultiDict):
    new_dict = dict(
        [
            (key, some_multi_dict.get(key)) for key in some_multi_dict.keys()
        ]
    )

    return new_dict

def from_abstract_to_laid_out_html(
    abstract_form_for_action: Form, action_name: str
) -> Html:
    urls_of_interest = get_urls_of_interest(action_name)
    html_code_for_action = process_abstract_form_to_html(
        abstract_form_for_action, urls_of_interest=urls_of_interest
    )

    return html_code_for_action


def get_abstract_form_for_specific_action(action_name: str,
                                          form_name: str,
                              args_passed:dict
                                          ) -> Union[File, Form, NewFormWithRedirectInfo]:

    try:
        form_handler = get_form_handler_for_specific_action(action_name=action_name,
                                                            form_name=form_name,
                                                            args_passed=args_passed)
    except MissingMethod:
        ## missing action
        return form_with_message(
            "Action %s not defined. Could be a bug or simply not written yet\n"
            % action_name
        )

    abstract_form_for_action = form_handler.get_form()

    return abstract_form_for_action



def get_form_handler_for_specific_action(action_name: str, form_name: str,
                              args_passed:dict) -> FormHandler:
    form_mapping = get_functions_mapping_for_action_name(action_name)
    group = get_access_group_for_current_user()
    interface = flaskInterface(
        action_name=action_name,
        form_name=form_name,
        args_passed=args_passed,
        user_group=group,
        display_and_post_form_function_maps=form_mapping,
        object_store=object_store,
    )

    return FormHandler(interface)

def redirect_from_info(redirect_info: NewFormWithRedirectInfo) -> Response:
    return redirect(url_for(ACTION_PREFIX,action_option=redirect_info.action_name,
                                                    form_name=redirect_info.new_form_name,
                            **redirect_info.args_passed))

def generate_action_page_html_from_abstract_form(abstract_form_for_action: Form, action_name:str) -> Html:
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
