from app.logic.abstract_logic_api import LogicApi, INITIAL_STATE
from app.objects.abstract_objects.abstract_form import Form

from app.logic.volunteers.ENTRY_view_volunteers import get_form_view_of_volunteers, post_form_view_of_volunteers
from app.logic.volunteers.constants import *
from app.logic.volunteers.add_volunteer import display_form_add_volunteer, post_form_add_volunteer
from app.logic.volunteers.view_individual_volunteer import display_form_view_individual_volunteer, post_form_view_individual_volunteer
from app.logic.volunteers.delete_volunteer import display_form_delete_individual_volunteer, post_form_delete_individual_volunteer
from app.logic.volunteers.edit_volunteer import display_form_edit_individual_volunteer, post_form_edit_individual_volunteer
from app.logic.volunteers.edit_cadet_connections import display_form_edit_cadet_volunteer_connections,post_form_edit_cadet_volunteer_connections

class VolunteerLogicApi(LogicApi):
    @property
    def display_form_name_function_mapping(self) -> dict:
        return {
        INITIAL_STATE:
            get_form_view_of_volunteers,
        ADD_VOLUNTEER_STAGE:
            display_form_add_volunteer,
        VIEW_INDIVIDUAL_VOLUNTEER_STAGE:
           display_form_view_individual_volunteer,
        DELETE_VOLUNTEER_STAGE:
            display_form_delete_individual_volunteer,
        EDIT_VOLUNTEER_STAGE:
            display_form_edit_individual_volunteer,
        EDIT_CONNECTIONS_STAGE:
            display_form_edit_cadet_volunteer_connections,
        }

    @property
    def post_form_name_function_mapping(self) -> dict:
        return {INITIAL_STATE:
            post_form_view_of_volunteers,
        ADD_VOLUNTEER_STAGE:
            post_form_add_volunteer,
        VIEW_INDIVIDUAL_VOLUNTEER_STAGE:
             post_form_view_individual_volunteer,
        DELETE_VOLUNTEER_STAGE:
             post_form_delete_individual_volunteer,
        EDIT_VOLUNTEER_STAGE:
             post_form_edit_individual_volunteer,
        EDIT_CONNECTIONS_STAGE:
            post_form_edit_cadet_volunteer_connections}

