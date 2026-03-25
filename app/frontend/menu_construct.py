from app.frontend.administration.admin_function_mapping import admin_function_mapping
from app.frontend.cadets.cadet_function_mapping import cadet_function_mapping
from app.frontend.configuration.config_function_mapping import config_function_mapping
from app.frontend.events.events_function_mapping import event_function_mapping
from app.frontend.instructors.instructor_function_mapping import (
    instructor_function_mapping,
)
from app.frontend.reporting.reporting_function_mapping import reporting_function_mapping
from app.frontend.utilities.utilities_function_mapping import utilities_function_mapping
from app.frontend.volunteers.volunteer_function_mapping import (
    volunteer_function_mapping,
)
from app.objects.abstract_objects.form_function_mapping import (
    DisplayAndPostFormFunctionMaps,
)
from app.objects.utilities.exceptions import MissingMethod


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
