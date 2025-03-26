from dataclasses import dataclass
from typing import Callable, Dict, Union, List

from app.objects.composed.cadets_with_all_event_info import (
    compose_dict_of_all_event_info_for_cadet,
)
from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import (
    compose_dict_of_cadets_and_boat_classes_and_partners,
)
from app.objects.composed.cadets_at_event_with_club_dinghies import (
    compose_dict_of_cadets_and_club_dinghies_at_event,
)
from app.objects.composed.cadets_at_event_with_groups import (
    compose_dict_of_cadets_with_days_and_groups_at_event,
)
from app.objects.composed.cadets_at_event_with_registration_data import (
    compose_dict_of_cadets_with_event_data,
)

from app.data_access.store.data_access import *
from app.objects.composed.cadet_volunteer_associations import (
    create_list_of_cadet_volunteer_associations_from_underlying_data,
    compose_dict_of_cadets_associated_with_volunteers,
    compose_dict_of_volunteers_associated_with_cadets,
)
from app.objects.composed.cadets_with_qualifications import (
    create_dict_of_qualifications_for_cadets,
)
from app.objects.composed.clothing_at_event import (
    compose_dict_of_cadets_with_clothing_at_event,
)
from app.objects.composed.club_dinghy_limits import compose_club_dinghy_limits
from app.objects.composed.committee import (
    create_list_of_cadet_committee_members_from_underlying_data,
)
from app.objects.composed.food_at_event import (
    compose_dict_of_cadets_with_food_requirements_at_event,
    compose_dict_of_volunteers_with_food_requirements_at_event,
)
from app.objects.composed.roles_and_teams import compose_dict_of_teams_with_roles
from app.objects.composed.ticks_in_dicts import (
    create_qualifications_and_tick_items_as_dict_from_underyling,
)
from app.objects.composed.ticksheet import (
    compose_dict_of_cadets_with_qualifications_and_ticks,
)
from app.objects.composed.volunteer_roles import compose_list_of_roles_with_skills
from app.objects.composed.volunteer_with_group_and_role_at_event import (
    compose_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups,
)
from app.objects.composed.volunteers_at_event_with_patrol_boats import (
    compose_dict_of_patrol_boats_by_day_for_volunteer_at_event,
)
from app.objects.composed.volunteers_at_event_with_registration_data import (
    compose_dict_of_registration_data_for_volunteer_at_event,
)
from app.objects.composed.volunteers_with_all_event_data import (
    compose_dict_of_all_event_data_for_volunteers,
)
from app.objects.composed.volunteers_with_skills import compose_dict_of_volunteer_skills
from app.objects.exceptions import arg_not_passed
from app.objects.composed.dict_of_volunteer_role_targets import (
    compose_list_of_targets_for_roles_at_event,
)


@dataclass
class UnderlyingObjectDefinition:
    data_store_method_function: Callable
    required_keys: List[str] = arg_not_passed

    @property
    def key(self):
        return "Underlying_" + self.data_store_method_function.__name__

    def matching_kwargs(self, **kwargs) -> dict:
        return matching_kwargs(self, **kwargs)


@dataclass
class IterableObjectDefinition:
    underlying_object_definition: UnderlyingObjectDefinition
    required_key_for_iteration: str
    key_for_underlying_object: str

    @property
    def required_keys(self) -> List[str]:
        return [self.required_key_for_iteration]

    @property
    def key(self):
        return "Iterable_" + self.underlying_object_definition.key

    def matching_kwargs(self, **kwargs) -> dict:
        return matching_kwargs(self, **kwargs)


@dataclass
class DerivedObjectDefinition:
    composition_function: Callable
    dict_of_arguments_and_underlying_object_definitions: Dict[
        str,
        Union[
            "DerivedObjectDefinition",
            UnderlyingObjectDefinition,
            IterableObjectDefinition,
        ],
    ]
    dict_of_properties_and_underlying_object_definitions_if_modified: Dict[
        str,
        Union[
            "DerivedObjectDefinition",
            UnderlyingObjectDefinition,
            IterableObjectDefinition,
        ],
    ]
    required_keys: List[str] = arg_not_passed

    @property
    def key(self):
        return "Derived_" + self.composition_function.__name__

    def matching_kwargs(self, **kwargs) -> dict:
        return matching_kwargs(self, **kwargs)


