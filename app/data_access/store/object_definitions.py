from dataclasses import dataclass
from typing import Callable, Dict, Union

from app.objects.composed.cadets_with_all_event_info import compose_dict_of_all_event_info_for_cadet
from app.objects.composed.cadets_at_event_with_boat_classes_and_partners import \
    compose_dict_of_cadets_and_boat_classes_and_partners
from app.objects.composed.cadets_at_event_with_club_dinghies import compose_dict_of_cadets_and_club_dinghies_at_event
from app.objects.composed.cadets_at_event_with_groups import compose_dict_of_cadets_with_days_and_groups_at_event
from app.objects.composed.cadets_at_event_with_registration_data import compose_dict_of_cadets_with_event_data

from app.data_access.store.data_access import *
from app.objects.composed.cadet_volunteer_associations import \
    create_list_of_cadet_volunteer_associations_from_underlying_data
from app.objects.composed.cadets_with_qualifications import create_dict_of_qualifications_for_cadets
from app.objects.composed.committee import create_list_of_cadet_committee_members_from_underlying_data
from app.objects.composed.roles_and_teams import compose_dict_of_teams_with_roles
from app.objects.composed.ticks_in_dicts import create_qualifications_and_tick_items_as_dict_from_underyling
from app.objects.composed.volunteer_roles import compose_list_of_roles_with_skills
from app.objects.composed.volunteer_with_group_and_role_at_event import \
    compose_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups
from app.objects.composed.volunteers_at_event_with_patrol_boats import \
    compose_dict_of_patrol_boats_by_day_for_volunteer_at_event
from app.objects.composed.volunteers_at_event_with_registration_data import \
    compose_dict_of_registration_data_for_volunteer_at_event
from app.objects.composed.volunteers_with_all_event_data import compose_dict_of_all_event_data_for_volunteers
from app.objects.composed.volunteers_with_skills import compose_dict_of_volunteer_skills
from app.objects.exceptions import arg_not_passed




@dataclass
class UnderlyingObjectDefinition:
    data_store_method_function: Callable
    required_keys: List[str] = arg_not_passed

    @property
    def key(self):
        return "Underlying_"+self.data_store_method_function.__name__

    def matching_kwargs(self, **kwargs) -> dict:
        return  matching_kwargs(self, **kwargs)

def matching_kwargs(object, **kwargs) -> dict:
        required_keys = object.required_keys
        if required_keys is arg_not_passed:
            required_keys = []

        try:
            new_kwargs = dict([
                (key, kwargs[key])
                for key in required_keys
            ])
        except KeyError as e:
            raise Exception("%s missing argument when calling object definition" % str(e))

        return new_kwargs

@dataclass
class DerivedObjectDefinition:
    composition_function: Callable
    dict_of_arguments_and_underlying_object_definitions: Dict[str, Union['DerivedObjectDefinition', UnderlyingObjectDefinition]]
    dict_of_properties_and_underlying_object_definitions_if_modified: Dict[str, Union['DerivedObjectDefinition', UnderlyingObjectDefinition]]
    required_keys: List[str] = arg_not_passed

    @property
    def key(self):
        return "Derived_"+self.composition_function.__name__

    def matching_kwargs(self, **kwargs) -> dict:
        return  matching_kwargs(self, **kwargs)

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

object_definition_for_cadets_with_ids_and_registration_data_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_cadets_with_ids_and_registration_data_at_event,
    required_keys=['event_id']
)
object_definition_for_cadets_with_ids_and_groups_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_cadets_with_groups,
    required_keys=['event_id']
)

object_definition_for_cadets_with_ids_and_boat_classes_at_event = UnderlyingObjectDefinition(
data_store_method_function=get_data_access_for_list_of_cadets_at_event_with_dinghies,
required_keys = ['event_id']
)

object_definition_for_cadets_with_ids_and_club_dinghies_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadets_at_event_with_club_dinghies,
    required_keys=['event_id']

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

