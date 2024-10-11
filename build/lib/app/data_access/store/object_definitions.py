from dataclasses import dataclass
from typing import Callable, Dict, Union, List

from app.data_access.store.data_layer import *
from app.objects.composed.cadet_volunteer_associations import \
    create_list_of_cadet_volunteer_associations_from_underlying_data
from app.objects.composed.cadets_with_qualifications import create_dict_of_qualifications_for_cadets
from app.objects.composed.committee import create_list_of_cadet_committee_members_from_underlying_data
from app.objects.composed.roles_and_teams import compose_dict_of_teams_with_roles
from app.objects.composed.ticks_in_dicts import create_qualifications_and_tick_items_as_dict_from_underyling
from app.objects.composed.volunteer_roles import compose_list_of_roles_with_skills
from app.objects.composed.volunteers_with_skills import compose_list_of_volunteer_skills
from app.objects.exceptions import arg_not_passed



@dataclass
class ObjectDefinition:
    @property
    def key(self):
        raise NotImplemented

@dataclass
class UnderlyingObjectDefinition(ObjectDefinition):
    data_store_method_function: Callable

    @property
    def key(self):
        return "Underlying_"+self.data_store_method_function.__name__



@dataclass
class DerivedObjectDefinition(ObjectDefinition):
    composition_function: Callable
    dict_of_arguments_and_underlying_object_definitions: Dict[str, Union['DerivedObjectDefinition', UnderlyingObjectDefinition]]
    dict_of_properties_and_underlying_object_definitions_if_modified: Dict[str, Union['DerivedObjectDefinition', UnderlyingObjectDefinition]]

    @property
    def key(self):
        return "Derived_"+self.composition_function.__name__

######## LIST OF OBJECT DEFINITIONS

# UNDERLYING

object_definition_for_list_of_cadets = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadets
)
object_definition_for_list_of_cadet_committee_members_with_id = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadets_on_committee
)
object_definition_for_list_of_cadets_and_qualifications_with_ids = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadets_with_qualifications
)

object_definition_for_cadets_with_ids_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_cadets_at_event,
)
object_definition_for_cadets_with_ids_and_groups_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_cadets_with_groups,
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

object_definition_for_list_of_patrol_boats = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_patrol_boats
)

object_definition_for_list_of_qualifications = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_qualifications
)

object_definition_for_list_of_tick_sheet_items = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_tick_sheet_items
)

object_definition_for_list_of_tick_sub_stages= UnderlyingObjectDefinition(
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

## DERIVED

object_definition_for_list_of_cadet_committee_members = DerivedObjectDefinition(
    composition_function=create_list_of_cadet_committee_members_from_underlying_data,
    dict_of_arguments_and_underlying_object_definitions= dict(list_of_cadets=object_definition_for_list_of_cadets, list_of_cadets_with_id_on_commitee=object_definition_for_list_of_cadet_committee_members_with_id),
    dict_of_properties_and_underlying_object_definitions_if_modified= dict(list_of_cadets_with_id_on_commitee=object_definition_for_list_of_cadet_committee_members_with_id)
    )

object_definition_for_dict_of_qualifications_for_cadets = DerivedObjectDefinition(
    composition_function=create_dict_of_qualifications_for_cadets,
    dict_of_arguments_and_underlying_object_definitions=dict(
list_of_qualifications=object_definition_for_list_of_qualifications,
list_of_cadets=object_definition_for_list_of_cadets,
list_of_cadets_with_ids_and_qualifications=object_definition_for_list_of_cadets_and_qualifications_with_ids
    ),
dict_of_properties_and_underlying_object_definitions_if_modified= dict(list_of_cadets_with_ids_and_qualifications=object_definition_for_list_of_cadets_and_qualifications_with_ids)
)

object_definition_for_volunteer_and_cadet_associations = DerivedObjectDefinition(
    composition_function=create_list_of_cadet_volunteer_associations_from_underlying_data,
    dict_of_arguments_and_underlying_object_definitions=dict(
list_of_cadets=object_definition_for_list_of_cadets, list_of_volunteers=object_definition_for_volunteers,
                                                                     list_of_cadet_volunteer_associations_with_ids=object_definition_for_volunteer_and_cadet_associations_with_ids
    ),
dict_of_properties_and_underlying_object_definitions_if_modified=dict(list_of_cadet_volunteer_associations_with_ids=object_definition_for_volunteer_and_cadet_associations_with_ids)
)

object_definition_for_qualifications_and_tick_items_as_dict = DerivedObjectDefinition(
    composition_function=create_qualifications_and_tick_items_as_dict_from_underyling,
    dict_of_arguments_and_underlying_object_definitions=dict(
list_of_qualifications = object_definition_for_list_of_qualifications,
                                                                 list_of_tick_sheet_items=object_definition_for_list_of_tick_sheet_items,
                                                                 list_of_tick_sub_stages=object_definition_for_list_of_tick_sub_stages,
    ),
dict_of_properties_and_underlying_object_definitions_if_modified=dict(                                                                 list_of_tick_sheet_items=object_definition_for_list_of_tick_sheet_items,
                                                                 list_of_tick_sub_stages=object_definition_for_list_of_tick_sub_stages,
)
)

object_definition_for_volunteers_with_skills = DerivedObjectDefinition(
    composition_function=compose_list_of_volunteer_skills,
    dict_of_arguments_and_underlying_object_definitions=\
        dict(
            list_of_volunteers = object_definition_for_volunteers,
            list_of_skills = object_definition_for_list_of_skills,
            list_of_volunteers_with_skills_and_ids = object_definition_for_volunteer_skills_with_ids
        ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_volunteers_with_skills_and_ids=object_definition_for_volunteer_skills_with_ids

    )
)

object_definition_for_list_of_roles_with_skills = DerivedObjectDefinition(
    composition_function=compose_list_of_roles_with_skills,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_roles_with_skill_ids = object_definition_for_list_of_roles_with_skill_ids,
list_of_skills = object_definition_for_list_of_skills
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
list_of_roles_with_skill_ids = object_definition_for_list_of_roles_with_skill_ids
    )
)

object_definition_for_dict_of_teams_with_roles = DerivedObjectDefinition(
    composition_function=compose_dict_of_teams_with_roles,
    dict_of_arguments_and_underlying_object_definitions=dict(list_of_teams_and_roles_with_ids = object_definition_for_list_of_teams_and_roles_with_ids,
                                     list_of_teams= object_definition_for_list_of_teams,
                                     list_of_roles_with_skills = object_definition_for_list_of_roles_with_skills),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(list_of_teams_and_roles_with_ids = object_definition_for_list_of_teams_and_roles_with_ids)
)