from copy import copy
from typing import Callable

from app.data_access.csv.csv_api import CsvDataApi


class DataAccessMethod:
    def __init__(self, key, data_object_with_methods, **kwargs):
        try:
            self._read_method = data_object_with_methods.read
            self._write_method = data_object_with_methods.write
        except:
            raise Exception("Data object identified with key %s should have read and write methods" % key)

        copied_key = copy(key)
        if len(kwargs) == 0:
            self._method_kwargs = {}
        else:
            self._method_kwargs = kwargs
            kwargs_described = ",".join(["%s:%s" % (key, item) for key, item in kwargs.items()])
            copied_key = "%s_(%s)" % (copied_key, kwargs_described)

        self._key = copied_key

    @property
    def read_method(self) -> Callable:
        return self._read_method

    @property
    def write_method(self) -> Callable:
        return self._write_method

    @property
    def key(self) -> str:
        return self._key

    @property
    def method_kwargs(self) -> dict:
        return self._method_kwargs


def get_data_access_for_list_of_users(data: CsvDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        key="list_of_users",
        data_object_with_methods=data.data_list_of_users,
    )


def get_data_access_for_list_of_cadets(data: CsvDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        key="list_of_cadets",
        data_object_with_methods=data.data_list_of_cadets,
    )


def get_data_access_for_list_of_cadets_on_committee(
    data: CsvDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        key="list_of_cadets_on_committee",
        data_object_with_methods=data.data_list_of_cadets_on_committee
    )


def get_data_access_for_list_of_cadets_with_tick_list_items_for_cadet_id(
    data: CsvDataApi, cadet_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_cadets_with_tick_list_items_for_cadet_id",
        data_object_with_methods=data.data_list_of_cadets_with_tick_list_items,
        cadet_id=cadet_id,
    )


def get_data_access_for_list_of_cadet_attendance_for_cadet_id(
    data: CsvDataApi, cadet_id: str
):
    return DataAccessMethod(
        "list_of_cadet_attendance_for_cadet_id",
        data_object_with_methods=data.data_attendance_at_events_for_specific_cadet,
        cadet_id=cadet_id,
    )


def get_data_access_for_list_of_qualifications(
    data: CsvDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_qualifications",
    data_object_with_methods=data.data_list_of_qualifications
    )


def get_data_access_for_list_of_substages(data: CsvDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_substages",
        data_object_with_methods=data.data_list_of_tick_sub_stages
    )


def get_data_access_for_list_of_tick_sheet_items(
    data: CsvDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_tick_sheet_items",
        data_object_with_methods=data.data_list_of_tick_sheet_items
    )


def get_data_access_for_list_of_events(data: CsvDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_events", data_object_with_methods=data.data_list_of_events
    )


def get_data_access_for_list_of_cadets_with_qualifications(
    data: CsvDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_cadets_with_qualifications",
        data_object_with_methods=data.data_list_of_cadets_with_qualifications
    )


def get_data_access_for_cadets_with_groups(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "cadets_with_groups",
        data_object_with_methods=data.data_list_of_cadets_with_groups,
        event_id=event_id,
    )


def get_data_access_for_list_of_event_warnings(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_event_warnings",
        data_object_with_methods=data.data_event_warnings,
        event_id=event_id,
    )


def get_data_access_for_cadets_with_ids_and_registration_data_at_event(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "cadets_at_event",
        data_object_with_methods=data.data_cadets_at_event,
        event_id=event_id,
    )


def get_data_access_for_identified_cadets_at_event(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "identified_cadets_at_event",
        data_object_with_methods=data.data_identified_cadets_at_event,
        event_id=event_id,
    )


def get_data_access_for_identified_volunteers_at_event(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "identified_volunteers_at_event",
        data_object_with_methods=data.data_list_of_identified_volunteers_at_event,
        event_id=event_id,
    )


def get_data_access_for_volunteers_at_event(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "volunteers_at_event",
        data_object_with_methods=data.data_list_of_volunteers_at_event,
        event_id=event_id,
    )


def get_data_access_for_volunteers_with_food_at_event(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "volunteers_at_event_with_food",
        data_object_with_methods=data.data_list_of_volunteers_with_food_requirement_at_event,
        event_id=event_id,
    )


def get_data_access_for_cadets_with_food_at_event(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "cadets_at_event_with_food",
        data_object_with_methods=data.data_list_of_cadets_with_food_requirement_at_event,
        event_id=event_id,
    )


def get_data_access_for_cadets_with_clothing_at_event(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "cadets_at_event_with_clothing",
        data_object_with_methods=data.data_list_of_cadets_with_clothing_at_event,
        event_id=event_id,
    )


def get_data_access_for_wa_field_mapping_at_event(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "wa_field_mapping_at_event",
        data_object_with_methods=data.data_wa_field_mapping,
        event_id=event_id,
    )


def get_data_access_for_wa_field_mapping_templates(
    data: CsvDataApi, template_name: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "wa_field_mapping_templates",
        data_object_with_methods=data.data_wa_field_mapping_templates,
        template_name=template_name,
    )