def matching_kwargs(
    object_with_kwargs: Union[
        UnderlyingObjectDefinition, IterableObjectDefinition, DerivedObjectDefinition
    ],
    **kwargs,
) -> dict:
    required_keys = object_with_kwargs.required_keys
    if required_keys is arg_not_passed:
        required_keys = []

    try:
        new_kwargs = dict([(key, kwargs[key]) for key in required_keys])
    except KeyError as e:
        raise Exception("%s missing argument when calling object definition" % str(e))

    return new_kwargs


######## LIST OF OBJECT DEFINITIONS

# UNDERLYING

object_definition_for_list_of_cadets = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadets
)
object_definition_for_list_of_cadet_committee_members_with_id = (
    UnderlyingObjectDefinition(
        data_store_method_function=get_data_access_for_list_of_cadets_on_committee
    )
)
object_definition_for_list_of_cadets_and_qualifications_with_ids = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadets_with_qualifications
)

object_definition_for_mapped_registration_data = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_mapped_registration_data,
    required_keys=["event_id"],
)

object_definition_for_identified_cadets_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_identified_cadets_at_event,
    required_keys=["event_id"],
)

object_definition_for_identified_volunteers_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_identified_volunteers_at_event,
    required_keys=["event_id"],
)

object_definition_for_cadets_with_ids_and_registration_data_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_cadets_with_ids_and_registration_data_at_event,
    required_keys=["event_id"],
)
object_definition_for_cadets_with_ids_and_groups_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_cadets_with_groups,
    required_keys=["event_id"],
)

object_definition_for_cadets_with_ids_and_boat_classes_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadets_at_event_with_dinghies,
    required_keys=["event_id"],
)

object_definition_for_cadets_with_ids_and_club_dinghies_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadets_at_event_with_club_dinghies,
    required_keys=["event_id"],
)

object_definition_for_volunteers = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_volunteers
)

object_definition_for_volunteer_skills_with_ids = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_volunteer_skills
)

object_definition_for_volunteer_and_cadet_associations_with_ids = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadet_volunteer_associations_with_ids
)

object_definition_for_list_of_users = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_users
)

object_definition_for_list_of_events = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_events
)

object_definition_for_list_of_boat_classes = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_boat_classes
)

object_definition_for_list_of_club_dinghies = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_club_dinghies
)

object_definition_for_list_of_club_dinghy_limits_with_ids = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_club_dinghies_with_limits
)


object_definition_for_list_of_patrol_boats = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_patrol_boats
)

object_definition_for_list_of_qualifications = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_qualifications
)

object_definition_for_list_of_tick_sheet_items = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_tick_sheet_items
)

object_definition_for_list_of_tick_sub_stages = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_substages
)

object_definition_for_list_of_groups = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_groups
)

object_definition_for_list_of_skills = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_skills
)

object_definition_for_list_of_roles_with_skill_ids = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_roles
)

object_definition_for_list_of_teams = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_teams
)

object_definition_for_list_of_teams_and_roles_with_ids = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_teams_and_roles_with_ids
)

object_definition_for_list_of_volunteers_with_ids_roles_and_groups_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_volunteers_in_roles_at_event,
    required_keys=["event_id"],
)

object_definition_for_list_of_volunteers_with_ids_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_volunteers_at_event,
    required_keys=["event_id"],
)

object_definition_for_list_of_volunteers_with_ids_and_patrol_boats_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_voluteers_at_event_with_patrol_boats,
    required_keys=["event_id"],
)

object_definition_for_list_of_cadets_with_tick_list_items_for_cadet_id = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadets_with_tick_list_items_for_cadet_id,
    required_keys=["cadet_id"],  ##returns ListOfCadetsWithTickListItems
)

object_definition_for_field_mappings_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_wa_field_mapping_at_event,
    required_keys=["event_id"],
)

object_definition_for_list_of_field_mapping_templates = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_wa_field_mapping_templates,
)

object_definition_for_field_mapping_templates = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_wa_field_mapping_templates,
    required_keys=["template_name"],
)

