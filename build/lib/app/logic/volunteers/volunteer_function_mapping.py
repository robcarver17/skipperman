from app.logic.volunteers.ENTRY_view_volunteers import  post_form_view_of_volunteers, \
    display_form_view_of_volunteers
from app.logic.volunteers.add_volunteer import display_form_add_volunteer, post_form_add_volunteer
from app.logic.volunteers.view_individual_volunteer import display_form_view_individual_volunteer, post_form_view_individual_volunteer
from app.logic.volunteers.delete_volunteer import display_form_delete_individual_volunteer, post_form_delete_individual_volunteer
from app.logic.volunteers.edit_volunteer import display_form_edit_individual_volunteer, post_form_edit_individual_volunteer
from app.logic.volunteers.edit_cadet_connections import display_form_edit_cadet_volunteer_connections,post_form_edit_cadet_volunteer_connections
from app.objects.abstract_objects.form_function_mapping import FormNameFunctionNameMapping, \
    DisplayAndPostFormFunctionMaps, INITIAL_STATE

ADD_VOLUNTEER_STAGE = "add_volunteer_stage"
VIEW_INDIVIDUAL_VOLUNTEER_STAGE = "view_individual_volunteer_stage"
DELETE_VOLUNTEER_STAGE = "delete_volunteer_stage"
EDIT_VOLUNTEER_STAGE = "edit_volunteer_stage"
EDIT_CONNECTIONS_STAGE = "edit_cadet_volunteer_connections_stage"

volunteer_function_mapping = DisplayAndPostFormFunctionMaps(
    display_mappings=FormNameFunctionNameMapping(mapping_dict={
        INITIAL_STATE:
            display_form_view_of_volunteers,
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
        },
    parent_child_dict={
display_form_view_of_volunteers: (display_form_add_volunteer, display_form_view_individual_volunteer),
display_form_view_individual_volunteer: (display_form_edit_cadet_volunteer_connections, display_form_edit_individual_volunteer, display_form_delete_individual_volunteer)
    }),
    post_mappings=FormNameFunctionNameMapping({INITIAL_STATE:
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
            post_form_edit_cadet_volunteer_connections})
)