object_definition_for_list_of_volunteers_with_ids_roles_and_groups_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_volunteers_in_roles_at_event,
    required_keys=['event_id']

)

object_definition_for_list_of_volunteers_with_ids_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_volunteers_at_event,
    required_keys=['event_id']

)

object_definition_for_list_of_volunteers_with_ids_and_patrol_boats_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_voluteers_at_event_with_patrol_boats,
    required_keys=['event_id']
)

object_definition_for_list_of_cadets_with_tick_list_items_for_cadet_id=UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadets_with_tick_list_items_for_cadet_id,
    required_keys=['cadet_id'] ##returns ListOfCadetsWithTickListItems
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

object_definition_for_dict_of_volunteers_with_skills = DerivedObjectDefinition(
    composition_function=compose_dict_of_volunteer_skills,
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

object_definition_for_dict_of_cadets_with_registration_data_at_event = DerivedObjectDefinition(
    composition_function=compose_dict_of_cadets_with_event_data,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_events = object_definition_for_list_of_events,
        list_of_cadets = object_definition_for_list_of_cadets,
        list_of_cadets_with_id_at_event = object_definition_for_cadets_with_ids_and_registration_data_at_event
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
list_of_cadets_with_id_at_event = object_definition_for_cadets_with_ids_and_registration_data_at_event
    ), required_keys=['event_id']
)

object_definition_for_dict_of_cadets_with_groups_at_event = DerivedObjectDefinition(
    composition_function= compose_dict_of_cadets_with_days_and_groups_at_event,
    dict_of_arguments_and_underlying_object_definitions=dict(
list_of_cadets = object_definition_for_list_of_cadets,
list_of_groups=object_definition_for_list_of_groups,
        list_of_events=object_definition_for_list_of_events,
        list_of_cadet_ids_with_groups = object_definition_for_cadets_with_ids_and_groups_at_event
),
dict_of_properties_and_underlying_object_definitions_if_modified=dict(
list_of_cadet_ids_with_groups = object_definition_for_cadets_with_ids_and_groups_at_event
), required_keys=['event_id']
)

object_definition_for_dict_of_cadets_and_boat_classes_and_partners = DerivedObjectDefinition(
    composition_function=compose_dict_of_cadets_and_boat_classes_and_partners,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_cadets = object_definition_for_list_of_cadets,
        list_of_events=object_definition_for_list_of_events,
        list_of_boat_classes = object_definition_for_list_of_boat_classes,
        list_of_cadets_at_event_with_boat_class_and_partners_with_ids= object_definition_for_cadets_with_ids_and_boat_classes_at_event
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(list_of_cadets_at_event_with_boat_class_and_partners_with_ids= object_definition_for_cadets_with_ids_and_boat_classes_at_event), required_keys=['event_id']
)


object_definition_for_dict_of_cadets_and_club_dinghies_at_event= DerivedObjectDefinition(
    composition_function=compose_dict_of_cadets_and_club_dinghies_at_event,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_cadets=object_definition_for_list_of_cadets,
        list_of_events=object_definition_for_list_of_events,
        list_of_club_dinghies=object_definition_for_list_of_club_dinghies,
    list_of_cadets_at_event_with_id_and_club_dinghy = object_definition_for_cadets_with_ids_and_club_dinghies_at_event
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
list_of_cadets_at_event_with_id_and_club_dinghy = object_definition_for_cadets_with_ids_and_club_dinghies_at_event
    ), required_keys=['event_id']
)

