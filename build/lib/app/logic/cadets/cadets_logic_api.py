from app.logic.abstract_logic_api import LogicApi
from app.objects.abstract_objects.form_function_mapping import INITIAL_STATE

from app.logic.cadets.ENTRY_view_cadets import (
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


class CadetLogicApi(LogicApi):
    @property
    def display_form_name_function_mapping(self) -> dict:
        return {
        INITIAL_STATE: display_form_view_of_cadets,
        VIEW_INDIVIDUAL_CADET_STAGE: display_form_view_individual_cadet,
        ADD_CADET_STAGE:display_form_add_cadet,
        DELETE_INDIVIDUAL_CADET_STAGE:display_form_delete_individual_cadet,
        EDIT_INDIVIDUAL_CADET_STAGE: display_form_edit_individual_cadet
        }

    @property
    def post_form_name_function_mapping(self) -> dict:
        return {INITIAL_STATE: post_form_view_of_cadets,
        ADD_CADET_STAGE: post_form_add_cadets,
        VIEW_INDIVIDUAL_CADET_STAGE: post_form_view_individual_cadet,
        DELETE_INDIVIDUAL_CADET_STAGE: post_form_delete_individual_cadet,
        EDIT_INDIVIDUAL_CADET_STAGE: post_form_edit_individual_cadet}