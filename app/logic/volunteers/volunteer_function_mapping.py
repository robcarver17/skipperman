from app.logic.volunteers.ENTRY_view_volunteers import  post_form_view_of_volunteers, \
    display_form_view_of_volunteers
from app.logic.volunteers.add_volunteer import display_form_add_volunteer, post_form_add_volunteer
from app.logic.volunteers.view_individual_volunteer import display_form_view_individual_volunteer, post_form_view_individual_volunteer
from app.logic.volunteers.delete_volunteer import display_form_delete_individual_volunteer, post_form_delete_individual_volunteer
from app.logic.volunteers.edit_volunteer import display_form_edit_individual_volunteer, post_form_edit_individual_volunteer
from app.logic.volunteers.edit_cadet_connections import display_form_edit_cadet_volunteer_connections,post_form_edit_cadet_volunteer_connections
from app.objects.abstract_objects.form_function_mapping import   DisplayAndPostFormFunctionMaps, NestedDictOfMappings


volunteer_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
    NestedDictOfMappings(
        {
            (display_form_view_of_volunteers, post_form_view_of_volunteers):
                {
                (display_form_add_volunteer, post_form_add_volunteer): 0,
                (display_form_view_individual_volunteer, post_form_view_individual_volunteer):
                    {

                            (display_form_edit_cadet_volunteer_connections,post_form_edit_cadet_volunteer_connections):0,
                            (display_form_edit_individual_volunteer,post_form_edit_individual_volunteer):0,
                            (display_form_delete_individual_volunteer, post_form_delete_individual_volunteer):0
                    }
                }
        }
    )
)

