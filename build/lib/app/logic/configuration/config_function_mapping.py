from app.logic.configuration.view_main_config_page import display_form_main_config_page, post_form_main_config_page

from app.objects.abstract_objects.form_function_mapping import   DisplayAndPostFormFunctionMaps, NestedDictOfMappings



config_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(NestedDictOfMappings(
    {(display_form_main_config_page,post_form_main_config_page): ''
     }))