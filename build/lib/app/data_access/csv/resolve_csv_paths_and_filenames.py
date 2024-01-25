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

    filename = file_from_generic(generic_name_of_file_required)
    filename_with_additional_items = filename % additional_file_identifiers
    resolved_path = get_path_for_generic_name(
        master_data_path=master_data_path,
        generic_name_of_file_required=generic_name_of_file_required,
    )

    resolved_path_and_filename = join(resolved_path, filename_with_additional_items)

    return resolved_path_and_filename


def get_path_for_generic_name(
    master_data_path: str,
    generic_name_of_file_required: str,
):
    path = path_from_generic(generic_name_of_file_required)
    resolved_path = join(master_data_path, path)
    if not exists(resolved_path):
        path = Path(resolved_path)
        path.mkdir(parents=True)

    return resolved_path


def path_from_generic(generic_name_of_file_required):
    try:
        path, __ = _dict_of_filenames_and_paths[generic_name_of_file_required]
    except KeyError:
        raise Exception(
            "generic file name '%s' not in possible set of configuration %s"
            % (
                generic_name_of_file_required,
                str(list(_dict_of_filenames_and_paths.keys())),
            )
        )

    return path


def file_from_generic(generic_name_of_file_required):
    try:
        __, filename = _dict_of_filenames_and_paths[generic_name_of_file_required]
    except KeyError:
        raise Exception(
            "generic file name '%s' not in possible set of configuration %s"
            % (
                generic_name_of_file_required,
                str(list(_dict_of_filenames_and_paths.keys())),
            )
        )

    return filename


## MODIFY THE FOLLOWING LINES TO CHANGE WHERE FILES LIVE AND THEIR
## THE FIRST ITEM IN EACH TUPLE IS THE PATH, THE SECOND IS THE FILENAME
_dict_of_filenames_and_paths = dict(
    cadet_master_list=("cadets", "cadet_master_list.csv"),
    list_of_events=("events", "list_of_events.csv"),
    wa_event_mapping=("events", "wa_event_mapping.csv"),
    wa_field_mapping=("event_field_mapping", "wa_field_mapping_for_event_%s.csv"),
    wa_field_mapping_templates=("event_field_mapping_templates", "%s.csv"),
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
    print_options=("options", "print_options_for_report_%s.csv"),
    list_of_volunteers=("volunteers", "list_of_volunteers.csv"),
list_of_volunteer_skills=("volunteers", "list_of_volunteers_skills.csv"),
list_of_cadet_volunteer_associations=("volunteers", "list_of_cadet_volunteer_associations.csv"),
list_of_volunteers_at_event=("volunteers_at_event", "list_of_volunteers_at_event_%s.csv"),
list_of_cadets_without_volunteers_at_event=("volunteers_at_event", "list_of_cadets_without_volunteers_at_event.csv")
)
