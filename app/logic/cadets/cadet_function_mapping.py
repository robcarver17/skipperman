

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

from app.objects.abstract_objects.form_function_mapping import   DisplayAndPostFormFunctionMaps, NestedDictOfMappings


nested_dict=NestedDictOfMappings(
    {(display_form_view_of_cadets, post_form_view_of_cadets): {
    (display_form_add_cadet, post_form_add_cadets): '',
    (display_form_view_individual_cadet, post_form_view_individual_cadet): {
            (display_form_delete_individual_cadet, post_form_delete_individual_cadet): '',
            (display_form_edit_individual_cadet, post_form_edit_individual_cadet): '',
        }

    }

})







cadet_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(nested_dict)