object_definition_for_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups = DerivedObjectDefinition(
    composition_function=compose_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups,
    dict_of_arguments_and_underlying_object_definitions=dict(
    list_of_events=object_definition_for_list_of_events,
        list_of_groups = object_definition_for_list_of_groups,
        list_of_roles_with_skills = object_definition_for_list_of_roles_with_skills,
    list_of_volunteers = object_definition_for_volunteers,
list_of_volunteers_with_id_in_role_at_event = object_definition_for_list_of_volunteers_with_ids_roles_and_groups_at_event
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(

list_of_volunteers_with_id_in_role_at_event = object_definition_for_list_of_volunteers_with_ids_roles_and_groups_at_event,


), required_keys=['event_id'])

object_definition_for_dict_of_registration_data_for_volunteers_at_event = DerivedObjectDefinition(
    composition_function=compose_dict_of_registration_data_for_volunteer_at_event,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_volunteers = object_definition_for_volunteers,
        list_of_events = object_definition_for_list_of_events,
        list_of_volunteers_at_events_with_id = object_definition_for_list_of_volunteers_with_ids_at_event,
        list_of_cadets = object_definition_for_list_of_cadets
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        list_of_volunteers_at_events_with_id=object_definition_for_list_of_volunteers_with_ids_at_event

    ),
    required_keys=['event_id']
)

object_definition_for_dict_of_patrol_boats_by_day_for_volunteer_at_event = DerivedObjectDefinition(
    composition_function=compose_dict_of_patrol_boats_by_day_for_volunteer_at_event,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_events = object_definition_for_list_of_events,
        list_of_volunteers = object_definition_for_volunteers,
        list_of_patrol_boats = object_definition_for_list_of_patrol_boats,
list_of_volunteers_with_id_at_event_with_patrol_boat_id = object_definition_for_list_of_volunteers_with_ids_and_patrol_boats_at_event
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(),
required_keys=['event_id']
)



## Second level


object_definition_for_dict_of_all_event_info_for_cadet = DerivedObjectDefinition(
    composition_function=compose_dict_of_all_event_info_for_cadet,
    dict_of_arguments_and_underlying_object_definitions=dict( list_of_events = object_definition_for_list_of_events,
                                                              dict_of_cadets_and_boat_class_and_partners = object_definition_for_dict_of_cadets_and_boat_classes_and_partners,
                                                              dict_of_cadets_and_club_dinghies_at_event = object_definition_for_dict_of_cadets_and_club_dinghies_at_event,
                                                                dict_of_cadets_with_registration_data = object_definition_for_dict_of_cadets_with_registration_data_at_event,
                                                              dict_of_cadets_with_days_and_groups = object_definition_for_dict_of_cadets_with_groups_at_event
                                                              ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(
        dict_of_cadets_and_boat_class_and_partners=object_definition_for_dict_of_cadets_and_boat_classes_and_partners,
        dict_of_cadets_and_club_dinghies_at_event=object_definition_for_dict_of_cadets_and_club_dinghies_at_event,
        dict_of_cadets_with_registration_data=object_definition_for_dict_of_cadets_with_registration_data_at_event,
        dict_of_cadets_with_days_and_groups=object_definition_for_dict_of_cadets_with_groups_at_event

    ),
 required_keys=['event_id', 'active_only'])


object_definition_for_dict_of_all_event_data_for_volunteers = DerivedObjectDefinition(
    composition_function=compose_dict_of_all_event_data_for_volunteers,
    dict_of_arguments_and_underlying_object_definitions=dict(
        list_of_events = object_definition_for_list_of_events,
dict_of_registration_data_for_volunteers_at_event=object_definition_for_dict_of_registration_data_for_volunteers_at_event,
dict_of_volunteers_with_skills=object_definition_for_dict_of_volunteers_with_skills,
dict_of_volunteers_at_event_with_days_and_roles=object_definition_for_dict_of_volunteers_at_event_with_dict_of_days_roles_and_groups,
dict_of_volunteers_at_event_with_patrol_boats=object_definition_for_dict_of_patrol_boats_by_day_for_volunteer_at_event,
    ),
    dict_of_properties_and_underlying_object_definitions_if_modified=dict(),
 required_keys=['event_id']

)

