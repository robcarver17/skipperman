from app.frontend.utilities.ENTRY_utilities_menu import (
    display_form_utilities_menu,
    post_form_utilities_menu,
)
from app.frontend.utilities.files.ENTRY_files import (
    display_form_file_management,
    post_form_file_management,
)
from app.frontend.utilities.data_and_backups.ENTRY_data_and_backups import (
    display_form_data_and_backups,
    post_form_data_and_backups,
)
from app.frontend.utilities.data_and_backups.restore_backup_from_snapshot import (
    display_form_view_of_snapshots,
    post_form_view_of_snapshots,
)

from app.objects_OLD.abstract_objects.form_function_mapping import (
    DisplayAndPostFormFunctionMaps,
    NestedDictOfMappings,
)
from app.frontend.utilities.data_and_backups.restore_backup_from_local import (
    display_form_for_upload_backup,
    post_form_upload_backup_file,
)
from app.frontend.utilities.files.upload_file import (
    display_form_for_upload_public_file,
    post_form_for_upload_public_file,
)
from app.frontend.utilities.files.replace_files import (
    display_form_to_replace_selected_files,
    post_form_to_replace_selected_files,
)
from app.frontend.utilities.cleaning.ENTRY_cleaning import (
    display_form_for_event_cleaning,
    post_form_view_of_event_data_cleaning,
)

utilities_function_mapping = (
    DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
        NestedDictOfMappings(
            {
                (display_form_utilities_menu, post_form_utilities_menu): {
                    (display_form_data_and_backups, post_form_data_and_backups): {
                        (
                            display_form_for_upload_backup,
                            post_form_upload_backup_file,
                        ): 0,
                        (
                            display_form_view_of_snapshots,
                            post_form_view_of_snapshots,
                        ): 0,
                    },
                    (display_form_file_management, post_form_file_management): {
                        (
                            display_form_for_upload_public_file,
                            post_form_for_upload_public_file,
                        ): 0,
                        (
                            display_form_to_replace_selected_files,
                            post_form_to_replace_selected_files,
                        ): 0,
                    },
                    (
                        display_form_for_event_cleaning,
                        post_form_view_of_event_data_cleaning,
                    ): 0,
                },
            }
        )
    )
)
