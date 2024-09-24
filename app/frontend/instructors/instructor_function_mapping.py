from app.objects_OLD.abstract_objects.form_function_mapping import (
    DisplayAndPostFormFunctionMaps,
    NestedDictOfMappings,
)
from app.frontend.instructors.ENTRY1_choose_event import (
    display_form_main_instructors_page,
    post_form_main_instructors_page,
)
from app.frontend.instructors.ENTRY2_choose_group import (
    display_form_choose_group_for_event,
    post_form_choose_group_for_event,
)
from app.frontend.instructors.ENTRY3_choose_level import (
    display_form_choose_level_for_group_at_event,
    post_form_choose_level_for_group_at_event,
)
from app.frontend.instructors.ENTRY_FINAL_view_ticksheets import (
    display_form_view_ticksheets_for_event_and_group,
    post_form_view_ticksheets_for_event_and_group,
)

instructor_function_mapping = (
    DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
        NestedDictOfMappings(
            {
                (display_form_main_instructors_page, post_form_main_instructors_page): {
                    (
                        display_form_choose_group_for_event,
                        post_form_choose_group_for_event,
                    ): {
                        (
                            display_form_choose_level_for_group_at_event,
                            post_form_choose_level_for_group_at_event,
                        ): {
                            (
                                display_form_view_ticksheets_for_event_and_group,
                                post_form_view_ticksheets_for_event_and_group,
                            ): 0
                        }
                    }
                }
            }
        )
    )
)
