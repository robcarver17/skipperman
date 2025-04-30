from app.data_access.store.store import DataAccessMethod
from app.data_access.api.generic_api import GenericDataApi


def get_data_access_for_list_of_users(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        key="list_of_users",
        read_method=data.data_list_of_users.read,
        write_method=data.data_list_of_users.write,
    )


def get_data_access_for_list_of_cadets(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        key="list_of_cadets",
        read_method=data.data_list_of_cadets.read,
        write_method=data.data_list_of_cadets.write,
    )


def get_data_access_for_list_of_cadets_on_committee(
    data: GenericDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        key="list_of_cadets_on_committee",
        read_method=data.data_list_of_cadets_on_committee.read,
        write_method=data.data_list_of_cadets_on_committee.write,
    )


def get_data_access_for_list_of_cadets_with_tick_list_items_for_cadet_id(
    data: GenericDataApi, cadet_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_cadets_with_tick_list_items_for_cadet_id",
        data.data_list_of_cadets_with_tick_list_items.read_for_cadet_id,
        data.data_list_of_cadets_with_tick_list_items.write_for_cadet_id,
        cadet_id=cadet_id,
    )


def get_data_access_for_list_of_cadet_attendance_for_cadet_id(
    data: GenericDataApi, cadet_id: str
):
    return DataAccessMethod(
        "list_of_cadet_attendance_for_cadet_id",
        data.data_attendance_at_events_for_specific_cadet.read_attendance_for_cadet_id,
        data.data_attendance_at_events_for_specific_cadet.write_attendance_for_cadet_id,
        cadet_id=cadet_id,
    )


def get_data_access_for_list_of_qualifications(
    data: GenericDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_qualifications",
        data.data_list_of_qualifications.read,
        data.data_list_of_qualifications.write,
    )


def get_data_access_for_list_of_substages(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_substages",
        data.data_list_of_tick_sub_stages.read,
        data.data_list_of_tick_sub_stages.write,
    )


def get_data_access_for_list_of_tick_sheet_items(
    data: GenericDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_tick_sheet_items",
        data.data_list_of_tick_sheet_items.read,
        data.data_list_of_tick_sheet_items.write,
    )


def get_data_access_for_list_of_events(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_events", data.data_list_of_events.read, data.data_list_of_events.write
    )


def get_data_access_for_list_of_cadets_with_qualifications(
    data: GenericDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_cadets_with_qualifications",
        data.data_list_of_cadets_with_qualifications.read,
        data.data_list_of_cadets_with_qualifications.write,
    )


def get_data_access_for_cadets_with_groups(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "cadets_with_groups",
        data.data_list_of_cadets_with_groups.read_groups_for_event,
        data.data_list_of_cadets_with_groups.write_groups_for_event,
        event_id=event_id,
    )


def get_data_access_for_list_of_event_warnings(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_event_warnings",
        data.data_event_warnings.read,
        data.data_event_warnings.write,
        event_id=event_id,
    )


def get_data_access_for_cadets_with_ids_and_registration_data_at_event(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "cadets_at_event",
        read_method=data.data_cadets_at_event.read,
        write_method=data.data_cadets_at_event.write,
        event_id=event_id,
    )


def get_data_access_for_identified_cadets_at_event(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "identified_cadets_at_event",
        read_method=data.data_identified_cadets_at_event.read,
        write_method=data.data_identified_cadets_at_event.write,
        event_id=event_id,
    )


def get_data_access_for_identified_volunteers_at_event(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "identified_volunteers_at_event",
        read_method=data.data_list_of_identified_volunteers_at_event.read,
        write_method=data.data_list_of_identified_volunteers_at_event.write,
        event_id=event_id,
    )


def get_data_access_for_volunteers_at_event(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "volunteers_at_event",
        read_method=data.data_list_of_volunteers_at_event.read,
        write_method=data.data_list_of_volunteers_at_event.write,
        event_id=event_id,
    )


def get_data_access_for_volunteers_with_food_at_event(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "volunteers_at_event_with_food",
        read_method=data.data_list_of_volunteers_with_food_requirement_at_event.read,
        write_method=data.data_list_of_volunteers_with_food_requirement_at_event.write,
        event_id=event_id,
    )


def get_data_access_for_cadets_with_food_at_event(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "cadets_at_event_with_food",
        read_method=data.data_list_of_cadets_with_food_requirement_at_event.read,
        write_method=data.data_list_of_cadets_with_food_requirement_at_event.write,
        event_id=event_id,
    )


def get_data_access_for_cadets_with_clothing_at_event(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "cadets_at_event_with_clothing",
        read_method=data.data_list_of_cadets_with_clothing_at_event.read,
        write_method=data.data_list_of_cadets_with_clothing_at_event.write,
        event_id=event_id,
    )


def get_data_access_for_wa_field_mapping_at_event(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "wa_field_mapping_at_event",
        read_method=data.data_wa_field_mapping.read,
        write_method=data.data_wa_field_mapping.write,
        event_id=event_id,
    )


def get_data_access_for_wa_field_mapping_templates(
    data: GenericDataApi, template_name: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "wa_field_mapping_templates",
        read_method=data.data_wa_field_mapping.get_template,
        write_method=data.data_wa_field_mapping.write_template,
        template_name=template_name,
    )


