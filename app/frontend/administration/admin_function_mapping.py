from app.objects_OLD.abstract_objects.form_function_mapping import (
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

admin_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
    NestedDictOfMappings(
        {
            (display_form_main_admin_page, post_form_main_admin_page): {
                (display_form_security, post_form_security): 0,
                (display_form_data, post_form_data): 0,
            }
        }
    )
)