object_definition_for_wa_event_mapping = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_wa_event_mapping
)

object_definition_for_list_of_targets_for_role_id_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_targets_for_role_at_event,
    required_keys=["event_id"],
)

object_definition_for_cadet_ids_with_clothing_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_cadets_with_clothing_at_event,
    required_keys=["event_id"],
)

object_definition_for_cadet_ids_with_food_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_cadets_with_food_at_event,
    required_keys=["event_id"],
)
object_definition_for_volunteer_ids_with_food_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_volunteers_with_food_at_event,
    required_keys=["event_id"],
)

object_definition_for_print_options = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_print_options,
    required_keys=["report_name"],
)

object_definition_for_report_arrangement_and_group_order_options = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_arrangement_and_group_order_options,
    required_keys=["report_name"],
)

## ITERABLE
object_definition_for_dict_of_cadet_ids_with_tick_list_items_for_cadet_id = IterableObjectDefinition(
    underlying_object_definition=object_definition_for_list_of_cadets_with_tick_list_items_for_cadet_id,
    required_key_for_iteration="list_of_cadet_ids",
    key_for_underlying_object="cadet_id",
)


## DERIVED


object_definition_for_list_of_cadet_committee_members = DerivedObjectDefinition(
    composition_function=create_list_of_cadet_committee_members_from_underlying_data,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_cadets=object_definition_for_list_of_cadets,
        list_of_cadets_with_id_on_commitee=object_definition_for_list_of_cadet_committee_members_with_id,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_cadets_with_id_on_commitee=object_definition_for_list_of_cadet_committee_members_with_id
    ),
)

object_definition_for_dict_of_qualifications_for_cadets = DerivedObjectDefinition(
    composition_function=create_dict_of_qualifications_for_cadets,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_qualifications=object_definition_for_list_of_qualifications,
        list_of_cadets=object_definition_for_list_of_cadets,
        list_of_cadets_with_ids_and_qualifications=object_definition_for_list_of_cadets_and_qualifications_with_ids,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_cadets_with_ids_and_qualifications=object_definition_for_list_of_cadets_and_qualifications_with_ids
    ),
)

object_definition_for_volunteer_and_cadet_associations = DerivedObjectDefinition(
    composition_function=create_list_of_cadet_volunteer_associations_from_underlying_data,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_cadets=object_definition_for_list_of_cadets,
        list_of_volunteers=object_definition_for_volunteers,
        list_of_cadet_volunteer_associations_with_ids=object_definition_for_volunteer_and_cadet_associations_with_ids,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_cadet_volunteer_associations_with_ids=object_definition_for_volunteer_and_cadet_associations_with_ids
    ),
)

object_definition_for_qualifications_and_tick_items_as_dict = DerivedObjectDefinition(
    composition_function=create_qualifications_and_tick_items_as_dict_from_underyling,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_qualifications=object_definition_for_list_of_qualifications,
        list_of_tick_sheet_items=object_definition_for_list_of_tick_sheet_items,
        list_of_tick_sub_stages=object_definition_for_list_of_tick_sub_stages,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_tick_sheet_items=object_definition_for_list_of_tick_sheet_items,
        list_of_tick_sub_stages=object_definition_for_list_of_tick_sub_stages,
    ),
)

object_definition_for_dict_of_volunteers_with_skills = DerivedObjectDefinition(
    composition_function=compose_dict_of_volunteer_skills,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_volunteers=object_definition_for_volunteers,
        list_of_skills=object_definition_for_list_of_skills,
        list_of_volunteers_with_skills_and_ids=object_definition_for_volunteer_skills_with_ids,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_volunteers_with_skills_and_ids=object_definition_for_volunteer_skills_with_ids
    ),
)

object_definition_for_list_of_roles_with_skills = DerivedObjectDefinition(
    composition_function=compose_list_of_roles_with_skills,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_roles_with_skill_ids=object_definition_for_list_of_roles_with_skill_ids,
        list_of_skills=object_definition_for_list_of_skills,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_roles_with_skill_ids=object_definition_for_list_of_roles_with_skill_ids
    ),
)

