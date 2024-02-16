
from app.logic.abstract_logic_api import LogicApi, INITIAL_STATE

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

from app.objects.abstract_objects.form_function_mapping import FormNameFunctionNameMapping, DisplayAndPostFormFunctionMaps

## stage names
ADD_CADET_STAGE = "add_cadet_stage"
VIEW_INDIVIDUAL_CADET_STAGE = "view_individual_cadet_stage"
EDIT_INDIVIDUAL_CADET_STAGE = "edit_individual_cadet_stage"
DELETE_INDIVIDUAL_CADET_STAGE = "delete_individual_cadet_stage"

cadet_function_mapping = DisplayAndPostFormFunctionMaps(
    display_mappings= FormNameFunctionNameMapping(mapping_dict={

        INITIAL_STATE: display_form_view_of_cadets,
        VIEW_INDIVIDUAL_CADET_STAGE: display_form_view_individual_cadet,
        ADD_CADET_STAGE:display_form_add_cadet,
        DELETE_INDIVIDUAL_CADET_STAGE:display_form_delete_individual_cadet,
        EDIT_INDIVIDUAL_CADET_STAGE: display_form_edit_individual_cadet
        },
    parent_child_dict={
    display_form_view_of_cadets: (display_form_view_individual_cadet, display_form_add_cadet),
    display_form_view_individual_cadet: (display_form_edit_individual_cadet, display_form_delete_individual_cadet)

    }),

    post_mappings= FormNameFunctionNameMapping({INITIAL_STATE: post_form_view_of_cadets,
        ADD_CADET_STAGE: post_form_add_cadets,
        VIEW_INDIVIDUAL_CADET_STAGE: post_form_view_individual_cadet,
        DELETE_INDIVIDUAL_CADET_STAGE: post_form_delete_individual_cadet,
        EDIT_INDIVIDUAL_CADET_STAGE: post_form_edit_individual_cadet}))


