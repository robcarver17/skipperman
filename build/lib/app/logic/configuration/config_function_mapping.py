from app.objects.abstract_objects.form_function_mapping import (
    DisplayAndPostFormFunctionMaps,
    NestedDictOfMappings,
)

from app.frontend.configuration.ENTRY_view_main_config_page import (
    display_form_main_config_page,
    post_form_main_config_page,
)
from app.frontend.configuration.patrol_boats import (
    display_form_config_patrol_boats_page,
    post_form_config_patrol_boats_page,
)
from app.frontend.configuration.club_dinghies import (
    display_form_config_club_dinghies_page,
    post_form_config_club_dinghies_page,
)
from app.frontend.configuration.boat_classes import (
    display_form_config_boat_classes_page,
    post_form_config_dinghies_page,
)
from app.frontend.configuration.qualifications.qualifications import (
    display_form_config_qualifications_page,
    post_form_config_qualifications_page,
)
from app.frontend.configuration.qualifications.edit_qualifications_in_detail import (
    display_form_edit_qualification_details,
    post_form_edit_qualification_details,
)

config_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
    NestedDictOfMappings(
        {
            (display_form_main_config_page, post_form_main_config_page): {
                (
                    display_form_config_club_dinghies_page,
                    post_form_config_club_dinghies_page,
                ): 0,
                (
                    display_form_config_patrol_boats_page,
                    post_form_config_patrol_boats_page,
                ): 0,
                (
                    display_form_config_boat_classes_page,
                    post_form_config_dinghies_page,
                ): 0,
                (
                    display_form_config_qualifications_page,
                    post_form_config_qualifications_page,
                ): {
                    (
                        display_form_edit_qualification_details,
                        post_form_edit_qualification_details,
                    ): 0
                },
            }
        }
    )
)
