from app.logic.abstract_logic_api import AbstractLogicApi, INITIAL_STATE

from app.logic.cadets.view_cadets import (
    display_form_view_of_cadets,
    post_form_view_of_cadets,
)
from app.logic.cadets.add_cadet import display_form_add_cadet, post_form_add_cadets
from app.logic.cadets.view_individual_cadets import (
    display_form_view_individual_cadet,
    post_form_view_individual_cadet,
)
from app.logic.cadets.edit_cadet import display_form_edit_individual_cadet, post_form_edit_individual_cadet
from app.logic.cadets.delete_cadet import display_form_delete_individual_cadet, post_form_delete_individual_cadet
from app.logic.cadets.constants import *


class CadetLogicApi(AbstractLogicApi):
    @property
    def dict_of_display_forms(self) -> dict:
        return {
        INITIAL_STATE: display_form_view_of_cadets,
        VIEW_INDIVIDUAL_CADET_STAGE: display_form_view_individual_cadet,
        ADD_CADET_STAGE:display_form_add_cadet,
        DELETE_INDIVIDUAL_CADET_STAGE:display_form_delete_individual_cadet,
        EDIT_INDIVIDUAL_CADET_STAGE: display_form_edit_individual_cadet
        }

    @property
    def dict_of_posted_forms(self) -> dict:
        return {INITIAL_STATE: post_form_view_of_cadets,
        ADD_CADET_STAGE: post_form_add_cadets,
        VIEW_INDIVIDUAL_CADET_STAGE: post_form_view_individual_cadet,
        DELETE_INDIVIDUAL_CADET_STAGE: post_form_delete_individual_cadet,
        EDIT_INDIVIDUAL_CADET_STAGE: post_form_edit_individual_cadet}