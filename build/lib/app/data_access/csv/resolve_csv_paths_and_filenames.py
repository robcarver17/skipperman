from os.path import join, exists
from pathlib import Path
from app.objects.constants import arg_not_passed


def get_path_and_filename_for_named_csv_file(
    master_data_path: str,
    generic_name_of_file_required: str,
    additional_file_identifiers: tuple = arg_not_passed,
):
    ## returns eg 'group_allocations', 'cadet_master_list.csv'
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


IDENTIFIED_CADETS_AT_EVENT_ID = "identified_cadets_at_event"
CADETS_AT_EVENT_ID = "cadets_at_event"
LIST_OF_CADETS_ON_COMMITTEE = "cadets_on_committee"

CADETS_WITH_GROUPS_ID = "cadets_with_groups_for_event"

LIST_OF_CADETS_FILE_ID = "cadet_master_list"
EVENT_FILE_IDENTIFIER = "list_of_events"
MAPPED_WA_EVENT_FILE_ID = "mapped_wa_event"
PRINT_OPTIONS_FILE_ID = "print_options"
ARRANGEMENT_OPTIONS_FILE_ID = "arrangement_options"
LIST_OF_PATROL_BOATS_FILE_ID = "list_of_patrol_boats"
LIST_OF_CLUB_DINGHIES_FILE_ID = "list_of_club_dinghies"
LIST_OF_DINGHIES_FILE_ID = "list_of_dinghies"
LIST_OF_CADETS_WITH_DINGHIES_AT_EVENT_FILE_ID = "list_of_cadets_with_dinghies"
LIST_OF_PATROL_BOATS_AND_VOLUNTEERS_FILE_ID = (
    "list_of_patrol_boats_and_volunteers_at_event"
)
LIST_OF_CLUB_DINGHIES_AND_CADETS_FILE_ID = "list_of_club_dinghies_with_cadets_at_event"
LIST_OF_VOLUNTEERS_FILE_ID = "list_of_volunteers"
LIST_OF_VOLUNTEER_SKILLS_FILE_ID = "list_of_volunteer_skills"
LIST_OF_VOLUNTEER_ASSOCIATIONS_FILE_ID = "list_of_cadet_volunteer_associations"
LIST_OF_VOLUNTEERS_AT_EVENT_FILE_ID = "list_of_volunteers_at_event"
LIST_OF_VOLUNTEER_TARGETS_AT_EVENT_FILE_ID = "list_of_volunteer_targets_at_event"

LIST_OF_IDENTIFIED_VOLUNTEERS_AT_EVENT_FILE_ID = (
    "list_of_identified_volunteers_at_event"
)
LIST_OF_VOLUNTEERS_IN_ROLES_FILE_ID = "list_of_volunteers_in_roles_at_event"
LIST_OF_QUALIFICATIONS = "list_of_qualifications"
LIST_OF_CADETS_WITH_QUALIFICATIONS = "list_of_cadets_with_qualifications"
LIST_OF_TICK_SUBSTAGES = "list_of_tick_sub_stages"
LIST_OF_TICK_SHEET_ITEMS = "list_of_tick_sheet_items"
LIST_OF_CADETS_WITH_TICK_LIST_ITEMS_FOR_EACH_CADET = (
    "list_of_cadets_with_tick_list_items_for_cadet"
)
LIST_OF_CADETS_WITH_CLOTHING_AT_EVENT = "list_of_cadets_with_clothing_at_event"
LIST_OF_CADETS_WITH_FOOD_AT_EVENT = "list_of_cadets_with_food_at_event"
LIST_OF_VOLUNTEERS_WITH_FOOD_AT_EVENT = "list_of_volunteers_with_food_at_event"


EVENT_MAPPING_FILE_ID = "wa_event_mapping"
FIELD_MAPPING_FILE_ID = "wa_field_mapping"
TEMPLATES_FIELD_MAPPING_FILE_ID = "wa_field_mapping_templates"
USERLIST_FILE_ID = "userlist"

## MODIFY THE FOLLOWING LINES TO CHANGE WHERE FILES LIVE AND THEIR
## THE FIRST ITEM IN EACH TUPLE IS THE PATH, THE SECOND IS THE FILENAME


