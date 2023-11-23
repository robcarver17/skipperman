from os.path import join, exists
from pathlib import Path
from app.objects.constants import arg_not_passed


def get_path_and_filename_for_named_csv_file(
    master_data_path: str,
    generic_name_of_file_required: str,
    additional_file_identifiers: tuple = arg_not_passed,
):

    ## returns eg 'cadets', 'cadet_master_list.csv'
    if additional_file_identifiers is arg_not_passed:
        additional_file_identifiers = ()

    try:
        path, filename = _dict_of_filenames_and_paths[generic_name_of_file_required]
    except KeyError:
        raise Exception(
            "generic file name '%s' not in possible set of configuration %s"
            % (
                generic_name_of_file_required,
                str(list(_dict_of_filenames_and_paths.keys())),
            )
        )

    filename_with_additional_items = filename % additional_file_identifiers

    resolved_path = join(master_data_path, path)
    if not exists(resolved_path):
        path = Path(resolved_path)
        path.mkdir(parents=True)

    resolved_path_and_filename = join(resolved_path, filename_with_additional_items)

    return resolved_path_and_filename


## MODIFY THE FOLLOWING LINES TO CHANGE WHERE FILES LIVE AND THEIR
## THE FIRST ITEM IN EACH TUPLE IS THE PATH, THE SECOND IS THE FILENAME
_dict_of_filenames_and_paths = dict(
    cadet_master_list=("cadets", "cadet_master_list.csv"),
    list_of_events=("events", "list_of_events.csv"),
    wa_event_mapping=("events", "wa_event_mapping.csv"),
    wa_field_mapping=("event_field_mapping", "wa_field_mapping_for_event_%s.csv"),
    mapped_wa_event_with_no_ids=("mapped_events", "mapped_wa_event_with_no_ids_%s.csv"),
    mapped_wa_event_with_ids=("mapped_events", "mapped_wa_event_with_ids_%s.csv"),
    master_event=(
        "mapped_events",
        "master_event_%s.csv",
    ),
    cadets_with_groups_for_event=(
        "cadets_with_groups_for_event",
        "cadets_with_groups_for_event_%s.csv",
    ),
)