object_definition_for_dict_of_teams_with_roles = DerivedObjectDefinition(
    composition_function=compose_dict_of_teams_with_roles,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_teams_and_roles_with_ids=object_definition_for_list_of_teams_and_roles_with_ids,
        list_of_teams=object_definition_for_list_of_teams,
        list_of_roles_with_skills=object_definition_for_list_of_roles_with_skills,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_teams_and_roles_with_ids=object_definition_for_list_of_teams_and_roles_with_ids
    ),
)

object_definition_for_dict_of_cadets_with_registration_data_at_event = DerivedObjectDefinition(
    composition_function=compose_dict_of_cadets_with_event_data,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_events=object_definition_for_list_of_events,
        list_of_cadets=object_definition_for_list_of_cadets,
        list_of_cadets_with_id_at_event=object_definition_for_cadets_with_ids_and_registration_data_at_event,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_cadets_with_id_at_event=object_definition_for_cadets_with_ids_and_registration_data_at_event
    ),
    required_keys=["event_id"],
)

object_definition_for_dict_of_cadets_with_groups_at_event = DerivedObjectDefinition(
    composition_function=compose_dict_of_cadets_with_days_and_groups_at_event,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_cadets=object_definition_for_list_of_cadets,
        list_of_groups=object_definition_for_list_of_groups,
        list_of_events=object_definition_for_list_of_events,
        list_of_cadet_ids_with_groups=object_definition_for_cadets_with_ids_and_groups_at_event,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_cadet_ids_with_groups=object_definition_for_cadets_with_ids_and_groups_at_event
    ),
    required_keys=["event_id"],
)

object_definition_for_dict_of_cadets_and_boat_classes_and_partners = DerivedObjectDefinition(
    composition_function=compose_dict_of_cadets_and_boat_classes_and_partners,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_cadets=object_definition_for_list_of_cadets,
        list_of_events=object_definition_for_list_of_events,
        list_of_boat_classes=object_definition_for_list_of_boat_classes,
        list_of_cadets_at_event_with_boat_class_and_partners_with_ids=object_definition_for_cadets_with_ids_and_boat_classes_at_event,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_cadets_at_event_with_boat_class_and_partners_with_ids=object_definition_for_cadets_with_ids_and_boat_classes_at_event
    ),
    required_keys=["event_id"],
)


object_definition_for_dict_of_cadets_and_club_dinghies_at_event = DerivedObjectDefinition(
    composition_function=compose_dict_of_cadets_and_club_dinghies_at_event,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_cadets=object_definition_for_list_of_cadets,
        list_of_events=object_definition_for_list_of_events,
        list_of_club_dinghies=object_definition_for_list_of_club_dinghies,
        list_of_cadets_at_event_with_id_and_club_dinghy=object_definition_for_cadets_with_ids_and_club_dinghies_at_event,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_cadets_at_event_with_id_and_club_dinghy=object_definition_for_cadets_with_ids_and_club_dinghies_at_event
    ),
    required_keys=["event_id"],
)

object_definition_for_club_dinghy_limits = DerivedObjectDefinition(
    composition_function=compose_club_dinghy_limits,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_club_dinghy_limits = object_definition_for_list_of_club_dinghy_limits_with_ids,
list_of_club_dinghies = object_definition_for_list_of_club_dinghies,
list_of_events = object_definition_for_list_of_events),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_club_dinghy_limits=object_definition_for_list_of_club_dinghy_limits_with_ids
    )
)

object_definition_for_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups = DerivedObjectDefinition(
    composition_function=compose_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_events=object_definition_for_list_of_events,
        list_of_groups=object_definition_for_list_of_groups,
        list_of_roles_with_skills=object_definition_for_list_of_roles_with_skills,
        list_of_volunteers=object_definition_for_volunteers,
        list_of_volunteers_with_id_in_role_at_event=object_definition_for_list_of_volunteers_with_ids_roles_and_groups_at_event,
        dict_of_teams_and_roles=object_definition_for_dict_of_teams_with_roles,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_volunteers_with_id_in_role_at_event=object_definition_for_list_of_volunteers_with_ids_roles_and_groups_at_event,
    ),
    required_keys=["event_id"],
)

