from app.logic.configuration.view_main_config_page import display_form_main_config_page, post_form_main_config_page
from app.logic.configuration.constants import *
from app.objects.abstract_objects.form_function_mapping import FormNameFunctionNameMapping, \
    DisplayAndPostFormFunctionMaps, INITIAL_STATE

config_function_mapping = DisplayAndPostFormFunctionMaps(
    display_mappings=  FormNameFunctionNameMapping({
            INITIAL_STATE: display_form_main_config_page
        }),
    post_mappings= FormNameFunctionNameMapping({
            INITIAL_STATE: post_form_main_config_page
        }))