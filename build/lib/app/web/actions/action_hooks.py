from app.frontend.cadets.cadet_function_mapping import cadet_function_mapping
from app.frontend.events.events_function_mapping import event_function_mapping
from app.frontend.reporting.reporting_function_mapping import reporting_function_mapping
from app.frontend.volunteers.volunteer_function_mapping import volunteer_function_mapping
from app.frontend.configuration.config_function_mapping import config_function_mapping
from app.frontend.instructors.instructor_function_mapping import (
    instructor_function_mapping,
)
from app.frontend.administration.admin_function_mapping import admin_function_mapping
from app.frontend.utilities.utilities_function_mapping import utilities_function_mapping

from app.web.flask.flask_interface import flaskInterface
from app.objects.abstract_objects.abstract_form import Form, form_with_message, File
from app.objects.abstract_objects.form_function_mapping import (
    DisplayAndPostFormFunctionMaps,
)
from app.frontend.form_handler import FormHandler
from app.data_access.data import data_api


class MissingMethod(Exception):
    pass


class SiteActions:
    def get_abstract_form_for_specific_action(self, action_name) -> [File, Form]:
        try:
            api = self.get_logic_api_for_specific_action_with_form_mapping(action_name)
        except MissingMethod:
            ## missing action
            return form_with_message(
                "Action %s not defined. Could be a bug or simply not written yet\n"
                % action_name
            )

        abstract_form_for_action = api.get_form()

        return abstract_form_for_action

    def get_logic_api_for_specific_action_with_form_mapping(
        self, action_name
    ) -> FormHandler:
        try:
            form_mapping = getattr(self, action_name)
        except AttributeError:
            raise MissingMethod

        interface = flaskInterface(
            action_name=action_name,
            display_and_post_form_function_maps=form_mapping,
            data=data_api,
        )
        interface._clear_data_store_cache()  ## avoid caching issues

        return FormHandler(interface)

    ## TO ADD NEW ACTIONS SUBMIT A NEW METHOD HERE
    ## These are values from the dict in menu_define
    ## ALL METHODS MUST TAKE web and only that as an argument

    @property
    def view_master_list_of_cadets(self) -> DisplayAndPostFormFunctionMaps:
        return cadet_function_mapping

    @property
    def view_list_of_events(self) -> DisplayAndPostFormFunctionMaps:
        return event_function_mapping

    @property
    def view_possible_reports(
        self,
    ) -> DisplayAndPostFormFunctionMaps:
        return reporting_function_mapping

    @property
    def view_list_of_volunteers(self) -> DisplayAndPostFormFunctionMaps:
        return volunteer_function_mapping

    @property
    def view_configuration(self) -> DisplayAndPostFormFunctionMaps:
        return config_function_mapping

    @property
    def view_for_instructors(self) -> DisplayAndPostFormFunctionMaps:
        return instructor_function_mapping

    @property
    def administration(self) -> DisplayAndPostFormFunctionMaps:
        return admin_function_mapping

    @property
    def view_utilities(self) -> DisplayAndPostFormFunctionMaps:
        return utilities_function_mapping