object_definition_for_dict_of_registration_data_for_volunteers_at_event = DerivedObjectDefinition(
    composition_function=compose_dict_of_registration_data_for_volunteer_at_event,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_volunteers=object_definition_for_volunteers,
        list_of_events=object_definition_for_list_of_events,
        list_of_volunteers_at_event_with_id=object_definition_for_list_of_volunteers_with_ids_at_event,
        list_of_cadets=object_definition_for_list_of_cadets,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_volunteers_at_event_with_id=object_definition_for_list_of_volunteers_with_ids_at_event
    ),
    required_keys=["event_id"],
)

object_definition_for_dict_of_patrol_boats_by_day_for_volunteer_at_event = DerivedObjectDefinition(
    composition_function=compose_dict_of_patrol_boats_by_day_for_volunteer_at_event,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_events=object_definition_for_list_of_events,
        list_of_volunteers=object_definition_for_volunteers,
        list_of_patrol_boats=object_definition_for_list_of_patrol_boats,
        list_of_volunteers_with_id_at_event_with_patrol_boat_id=object_definition_for_list_of_volunteers_with_ids_and_patrol_boats_at_event,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_volunteers_with_id_at_event_with_patrol_boat_id=object_definition_for_list_of_volunteers_with_ids_and_patrol_boats_at_event
    ),
    required_keys=["event_id"],
)

object_definition_for_list_of_targets_for_role_at_event = DerivedObjectDefinition(
    composition_function=compose_list_of_targets_for_roles_at_event,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_targets_with_role_ids=object_definition_for_list_of_targets_for_role_id_at_event,
        list_of_roles_and_skills=object_definition_for_list_of_roles_with_skills,
        list_of_events=object_definition_for_list_of_events,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_targets_with_role_ids=object_definition_for_list_of_targets_for_role_id_at_event
    ),
    required_keys=["event_id"],
)

object_definition_for_dict_of_cadets_with_food_requirements_at_event = DerivedObjectDefinition(
    composition_function=compose_dict_of_cadets_with_food_requirements_at_event,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_cadets=object_definition_for_list_of_cadets,
        list_of_cadets_with_ids_and_food_requirements=object_definition_for_cadet_ids_with_food_at_event,
        list_of_events=object_definition_for_list_of_events,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_cadets_with_ids_and_food_requirements=object_definition_for_cadet_ids_with_food_at_event
    ),
    required_keys=["event_id"],
)

object_definition_for_dict_of_volunteers_with_food_requirements_at_event = DerivedObjectDefinition(
    composition_function=compose_dict_of_volunteers_with_food_requirements_at_event,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_volunteers=object_definition_for_volunteers,
        list_of_volunteers_with_ids_and_food_requirements=object_definition_for_volunteer_ids_with_food_at_event,
        list_of_events=object_definition_for_list_of_events,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_volunteers_with_ids_and_food_requirements=object_definition_for_volunteer_ids_with_food_at_event
    ),
    required_keys=["event_id"],
)

object_definition_for_dict_of_cadets_with_clothing_at_event = DerivedObjectDefinition(
    composition_function=compose_dict_of_cadets_with_clothing_at_event,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_cadets=object_definition_for_list_of_cadets,
        list_of_cadets_with_clothing_and_ids=object_definition_for_cadet_ids_with_clothing_at_event,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_cadets_with_clothing_and_ids=object_definition_for_cadet_ids_with_clothing_at_event
    ),
    required_keys=["event_id"],
)


## Second level


