from app.objects.abstract_objects.form_function_mapping import   DisplayAndPostFormFunctionMaps, NestedDictOfMappings

from app.logic.configuration.ENTRY_view_main_config_page import display_form_main_config_page, post_form_main_config_page
from app.logic.configuration.patrol_boats import display_form_config_patrol_boats_page, post_form_config_patrol_boats_page
from app.logic.configuration.club_dinghies import display_form_config_club_dinghies_page, post_form_config_club_dinghies_page
from app.logic.configuration.boat_classes import display_form_config_boat_classes_page, post_form_config_dinghies_page
from app.logic.configuration.qualifications import display_form_config_qualifications_page, post_form_config_qualifications_page


config_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(NestedDictOfMappings(
    {(display_form_main_config_page,post_form_main_config_page):
         {
             (display_form_config_club_dinghies_page, post_form_config_club_dinghies_page):0,
             (display_form_config_patrol_boats_page, post_form_config_patrol_boats_page):0,
            (display_form_config_boat_classes_page, post_form_config_dinghies_page):0,
             (display_form_config_qualifications_page, post_form_config_qualifications_page):0
         }
     }))