def get_data_access_for_list_of_wa_field_mapping_templates(
    data: GenericDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "wa_field_mapping_templates_list",
        read_method=data.data_wa_field_mapping.get_list_of_templates,
        write_method=object,  ## not used
    )


def get_data_access_for_mapped_registration_data(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "mapped_wa_event",
        read_method=data.data_registration_data.read,
        write_method=data.data_registration_data.write,
        event_id=event_id,
    )


def get_data_access_for_list_of_cadets_at_event_with_club_dinghies(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_cadets_at_event_with_club_dinghies",
        read_method=data.data_list_of_cadets_at_event_with_club_dinghies.read,
        write_method=data.data_list_of_cadets_at_event_with_club_dinghies.write,
        event_id=event_id,
    )


def get_data_access_for_list_of_cadets_at_event_with_dinghies(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_cadets_with_dinghies_at_event",
        read_method=data.data_list_of_cadets_with_dinghies_at_event.read,
        write_method=data.data_list_of_cadets_with_dinghies_at_event.write,
        event_id=event_id,
    )


def get_data_access_for_wa_event_mapping(data: GenericDataApi):
    return DataAccessMethod(
        "wa_event_mapping",
        read_method=data.data_wa_event_mapping.read,
        write_method=data.data_wa_event_mapping.write,
    )


def get_data_access_for_list_of_volunteers(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_volunteers",
        read_method=data.data_list_of_volunteers.read,
        write_method=data.data_list_of_volunteers.write,
    )


def get_data_access_for_list_of_cadet_volunteer_associations_with_ids(
    data: GenericDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_cadet_volunteer_associations",
        read_method=data.data_list_of_cadet_volunteer_associations.read,
        write_method=data.data_list_of_cadet_volunteer_associations.write,
    )


def get_data_access_for_list_of_volunteers_in_roles_at_event(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_cadet_volunteer_associations",
        read_method=data.data_list_of_volunteers_in_roles_at_event.read,
        write_method=data.data_list_of_volunteers_in_roles_at_event.write,
        event_id=event_id,
    )


def get_data_access_for_list_of_voluteers_at_event_with_patrol_boats(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_voluteers_at_event_with_patrol_boats",
        read_method=data.data_list_of_volunteers_at_event_with_patrol_boats.read,
        write_method=data.data_list_of_volunteers_at_event_with_patrol_boats.write,
        event_id=event_id,
    )


def get_data_access_for_list_of_targets_for_role_at_event(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_targets_for_role_at_event",
        read_method=data.data_list_of_targets_for_role_at_event.read,
        write_method=data.data_list_of_targets_for_role_at_event.write,
        event_id=event_id,
    )


def get_data_access_for_list_of_volunteer_skills(
    data: GenericDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_volunteer_skills",
        read_method=data.data_list_of_volunteer_skills.read,
        write_method=data.data_list_of_volunteer_skills.write,
    )


def get_data_access_for_list_of_patrol_boats(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_patrol_boats",
        read_method=data.data_list_of_patrol_boats.read,
        write_method=data.data_list_of_patrol_boats.write,
    )


def get_data_access_for_print_options(
    data: GenericDataApi, report_name: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "print_options",
        read_method=data.data_print_options.read_for_report,
        write_method=data.data_print_options.write_for_report,
        report_name=report_name,
    )


def get_data_access_for_arrangement_and_group_order_options(
    data: GenericDataApi, report_name: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "arrangement_options",
        read_method=data.data_arrangement_and_group_order_options.read_for_report,
        write_method=data.data_arrangement_and_group_order_options.write_for_report,
        report_name=report_name,
    )


def get_data_access_for_list_of_boat_classes(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_dinghies",
        read_method=data.data_list_of_dinghies.read,
        write_method=data.data_list_of_dinghies.write,
    )


def get_data_access_for_list_of_club_dinghies(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_club_dinghies",
        read_method=data.data_List_of_club_dinghies.read,
        write_method=data.data_List_of_club_dinghies.write,
    )


def get_data_access_for_list_of_club_dinghies_with_limits(
    data: GenericDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_club_dinghies_with_limits",
        read_method=data.data_List_of_club_dinghy_limits.read,
        write_method=data.data_List_of_club_dinghy_limits.write,
    )


def get_data_access_for_list_of_groups(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_groups",
        read_method=data.data_list_of_groups.read,
        write_method=data.data_list_of_groups.write,
    )


def get_data_access_for_list_of_skills(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_skills",
        read_method=data.data_list_of_skills.read,
        write_method=data.data_list_of_skills.write,
    )


def get_data_access_for_list_of_teams(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_teams",
        read_method=data.data_list_of_teams.read,
        write_method=data.data_list_of_teams.write,
    )


def get_data_access_for_list_of_roles(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_roles",
        read_method=data.data_list_of_roles.read,
        write_method=data.data_list_of_roles.write,
    )


def get_data_access_for_list_of_teams_and_roles_with_ids(
    data: GenericDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_teams_and_roles_with_ids",
        read_method=data.data_list_of_teams_and_roles_with_ids.read,
        write_method=data.data_list_of_teams_and_roles_with_ids.write,
    )


def get_data_access_for_list_of_notes_for_groups(
    data: GenericDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_notes_for_groups",
        read_method=data.data_list_of_group_notes_at_event.read_all_notes,
        write_method=data.data_list_of_group_notes_at_event.write_notes,
    )
