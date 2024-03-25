from app.objects.abstract_objects.form_function_mapping import   DisplayAndPostFormFunctionMaps, NestedDictOfMappings
from app.logic.instructors.ENTRY_view_instructors_page import display_form_main_instructors_page, post_form_main_instructors_page


instructor_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(NestedDictOfMappings(
    {(display_form_main_instructors_page, post_form_main_instructors_page):0
     }))

