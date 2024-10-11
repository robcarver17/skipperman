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

from app.frontend.configuration.sailing_groups import display_form_config_sailing_groups, post_form_config_sailing_groups
from app.frontend.configuration.teams_and_roles.volunteer_roles import display_form_config_volunteer_roles, post_form_config_volunteer_roles
from app.frontend.configuration.teams_and_roles.volunteer_teams import display_form_config_teams_page, post_form_config_teams_page
from app.frontend.configuration.volunteer_skills import display_form_config_volunteer_skills, post_form_config_volunteer_skills
from app.frontend.configuration.teams_and_roles.edit_individual_team import display_form_edit_individual_team_page, post_form_edit_individual_team_page

config_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
    NestedDictOfMappings(
        {
            (display_form_main_config_page, post_form_main_config_page): {
                (display_form_config_sailing_groups, post_form_config_sailing_groups):0,
                (display_form_config_volunteer_skills, post_form_config_volunteer_skills):0,
                (display_form_config_volunteer_roles, post_form_config_volunteer_roles):0,
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
                (display_form_config_teams_page,                 post_form_config_teams_page): {
                    (display_form_edit_individual_team_page, post_form_edit_individual_team_page):0
                }
                ,


            (
                    display_form_config_qualifications_page,
                    post_form_config_qualifications_page,
                ): {
                    (
                        display_form_edit_qualification_details,
                        post_form_edit_qualification_details,
                    ): 0,
                }
            }
        }
    )
)
