from app.frontend.cadets.ENTRY_view_cadets import (
    display_form_view_of_cadets,
    post_form_view_of_cadets,
)
from app.frontend.cadets.add_cadet import display_form_add_cadet, post_form_add_cadets
from app.frontend.cadets.view_individual_cadets import (
    display_form_view_individual_cadet,
    post_form_view_individual_cadet,
)
from app.frontend.cadets.edit_cadet import (
    display_form_edit_individual_cadet,
    post_form_edit_individual_cadet,
)

from app.objects.abstract_objects.form_function_mapping import (
    DisplayAndPostFormFunctionMaps,
    NestedDictOfMappings,
)
from app.frontend.cadets.import_members import (
    display_form_import_members,
    post_form_import_members,
)
from app.frontend.cadets.iterate_over_import_cadets_in_uploaded_file import (
    display_verify_adding_cadet_from_list_form,
    post_verify_adding_cadet_from_list_form,
)
from app.frontend.cadets.cadet_committee import *

nested_dict = NestedDictOfMappings(
    {
        (display_form_view_of_cadets, post_form_view_of_cadets): {
            (display_form_import_members, post_form_import_members): 0,
            (
                display_verify_adding_cadet_from_list_form,
                post_verify_adding_cadet_from_list_form,
            ): 0,  ## returns to display cadets
            (display_form_cadet_committee, post_form_cadet_committee): 0,
            (display_form_add_cadet, post_form_add_cadets): "",
            (display_form_view_individual_cadet, post_form_view_individual_cadet): {
                (
                    display_form_edit_individual_cadet,
                    post_form_edit_individual_cadet,
                ): "",
            },
        }
    }
)


cadet_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
    nested_dict
)
