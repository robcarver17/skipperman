from typing import Union

from app.frontend.cadets.cadet_function_mapping import cadet_function_mapping
from app.frontend.events.events_function_mapping import event_function_mapping
from app.frontend.reporting.reporting_function_mapping import reporting_function_mapping
from app.frontend.volunteers.volunteer_function_mapping import (
    volunteer_function_mapping,
)
from app.frontend.configuration.config_function_mapping import config_function_mapping
from app.frontend.instructors.instructor_function_mapping import (
    instructor_function_mapping,
)
from app.frontend.administration.admin_function_mapping import admin_function_mapping
from app.frontend.utilities.utilities_function_mapping import utilities_function_mapping
from app.objects.utilities.exceptions import MissingMethod, UnexpectedNewForm

from app.web.flask.flask_interface import flaskInterface
from app.objects.abstract_objects.abstract_form import Form, form_with_message, File, NewForm
from app.objects.abstract_objects.form_function_mapping import (
    DisplayAndPostFormFunctionMaps,
)
from app.frontend.form_handler import FormHandler
from app.data_access.init_data import object_store


def get_abstract_form_for_specific_action(action_name) -> Union[File, Form]:
    try:
        form_handler = get_form_handler_for_specific_action(action_name)
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


def get_form_handler_for_specific_action(action_name) -> FormHandler:
    form_mapping = get_functions_mapping_for_action_name(action_name)

    interface = flaskInterface(
        action_name=action_name,
        display_and_post_form_function_maps=form_mapping,
        object_store=object_store,
    )

    return FormHandler(interface)


def get_functions_mapping_for_action_name(
    action_name: str,
) -> DisplayAndPostFormFunctionMaps:
    ## TO ADD NEW ACTIONS (SUB WEB PAGES) SUBMIT A NEW METHOD HERE
    function_mapping_dict = dict(
        view_master_list_of_cadets=cadet_function_mapping,
        view_list_of_events=event_function_mapping,
        view_possible_reports=reporting_function_mapping,
        view_list_of_volunteers=volunteer_function_mapping,
        view_configuration=config_function_mapping,
        view_for_instructors=instructor_function_mapping,
        administration=admin_function_mapping,
        view_utilities=utilities_function_mapping,
    )

    try:
        return function_mapping_dict[action_name]
    except AttributeError:
        raise MissingMethod