_dict_of_filenames_and_paths = {
    LIST_OF_CADETS_FILE_ID: ("lists", "list_of_cadets.csv"),
    LIST_OF_CADETS_ON_COMMITTEE: ("lists", "list_of_cadets_on_committee.csv"),
    EVENT_FILE_IDENTIFIER: ("lists", "list_of_events.csv"),
    EVENT_MAPPING_FILE_ID: ("mapped_events", "wa_event_mapping.csv"),
    FIELD_MAPPING_FILE_ID: ("event_field_mapping", "wa_field_mapping_for_event_%s.csv"),
    TEMPLATES_FIELD_MAPPING_FILE_ID: ("event_field_mapping_templates", "%s.csv"),
    MAPPED_WA_EVENT_FILE_ID: ("mapped_events", "mapped_wa_event_%s.csv"),
    CADETS_AT_EVENT_ID: (
        "mapped_events",
        "cadets_at_event_%s.csv",
    ),
    IDENTIFIED_CADETS_AT_EVENT_ID: (
        "mapped_events",
        "identified_cadets_at_event_%s.csv",
    ),
    CADETS_WITH_GROUPS_ID: (
        "mapped_events",
        "cadets_with_groups_for_event_%s.csv",
    ),
    PRINT_OPTIONS_FILE_ID: ("lists", "print_options_for_report_%s.csv"),
    ARRANGEMENT_OPTIONS_FILE_ID: ("lists", "arrangement_options_for_report_%s.csv"),
    LIST_OF_VOLUNTEERS_FILE_ID: ("lists", "list_of_volunteers.csv"),
    LIST_OF_VOLUNTEER_SKILLS_FILE_ID: ("lists", "list_of_volunteers_skills.csv"),
    LIST_OF_VOLUNTEER_ASSOCIATIONS_FILE_ID: (
        "lists",
        "list_of_cadet_volunteer_associations.csv",
    ),
    LIST_OF_IDENTIFIED_VOLUNTEERS_AT_EVENT_FILE_ID: (
        "mapped_events",
        "list_of_identified_volunteers_at_event_%s.csv",
    ),
    LIST_OF_VOLUNTEERS_AT_EVENT_FILE_ID: (
        "mapped_events",
        "list_of_volunteers_at_event_%s.csv",
    ),
    LIST_OF_VOLUNTEERS_IN_ROLES_FILE_ID: (
        "mapped_events",
        "list_of_volunteers_in_roles_at_event_%s.csv",
    ),
    LIST_OF_VOLUNTEER_TARGETS_AT_EVENT_FILE_ID: (
        "mapped_events",
        "list_of_volunteer_role_targets_at_event_%s.csv",
    ),
    LIST_OF_PATROL_BOATS_FILE_ID: ("lists", "list_of_patrol_boats.csv"),
    LIST_OF_CLUB_DINGHIES_FILE_ID: ("lists", "list_of_club_dinghies.csv"),
    LIST_OF_PATROL_BOATS_AND_VOLUNTEERS_FILE_ID: (
        "mapped_events",
        "list_of_patrol_boats_and_volunteers_at_event_%s.csv",
    ),
    LIST_OF_CLUB_DINGHIES_AND_CADETS_FILE_ID: (
        "mapped_events",
        "list_of_club_dinghies_with_cadets_at_event_%s.csv",
    ),
    LIST_OF_DINGHIES_FILE_ID: ("lists", "list_of_dinghies.csv"),
    LIST_OF_CADETS_WITH_DINGHIES_AT_EVENT_FILE_ID: (
        "mapped_events",
        "list_of_cadets_with_dinghies_at_event_%s.csv",
    ),
    LIST_OF_QUALIFICATIONS: ("lists", "list_of_qualifications.csv"),
    LIST_OF_CADETS_WITH_QUALIFICATIONS: (
        "lists",
        "lists_of_cadets_with_qualifications.csv",
    ),
    LIST_OF_TICK_SUBSTAGES: ("lists", "list_of_tick_substages.csv"),
    LIST_OF_TICK_SHEET_ITEMS: ("lists", "list_of_tick_sheet_items.csv"),
    LIST_OF_CADETS_WITH_TICK_LIST_ITEMS_FOR_EACH_CADET: (
        "ticksheets",
        "tick_list_items_for_cadet_%s.csv",
    ),
    LIST_OF_CADETS_WITH_CLOTHING_AT_EVENT: (
        "mapped_events",
        "list_of_cadets_with_clothing_at_event_%s",
    ),
    LIST_OF_CADETS_WITH_FOOD_AT_EVENT: (
        "mapped_events",
        "list_of_cadets_with_food_at_event_%s",
    ),
    LIST_OF_VOLUNTEERS_WITH_FOOD_AT_EVENT: (
        "mapped_events",
        "list_of_volunteers_with_food_at_event_%s",
    ),
    USERLIST_FILE_ID: ("secure", "userlist.csv"),
}
