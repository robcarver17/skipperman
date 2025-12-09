from app.frontend.volunteers.volunteer_function_mapping import volunteer_function_raw_mapping_dict
from app.frontend.events.events_function_mapping import raw_dict_for_event_function_mapping
from app.objects.abstract_objects.form_function_mapping import DisplayAndPostFormFunctionMaps, NestedDictOfMappings

global_mapping_dict = {}
global_mapping_dict.update(raw_dict_for_event_function_mapping)
global_mapping_dict.update(volunteer_function_raw_mapping_dict)

global_function_mapping = (
    DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
        NestedDictOfMappings(
            global_mapping_dict, old_style_top_level_dict=False
        )
    )
)