def get_data_access_for_list_of_wa_field_mapping_templates(
    data: CsvDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "wa_field_mapping_templates_list",
        data_object_with_methods=data.data_wa_field_mapping_list_of_templates
    )


def get_data_access_for_mapped_registration_data(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "mapped_wa_event",
        data_object_with_methods=data.data_registration_data,
        event_id=event_id,
    )


def get_data_access_for_list_of_cadets_at_event_with_club_dinghies(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_cadets_at_event_with_club_dinghies",
        data_object_with_methods=data.data_list_of_cadets_at_event_with_club_dinghies,
        event_id=event_id,
    )


def get_data_access_for_list_of_volunteers_at_event_with_club_dinghies(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_volunteers_at_event_with_club_dinghies",
        data_object_with_methods=data.data_list_of_volunteers_at_event_with_club_dinghies,
        event_id=event_id,
    )

def get_access_for_list_of_last_roles_across_events_for_volunteers(
        data: CsvDataApi
) -> DataAccessMethod:
    return DataAccessMethod(
        key= "list_of_last_roles_across_events_for_volunteers",
        data_object_with_methods=data.data_list_of_last_roles_across_events_for_volunteers
    )

def get_data_access_for_list_of_cadets_at_event_with_dinghies(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_cadets_with_dinghies_at_event",
        data_object_with_methods=data.data_list_of_cadets_with_dinghies_at_event,
        event_id=event_id,
    )


def get_data_access_for_wa_event_mapping(data: CsvDataApi):
    return DataAccessMethod(
        "wa_event_mapping",
        data_object_with_methods=data.data_wa_event_mapping
    )


def get_data_access_for_list_of_volunteers(data: CsvDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_volunteers",
        data_object_with_methods=data.data_list_of_volunteers
    )


def get_data_access_for_list_of_cadet_volunteer_associations_with_ids(
    data: CsvDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_cadet_volunteer_associations",
        data_object_with_methods=data.data_list_of_cadet_volunteer_associations
    )


def get_data_access_for_list_of_volunteers_in_roles_at_event(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_cadet_volunteer_associations",
        data_object_with_methods=data.data_list_of_volunteers_in_roles_at_event,
        event_id=event_id,
    )


def get_data_access_for_list_of_voluteers_at_event_with_patrol_boats(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_voluteers_at_event_with_patrol_boats",
        data_object_with_methods=data.data_list_of_volunteers_at_event_with_patrol_boats,
        event_id=event_id,
    )


def get_data_access_for_list_of_targets_for_role_at_event(
    data: CsvDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_targets_for_role_at_event",
        data_object_with_methods=data.data_list_of_targets_for_role_at_event,
        event_id=event_id,
    )


def get_data_access_for_list_of_volunteer_skills(
    data: CsvDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_volunteer_skills",
        data_object_with_methods=data.data_list_of_volunteer_skills
    )


def get_data_access_for_list_of_patrol_boats(data: CsvDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_patrol_boats",
        data_object_with_methods=data.data_list_of_patrol_boats
    )


def get_data_access_for_print_options(
    data: CsvDataApi, report_name: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "print_options",
        data_object_with_methods=data.data_print_options,
        report_name=report_name,
    )


def get_data_access_for_arrangement_and_group_order_options(
    data: CsvDataApi, report_name: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "arrangement_options",
        data_object_with_methods=data.data_arrangement_and_group_order_options,
        report_name=report_name,
    )


def get_data_access_for_list_of_boat_classes(data: CsvDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_dinghies",
        data_object_with_methods=data.data_list_of_dinghies
    )


def get_data_access_for_list_of_club_dinghies(data: CsvDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_club_dinghies",
        data_object_with_methods=data.data_List_of_club_dinghies
    )


def get_data_access_for_list_of_club_dinghies_with_limits(
    data: CsvDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_club_dinghies_with_limits",
        data_object_with_methods=data.data_List_of_club_dinghy_limits
    )


def get_data_access_for_list_of_groups(data: CsvDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_groups",
        data_object_with_methods=data.data_list_of_groups
    )


def get_data_access_for_list_of_skills(data: CsvDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_skills",
        data_object_with_methods=data.data_list_of_skills
    )


def get_data_access_for_list_of_teams(data: CsvDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_teams",
        data_object_with_methods=data.data_list_of_teams
    )


def get_data_access_for_list_of_roles(data: CsvDataApi) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_roles",
        data_object_with_methods=data.data_list_of_roles
    )


def get_data_access_for_list_of_teams_and_roles_with_ids(
    data: CsvDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_teams_and_roles_with_ids",
        data_object_with_methods=data.data_list_of_teams_and_roles_with_ids
    )



def get_data_access_for_list_of_notes_for_groups(
    data: CsvDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_notes_for_groups",
        data_object_with_methods=data.data_list_of_group_notes_at_event
    )


def get_data_access_for_list_of_notes(
    data: CsvDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_notes",
        data_object_with_methods=data.data_list_of_notes
    )


def get_data_access_for_list_of_patrol_boat_labels(
    data: CsvDataApi,
) -> DataAccessMethod:
    return DataAccessMethod(
        "list_of_patrol_boat_labels",
        data_object_with_methods=data.data_list_of_patrol_boat_labels
    )