object_definition_for_dict_of_all_event_info_for_cadet = DerivedObjectDefinition(
    composition_function=compose_dict_of_all_event_info_for_cadet,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_events=object_definition_for_list_of_events,
        dict_of_cadets_and_boat_class_and_partners=object_definition_for_dict_of_cadets_and_boat_classes_and_partners,
        dict_of_cadets_and_club_dinghies_at_event=object_definition_for_dict_of_cadets_and_club_dinghies_at_event,
        dict_of_cadets_with_registration_data=object_definition_for_dict_of_cadets_with_registration_data_at_event,
        dict_of_cadets_with_days_and_groups=object_definition_for_dict_of_cadets_with_groups_at_event,
        dict_of_cadets_with_clothing_at_event=object_definition_for_dict_of_cadets_with_clothing_at_event,
        dict_of_cadets_with_food_required_at_event=object_definition_for_dict_of_cadets_with_food_requirements_at_event,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        dict_of_cadets_and_boat_class_and_partners=object_definition_for_dict_of_cadets_and_boat_classes_and_partners,
        dict_of_cadets_and_club_dinghies_at_event=object_definition_for_dict_of_cadets_and_club_dinghies_at_event,
        dict_of_cadets_with_registration_data=object_definition_for_dict_of_cadets_with_registration_data_at_event,
        dict_of_cadets_with_days_and_groups=object_definition_for_dict_of_cadets_with_groups_at_event,
        dict_of_cadets_with_clothing_at_event=object_definition_for_dict_of_cadets_with_clothing_at_event,
        dict_of_cadets_with_food_required_at_event=object_definition_for_dict_of_cadets_with_food_requirements_at_event,
    ),
    required_keys=["event_id", "active_only"],
)

object_definition_for_dict_of_cadets_with_qualifications_and_ticks = DerivedObjectDefinition(
    composition_function=compose_dict_of_cadets_with_qualifications_and_ticks,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_cadets=object_definition_for_list_of_cadets,
        qualifications_and_tick_items_as_dict=object_definition_for_qualifications_and_tick_items_as_dict,
        dict_of_cadet_ids_with_tick_list_items_for_cadet_id=object_definition_for_dict_of_cadet_ids_with_tick_list_items_for_cadet_id,  ##new
        dict_of_qualifications_for_all_cadets=object_definition_for_dict_of_qualifications_for_cadets,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        dict_of_cadet_ids_with_tick_list_items_for_cadet_id=object_definition_for_dict_of_cadet_ids_with_tick_list_items_for_cadet_id,  ##new
    ),
    required_keys=["list_of_cadet_ids"],
)  # DictOfCadetsWithQualificationsAndTicks

object_definition_for_dict_of_cadets_associated_with_volunteers = DerivedObjectDefinition(
    composition_function=compose_dict_of_cadets_associated_with_volunteers,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_cadet_volunteer_associations=object_definition_for_volunteer_and_cadet_associations
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_cadet_volunteer_associations=object_definition_for_volunteer_and_cadet_associations
    ),
)


object_definition_for_dict_of_volunteers_associated_with_cadets = DerivedObjectDefinition(
    composition_function=compose_dict_of_volunteers_associated_with_cadets,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_cadet_volunteer_associations=object_definition_for_volunteer_and_cadet_associations
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_cadet_volunteer_associations=object_definition_for_volunteer_and_cadet_associations
    ),
)


object_definition_for_dict_of_all_event_data_for_volunteers = DerivedObjectDefinition(
    composition_function=compose_dict_of_all_event_data_for_volunteers,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_events=object_definition_for_list_of_events,
        dict_of_registration_data_for_volunteers_at_event=object_definition_for_dict_of_registration_data_for_volunteers_at_event,
        dict_of_volunteers_with_skills=object_definition_for_dict_of_volunteers_with_skills,
        dict_of_volunteers_at_event_with_days_and_roles=object_definition_for_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups,
        dict_of_volunteers_at_event_with_patrol_boats=object_definition_for_dict_of_patrol_boats_by_day_for_volunteer_at_event,
        dict_of_cadets_associated_with_volunteers=object_definition_for_dict_of_cadets_associated_with_volunteers,
        dict_of_volunteers_with_food_at_event=object_definition_for_dict_of_volunteers_with_food_requirements_at_event,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        dict_of_registration_data_for_volunteers_at_event=object_definition_for_dict_of_registration_data_for_volunteers_at_event,
        dict_of_volunteers_at_event_with_days_and_roles=object_definition_for_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups,
        dict_of_volunteers_at_event_with_patrol_boats=object_definition_for_dict_of_patrol_boats_by_day_for_volunteer_at_event,
        dict_of_volunteers_with_food_at_event=object_definition_for_dict_of_volunteers_with_food_requirements_at_event,
    ),
    required_keys=["event_id"],
)
