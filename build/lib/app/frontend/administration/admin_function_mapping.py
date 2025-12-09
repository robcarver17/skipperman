from app.objects.abstract_objects.form_function_mapping import (
    DisplayAndPostFormFunctionMaps,
    NestedDictOfMappings,
)
from app.frontend.administration.ENTRY_view_admin_page import (
    display_form_main_admin_page,
    post_form_main_admin_page,
)
from app.frontend.administration.users.ENTRY_users import (
    display_form_security,
    post_form_security,
)
from app.frontend.administration.data.data import display_form_data, post_form_data
from app.frontend.administration.data.edit_delete_events import (
    display_form_edit_delete_events,
    post_form_edit_delete_events,
)
from app.frontend.administration.data.merge_delete_cadets import (
    display_form_merge_delete_cadets,
    post_form_merge_delete_cadets,
    display_form_merge_delete_individual_cadet,
    post_form_merge_delete_individual_cadet,
)
from app.frontend.administration.data.merge_delete_volunteers import (
    display_form_merge_delete_volunteers,
    post_form_merge_delete_volunteers,
    display_form_merge_delete_individual_volunteer,
    post_form_merge_delete_individual_volunteer,
)
from app.frontend.administration.data.deleting_cadets_process import (
    display_deleting_cadet_process,
    post_deleting_cadets_process,
)
from app.frontend.administration.data.deleting_volunteers_process import (
    display_deleting_volunteer_process,
    post_deleting_volunteers_process,
)

admin_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
    NestedDictOfMappings(
        {
            (display_form_main_admin_page, post_form_main_admin_page): {
                (display_form_security, post_form_security): 0,
                (display_form_data, post_form_data): {
                    (display_form_merge_delete_cadets, post_form_merge_delete_cadets): {
                        (
                            display_form_merge_delete_individual_cadet,
                            post_form_merge_delete_individual_cadet,
                        ): {
                            (
                                display_deleting_cadet_process,
                                post_deleting_cadets_process,
                            ): 0
                        }
                    },
                    (
                        display_form_merge_delete_volunteers,
                        post_form_merge_delete_volunteers,
                    ): {
                        (
                            display_form_merge_delete_individual_volunteer,
                            post_form_merge_delete_individual_volunteer,
                        ): {
                            (
                                display_deleting_volunteer_process,
                                post_deleting_volunteers_process,
                            ): 0
                        }
                    },
                    (display_form_edit_delete_events, post_form_edit_delete_events): 0,
                },
            }
        }
    )
)
