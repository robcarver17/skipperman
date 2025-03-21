from app.frontend.volunteers.ENTRY_view_volunteers import (
    post_form_view_of_volunteers,
    display_form_view_of_volunteers,
)
from app.frontend.volunteers.add_volunteer import (
    display_form_add_volunteer,
    post_form_add_volunteer,
)
from app.frontend.volunteers.iterate_over_imported_volunteer_skills import \
    display_volunteer_selection_in_skill_import_form, post_volunteer_selection_in_skill_import_form, \
    display_skills_editing_form_when_mismatch, post_skills_editing_form_when_mismatch
from app.frontend.volunteers.update_skills_from_csv import display_form_refresh_volunteer_skills, \
    post_form_refresh_volunteer_skills
from app.frontend.volunteers.view_individual_volunteer import (
    display_form_view_individual_volunteer,
    post_form_view_individual_volunteer,
)
from app.frontend.volunteers.edit_volunteer import (
    display_form_edit_individual_volunteer,
    post_form_edit_individual_volunteer,
)
from app.frontend.volunteers.edit_cadet_connections import (
    display_form_edit_cadet_volunteer_connections,
    post_form_edit_cadet_volunteer_connections,
)
from app.objects.abstract_objects.form_function_mapping import (
    DisplayAndPostFormFunctionMaps,
    NestedDictOfMappings,
)


volunteer_function_mapping = (
    DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
        NestedDictOfMappings(
            {
                (display_form_view_of_volunteers, post_form_view_of_volunteers): {
                    (display_form_add_volunteer, post_form_add_volunteer): 0,
                    (display_form_refresh_volunteer_skills, post_form_refresh_volunteer_skills):0,
                        (display_volunteer_selection_in_skill_import_form,
                         post_volunteer_selection_in_skill_import_form
                         ):0, ## RETURNS TO DISPLAY VOLUNTEERS
                    (display_skills_editing_form_when_mismatch,
                     post_skills_editing_form_when_mismatch):0,
                    (
                        display_form_view_individual_volunteer,
                        post_form_view_individual_volunteer,
                    ): {
                        (
                            display_form_edit_cadet_volunteer_connections,
                            post_form_edit_cadet_volunteer_connections,
                        ): 0,
                        (
                            display_form_edit_individual_volunteer,
                            post_form_edit_individual_volunteer,
                        ): 0,
                    },
                }
            }
        )
    )
)
