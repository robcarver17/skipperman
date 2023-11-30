from app.logic.abstract_logic_api import AbstractLogicApi, INITIAL_STATE
from app.logic.forms_and_interfaces.abstract_form import Form

from app.logic.cadets.view_cadets import display_form_view_of_cadets, post_form_view_of_cadets
from app.logic.cadets.add_cadet import display_form_add_cadet, post_form_add_cadets
from app.logic.cadets.view_individual_cadets import display_form_view_individual_cadet, post_form_view_individual_cadet
from app.logic.cadets.constants import VIEW_INDIVIDUAL_CADET_FORM, ADD_CADET_FORM


class CadetLogicApi(AbstractLogicApi):
    def get_displayed_form_given_form_name(self, form_name: str):
        if form_name==INITIAL_STATE:
            return display_form_view_of_cadets()
        elif form_name==VIEW_INDIVIDUAL_CADET_FORM:
            return display_form_view_individual_cadet(self.interface)
        elif form_name==ADD_CADET_FORM:
            return display_form_add_cadet(self.interface)
        else:
            raise Exception("Form name %s not recognised" % form_name)

    def get_posted_form_given_form_name_without_checking_for_redirection(self, form_name: str) -> Form:
        if form_name==INITIAL_STATE:
            return post_form_view_of_cadets(self.interface)
        elif form_name==ADD_CADET_FORM:
            return post_form_add_cadets(self.interface)
        elif form_name==VIEW_INDIVIDUAL_CADET_FORM:
            return post_form_view_individual_cadet(self.interface)
        else:
            raise Exception("Form name %s not recognised" % form_name)

