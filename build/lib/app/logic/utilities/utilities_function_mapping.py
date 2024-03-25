from app.logic.utilities.ENTRY_utilities_menu import display_form_utilities_menu, post_form_utilities_menu
from app.logic.utilities.data_and_backups.data_and_backups import display_form_data_and_backups, post_form_data_and_backups
from app.logic.utilities.data_and_backups.restore_backup_from_snapshot import display_form_view_of_snapshots, \
    post_form_view_of_snapshots

from app.objects.abstract_objects.form_function_mapping import   DisplayAndPostFormFunctionMaps, NestedDictOfMappings
from app.logic.utilities.data_and_backups.restore_backup_from_local import display_form_for_upload_backup, post_form_upload_backup_file


utilities_function_mapping = DisplayAndPostFormFunctionMaps.from_nested_dict_of_functions(
    NestedDictOfMappings(
    {
        (display_form_utilities_menu, post_form_utilities_menu): {
            (display_form_data_and_backups, post_form_data_and_backups):{
                (display_form_for_upload_backup, post_form_upload_backup_file):0,
                (display_form_view_of_snapshots, post_form_view_of_snapshots): 0
            }
        }

    }
    )
)
