from app.logic.abstract_logic_api import AbstractLogicApi, INITIAL_STATE
from app.logic.forms_and_interfaces.abstract_form import Form

from app.logic.volunteers.view_volunteers import display_form_view_of_volunteers, post_form_view_of_volunteers
from app.logic.volunteers.constants import *
from app.logic.volunteers.add_volunteer import display_form_add_volunteer, post_form_add_volunteer
from app.logic.volunteers.view_individual_volunteer import display_form_view_individual_volunteer, post_form_view_individual_volunteer
from app.logic.volunteers.delete_volunteer import display_form_delete_individual_volunteer, post_form_delete_individual_volunteer
from app.logic.volunteers.edit_volunteer import display_form_edit_individual_volunteer, post_form_edit_individual_volunteer
from app.logic.volunteers.edit_cadet_connections import display_form_edit_cadet_volunteer_connections,post_form_edit_cadet_volunteer_connections

class VolunteerLogicApi(AbstractLogicApi):
    def get_displayed_form_given_form_name(self, form_name: str):
        if form_name == INITIAL_STATE:
            return display_form_view_of_volunteers(self.interface)
        elif form_name== ADD_VOLUNTEER_STAGE:
            return display_form_add_volunteer(self.interface)
        elif form_name==VIEW_INDIVIDUAL_VOLUNTEER_STAGE:
            return display_form_view_individual_volunteer(self.interface)
        elif form_name==DELETE_VOLUNTEER_STAGE:
            return display_form_delete_individual_volunteer(self.interface)
        elif form_name==EDIT_VOLUNTEER_STAGE:
            return display_form_edit_individual_volunteer(self.interface)
        elif form_name==EDIT_CADET_CONNECTIONS_BUTTON_LABEL:
            return display_form_edit_cadet_volunteer_connections(self.interface)
        else:
            raise Exception("Form name %s not recognised" % form_name)

    def get_posted_form_given_form_name_without_checking_for_redirection(
        self, form_name: str
    ) -> Form:
        if form_name == INITIAL_STATE:
            return post_form_view_of_volunteers(self.interface)
        elif form_name == ADD_VOLUNTEER_STAGE:
            return post_form_add_volunteer(self.interface)
        elif form_name == VIEW_INDIVIDUAL_VOLUNTEER_STAGE:
            return post_form_view_individual_volunteer(self.interface)
        elif form_name == DELETE_VOLUNTEER_STAGE:
            return post_form_delete_individual_volunteer(self.interface)
        elif form_name == EDIT_VOLUNTEER_STAGE:
            return post_form_edit_individual_volunteer(self.interface)
        elif form_name == EDIT_CADET_CONNECTIONS_BUTTON_LABEL:
            return post_form_edit_cadet_volunteer_connections(self.interface)
        else:
            raise Exception("Form name %s not recognised" % form_name)
