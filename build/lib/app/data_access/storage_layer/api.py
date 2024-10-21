from typing import List

from app.OLD_backend.reporting.arrangement.arrange_options import (
    ArrangementOptionsAndGroupOrder,
)

from app.OLD_backend.reporting.options_and_parameters.print_options import PrintOptions

from app.objects.users_and_security import ListOfSkipperManUsers
from app.objects.volunteers import ListOfVolunteers
from app.objects.cadet_volunteer_connections_with_ids import ListOfCadetVolunteerAssociationsWithIds

from app.objects.volunteer_at_event_with_id import ListOfVolunteersAtEventWithId
from app.objects_OLD.primtive_with_id.identified_volunteer_at_event import ListOfIdentifiedVolunteersAtEvent

from app.objects.registration_data import MappedWAEvent

from app.objects_OLD.wa_field_mapping import ListOfWAFieldMappings

from app.objects_OLD.wa_event_mapping import ListOfWAEventMaps

from app.objects.cadet_with_id_at_event import ListOfCadetsWithIDAtEvent
from app.objects.identified_cadets_at_event import ListOfIdentifiedCadetsAtEvent

from app.objects.events import Event

from app.data_access.store.store import Store, DataAccessMethod
from app.data_access.api.generic_api import GenericDataApi
from app.objects.ticks import (
    ListOfCadetIdsWithTickListItemIds,
)
from app.objects.substages import ListOfTickSubStages, ListOfTickSheetItems
from app.objects.cadets import ListOfCadets
from app.objects.qualifications import ListOfQualifications
from app.objects.cadet_with_id_with_group_at_event import ListOfCadetIdsWithGroups
from app.objects.events import ListOfEvents
from app.objects.boat_classes import ListOfBoatClasses
from app.objects.cadet_at_event_with_dinghy_with_ids import ListOfCadetAtEventWithBoatClassAndPartnerWithIds
from app.objects.club_dinghies import (
    ListOfClubDinghies,
)
from app.objects.cadet_at_event_with_club_boat_with_ids import ListOfCadetAtEventWithIdAndClubDinghies
from app.objects.qualifications import ListOfCadetsWithIdsAndQualifications
from app.objects_OLD.primtive_with_id.volunteer_role_targets import ListOfTargetForRoleAtEvent
from app.objects.volunteer_roles_and_groups_with_id import ListOfVolunteersWithIdInRoleAtEvent
from app.objects.composed.volunteers_with_skills import DictOfVolunteersWithSkills
from app.objects.patrol_boats import ListOfPatrolBoats
from app.objects.patrol_boats_with_volunteers_with_id import ListOfVolunteersWithIdAtEventWithPatrolBoatsId
from app.objects.committee import ListOfCadetsWithIdOnCommittee
from app.objects_OLD.food import (
    ListOfCadetsWithFoodRequirementsAtEvent,
    ListOfVolunteersWithFoodRequirementsAtEvent,
)
from app.objects_OLD.clothing import ListOfCadetsWithClothingAtEvent


class DataLayer:
    def __init__(self, store: Store, underlying_data: GenericDataApi):
        self.store = store
        self.data = underlying_data

    def make_data_backup(self):
        self.data.make_backup()

    def clear_stored_items(self):
        print("Clearing store for data")
        self.store.clear_stored_items()

    def save_stored_items(self):
        self.store.save_stored_items()

    ## Just a long list of getters and setters
    def get_list_of_club_dinghies(self) -> ListOfClubDinghies:
        data_access_for_list_of_club_dinghies = (
            get_data_access_for_list_of_club_dinghies(self.data)
        )
        return self.store.read(data_access_for_list_of_club_dinghies)

    def save_list_of_club_dinghies(self, list_of_club_dinghies: ListOfClubDinghies):
        data_access_for_list_of_club_dinghies = (
            get_data_access_for_list_of_club_dinghies(self.data)
        )
        self.store.write(
            list_of_club_dinghies,
            data_access_method=data_access_for_list_of_club_dinghies,
        )

    def get_list_of_boat_classes(self) -> ListOfBoatClasses:
        data_access_for_list_of_dinghies = get_data_access_for_list_of_dinghies(
            self.data
        )
        return self.store.read(data_access_for_list_of_dinghies)

    def save_list_of_boat_classes(self, list_of_dinghies: ListOfBoatClasses):
        data_access_for_list_of_dinghies = get_data_access_for_list_of_dinghies(
            self.data
        )
        self.store.write(
            list_of_dinghies, data_access_method=data_access_for_list_of_dinghies
        )

    def get_list_of_events(self) -> ListOfEvents:
        data_access_for_list_of_events = get_data_access_for_list_of_events(self.data)
        return self.store.read(data_access_for_list_of_events)

    def save_list_of_events(self, list_of_events: ListOfEvents):
        data_access_for_list_of_events = get_data_access_for_list_of_events(self.data)
        self.store.write(
            list_of_events, data_access_method=data_access_for_list_of_events
        )

    def get_list_of_volunteers(self) -> ListOfVolunteers:
        data_access_for_list_of_volunteers = get_data_access_for_list_of_volunteers(
            self.data
        )
        return self.store.read(data_access_for_list_of_volunteers)

    def save_list_of_volunteers(self, list_of_volunteers: ListOfVolunteers):
        data_access_for_list_of_volunteers = get_data_access_for_list_of_volunteers(
            self.data
        )
        return self.store.write(
            list_of_volunteers, data_access_method=data_access_for_list_of_volunteers
        )

    def get_list_of_cadet_volunteer_associations(
        self,
    ) -> ListOfCadetVolunteerAssociationsWithIds:
        data_access_for_list_of_cadet_volunteer_associations = (
            get_data_access_for_list_of_cadet_volunteer_associations(self.data)
        )
        return self.store.read(data_access_for_list_of_cadet_volunteer_associations)

    def save_list_of_cadet_volunteer_associations(
        self, list_of_associations: ListOfCadetVolunteerAssociationsWithIds
    ):
        data_access_for_list_of_cadet_volunteer_associations = (
            get_data_access_for_list_of_cadet_volunteer_associations(self.data)
        )
        self.store.write(
            list_of_associations,
            data_access_method=data_access_for_list_of_cadet_volunteer_associations,
        )

    def get_list_of_cadets_with_tick_list_items_for_cadet_id(
        self, cadet_id: str
    ) -> ListOfCadetIdsWithTickListItemIds:
        data_access_for_list_of_cadets_with_tick_list_items = (
            get_data_access_for_list_of_cadets_with_tick_list_items_for_cadet_id(
                self.data, cadet_id=cadet_id
            )
        )
        return self.store.read(data_access_for_list_of_cadets_with_tick_list_items)

    def save_list_of_cadets_with_tick_list_items_for_cadet_id(
        self, list_of_cadets_with_tick_list_items: ListOfCadetIdsWithTickListItemIds
    ):
        cadet_id_list = list(set(list_of_cadets_with_tick_list_items.list_of_cadet_ids))
        if len(cadet_id_list) == 0:
            return
        elif len(cadet_id_list) > 1:
            raise Exception("Can only write one block of stuff ")
        else:
            cadet_id = cadet_id_list[0]

        data_access_for_list_of_cadets_with_tick_list_items = (
            get_data_access_for_list_of_cadets_with_tick_list_items_for_cadet_id(
                self.data, cadet_id=cadet_id
            )
        )
        self.store.write(
            list_of_cadets_with_tick_list_items,
            data_access_method=data_access_for_list_of_cadets_with_tick_list_items,
        )

    def get_list_of_qualifications(self) -> ListOfQualifications:
        data_access_for_list_of_qualifications = (
            get_data_access_for_list_of_qualifications(self.data)
        )
        return self.store.read(data_access_for_list_of_qualifications)

    def save_list_of_qualifications(self, list_of_qualifications: ListOfQualifications):
        data_access_for_list_of_qualifications = (
            get_data_access_for_list_of_qualifications(self.data)
        )
        self.store.write(
            list_of_qualifications,
            data_access_method=data_access_for_list_of_qualifications,
        )

    def get_list_of_tick_sub_stages(self) -> ListOfTickSubStages:
        data_access_for_list_of_substages = get_data_access_for_list_of_substages(
            self.data
        )
        return self.store.read(data_access_for_list_of_substages)

    def save_list_of_tick_sub_stages(self, list_of_tick_substages: ListOfTickSubStages):
        data_access_for_list_of_substages = get_data_access_for_list_of_substages(
            self.data
        )
        return self.store.write(list_of_tick_substages, data_access_method=data_access_for_list_of_substages)

    def get_list_of_tick_sheet_items(self) -> ListOfTickSheetItems:
        data_access_for_list_of_tick_sheet_items = (
            get_data_access_for_list_of_tick_sheet_items(self.data)
        )
        return self.store.read(data_access_for_list_of_tick_sheet_items)

    def save_list_of_tick_sheet_items(self, list_of_tick_sheet_items: ListOfTickSheetItems):
        data_access_for_list_of_tick_sheet_items = (
            get_data_access_for_list_of_tick_sheet_items(self.data)
        )
        return self.store.write(list_of_tick_sheet_items, data_access_method=data_access_for_list_of_tick_sheet_items)


    def get_list_of_cadets(self) -> ListOfCadets:
        data_access_for_list_of_cadets = get_data_access_for_list_of_cadets(self.data)
        return self.store.read(data_access_for_list_of_cadets)

    def save_list_of_cadets(self, list_of_cadets: ListOfCadets):
        data_access_for_list_of_cadets = get_data_access_for_list_of_cadets(self.data)
        return self.store.write(
            list_of_cadets, data_access_method=data_access_for_list_of_cadets
        )

    def get_list_of_cadets_on_committee(self) -> ListOfCadetsWithIdOnCommittee:
        data_access_for_list_of_cadets_on_committee = (
            get_data_access_for_list_of_cadets_on_committee(self.data)
        )
        return self.store.read(data_access_for_list_of_cadets_on_committee)

    def save_list_of_cadets_on_committee(
        self, list_of_cadets_on_committee: ListOfCadetsWithIdOnCommittee
    ):
        data_access_for_list_of_cadets_on_committee = (
            get_data_access_for_list_of_cadets_on_committee(self.data)
        )
        return self.store.write(
            list_of_cadets_on_committee,
            data_access_method=data_access_for_list_of_cadets_on_committee,
        )

    def get_list_of_cadets_with_qualifications(self) -> ListOfCadetsWithIdsAndQualifications:
        data_access_for_list_of_cadets_with_qualifications = (
            get_data_access_for_list_of_cadets_with_qualifications(self.data)
        )
        return self.store.read(data_access_for_list_of_cadets_with_qualifications)

    def save_list_of_cadets_with_qualifications(
        self, list_of_cadets_with_qualifications: ListOfCadetsWithIdsAndQualifications
    ):
        data_access_for_list_of_cadets_with_qualifications = (
            get_data_access_for_list_of_cadets_with_qualifications(self.data)
        )
        self.store.write(
            list_of_cadets_with_qualifications,
            data_access_method=data_access_for_list_of_cadets_with_qualifications,
        )

    def get_wa_event_mapping(self) -> ListOfWAEventMaps:
        data_access_for_wa_event_mapping = get_data_access_for_wa_event_mapping(
            self.data
        )
        return self.store.read(data_access_for_wa_event_mapping)

    def save_wa_event_mapping(self, list_of_wa_event_maps: ListOfWAEventMaps):
        data_access_for_wa_event_mapping = get_data_access_for_wa_event_mapping(
            self.data
        )
        return self.store.write(
            list_of_wa_event_maps, data_access_method=data_access_for_wa_event_mapping
        )

    def get_print_options(self, report_name: str) -> PrintOptions:
        data_access_for_print_options = get_data_access_for_print_options(
            self.data, report_name=report_name
        )
        return self.store.read(data_access_for_print_options)

    def save_print_options(self, print_options: PrintOptions, report_name: str):
        data_access_for_print_options = get_data_access_for_print_options(
            self.data, report_name=report_name
        )
        self.store.write(
            print_options, data_access_method=data_access_for_print_options
        )

    def get_arrange_group_options(
        self, report_name: str
    ) -> ArrangementOptionsAndGroupOrder:
        data_access_for_arrangements_options = (
            get_data_access_for_arrangement_and_group_order_options(
                self.data, report_name=report_name
            )
        )
        return self.store.read(data_access_for_arrangements_options)

    def save_arrange_group_options(
        self, arrange_group_options: ArrangementOptionsAndGroupOrder, report_name: str
    ):
        data_access_for_arrangements_options = (
            get_data_access_for_arrangement_and_group_order_options(
                self.data, report_name=report_name
            )
        )
        self.store.write(
            arrange_group_options,
            data_access_method=data_access_for_arrangements_options,
        )

    def get_field_mapping_for_template(
        self, template_name: str
    ) -> ListOfWAFieldMappings:
        data_access_for_wa_field_mapping_templates = (
            get_data_access_for_wa_field_mapping_templates(
                self.data, template_name=template_name
            )
        )
        return self.store.read(data_access_for_wa_field_mapping_templates)

    def save_field_mapping_for_template(
        self, template_name: str, list_of_mappings: ListOfWAFieldMappings
    ):
        data_access_for_wa_field_mapping_templates = (
            get_data_access_for_wa_field_mapping_templates(
                self.data, template_name=template_name
            )
        )
        self.store.write(
            list_of_mappings,
            data_access_method=data_access_for_wa_field_mapping_templates,
        )

    def get_list_of_field_mapping_template_names(self) -> List[str]:
        data_access_for_list_of_wa_field_mapping_templates = (
            get_data_access_for_list_of_wa_field_mapping_templates(self.data)
        )
        return self.store.read(
            data_access_method=data_access_for_list_of_wa_field_mapping_templates
        )

    def _save_list_of_field_mapping_template_names_DO_NOT_USE(self):
        raise

    #### EVENT SPECIFIC
    def get_field_mapping_for_event(self, event: Event) -> ListOfWAFieldMappings:
        data_access_for_wa_field_mapping_at_event = (
            get_data_access_for_wa_field_mapping_at_event(self.data, event_id=event.id)
        )
        return self.store.read(data_access_for_wa_field_mapping_at_event)

    def save_field_mapping_for_event(
        self, event: Event, field_mapping: ListOfWAFieldMappings
    ):
        data_access_for_wa_field_mapping_at_event = (
            get_data_access_for_wa_field_mapping_at_event(self.data, event_id=event.id)
        )
        self.store.write(
            field_mapping, data_access_method=data_access_for_wa_field_mapping_at_event
        )

    def get_mapped_wa_event(self, event: Event) -> MappedWAEvent:
        data_access_for_mapped_wa_event = get_data_access_for_mapped_wa_event(
            self.data, event_id=event.id
        )
        return self.store.read(data_access_for_mapped_wa_event)

    def save_mapped_wa_event(self, mapped_wa_event_data: MappedWAEvent, event: Event):
        data_access_for_mapped_wa_event = get_data_access_for_mapped_wa_event(
            self.data, event_id=event.id
        )
        self.store.write(
            mapped_wa_event_data, data_access_method=data_access_for_mapped_wa_event
        )

    def get_list_of_cadets_at_event_with_club_dinghies(
        self, event: Event
    ) -> ListOfCadetAtEventWithIdAndClubDinghies:
        data_access_for_list_of_cadets_at_event_with_club_dinghies = (
            get_data_access_for_list_of_cadets_at_event_with_club_dinghies(
                self.data, event_id=event.id
            )
        )
        return self.store.read(
            data_access_for_list_of_cadets_at_event_with_club_dinghies
        )

    def save_list_of_cadets_at_event_with_club_dinghies(
        self,
        event: Event,
        list_of_cadets_at_event_with_club_dinghies: ListOfCadetAtEventWithIdAndClubDinghies,
    ):
        data_access_for_list_of_cadets_at_event_with_club_dinghies = (
            get_data_access_for_list_of_cadets_at_event_with_club_dinghies(
                self.data, event_id=event.id
            )
        )
        self.store.write(
            list_of_cadets_at_event_with_club_dinghies,
            data_access_method=data_access_for_list_of_cadets_at_event_with_club_dinghies,
        )

    def get_list_of_cadets_at_event_with_dinghies(
        self, event: Event
    ) -> ListOfCadetAtEventWithBoatClassAndPartnerWithIds:
        data_access_for_list_of_cadets_at_event_with_dinghies = (
            get_data_access_for_list_of_cadets_at_event_with_dinghies(
                self.data, event_id=event.id
            )
        )
        return self.store.read(data_access_for_list_of_cadets_at_event_with_dinghies)

    def save_list_of_cadets_at_event_with_dinghies(
        self,
        event: Event,
        list_of_cadets_at_event_with_dinghies: ListOfCadetAtEventWithBoatClassAndPartnerWithIds,
    ):
        data_access_for_list_of_cadets_at_event_with_dinghies = (
            get_data_access_for_list_of_cadets_at_event_with_dinghies(
                self.data, event_id=event.id
            )
        )
        self.store.write(
            list_of_cadets_at_event_with_dinghies,
            data_access_method=data_access_for_list_of_cadets_at_event_with_dinghies,
        )

    def get_list_of_cadets_with_groups_at_event(
        self, event: Event
    ) -> ListOfCadetIdsWithGroups:
        data_access_for_cadets_with_groups = get_data_access_for_cadets_with_groups(
            self.data, event_id=event.id
        )

        return self.store.read(data_access_for_cadets_with_groups)

    def save_list_of_cadets_with_groups_at_event(
        self,
        event: Event,
        list_of_cadets_with_groups_at_event: ListOfCadetIdsWithGroups,
    ):
        data_access_for_cadets_with_groups = get_data_access_for_cadets_with_groups(
            self.data, event_id=event.id
        )

        self.store.write(
            list_of_cadets_with_groups_at_event,
            data_access_method=data_access_for_cadets_with_groups,
        )

    def get_list_of_cadets_at_event(self, event: Event) -> ListOfCadetsWithIDAtEvent:
        data_access_for_cadets_at_event = get_data_access_for_cadets_at_event(
            self.data, event_id=event.id
        )

        return self.store.read(data_access_for_cadets_at_event)

    def save_list_of_cadets_at_event(
        self, event: Event, list_of_cadets_at_event: ListOfCadetsWithIDAtEvent
    ):
        data_access_for_cadets_at_event = get_data_access_for_cadets_at_event(
            self.data, event_id=event.id
        )
        self.store.write(
            list_of_cadets_at_event, data_access_method=data_access_for_cadets_at_event
        )

    def get_list_of_identified_cadets_at_event(
        self, event: Event
    ) -> ListOfIdentifiedCadetsAtEvent:
        data_access_for_identified_cadets_at_event = (
            get_data_access_for_identified_cadets_at_event(self.data, event_id=event.id)
        )

        return self.store.read(data_access_for_identified_cadets_at_event)

    def save_list_of_identified_cadets_at_event(
        self,
        event: Event,
        list_of_identified_cadets_at_event: ListOfIdentifiedCadetsAtEvent,
    ):
        data_access_for_identified_cadets_at_event = (
            get_data_access_for_identified_cadets_at_event(self.data, event_id=event.id)
        )

        return self.store.write(
            list_of_identified_cadets_at_event,
            data_access_method=data_access_for_identified_cadets_at_event,
        )

    def get_list_of_identified_volunteers_at_event(
        self, event: Event
    ) -> ListOfIdentifiedVolunteersAtEvent:
        data_access_for_identified_volunteers_at_event = (
            get_data_access_for_identified_volunteers_at_event(
                self.data, event_id=event.id
            )
        )
        return self.store.read(data_access_for_identified_volunteers_at_event)

    def save_list_of_identified_volunteers_at_event(
        self, event: Event, list_of_volunteers: ListOfIdentifiedVolunteersAtEvent
    ):
        data_access_for_identified_volunteers_at_event = (
            get_data_access_for_identified_volunteers_at_event(
                self.data, event_id=event.id
            )
        )
        self.store.write(
            list_of_volunteers,
            data_access_method=data_access_for_identified_volunteers_at_event,
        )

    def get_list_of_volunteers_at_event(
        self, event: Event
    ) -> ListOfVolunteersAtEventWithId:
        data_access_for_volunteers_at_event = get_data_access_for_volunteers_at_event(
            self.data, event_id=event.id
        )
        return self.store.read(data_access_for_volunteers_at_event)

    def save_list_of_volunteers_at_event(
        self, event: Event, list_of_volunteers_at_event: ListOfVolunteersAtEventWithId
    ):
        data_access_for_volunteers_at_event = get_data_access_for_volunteers_at_event(
            self.data, event_id=event.id
        )
        self.store.write(
            list_of_volunteers_at_event,
            data_access_method=data_access_for_volunteers_at_event,
        )

    def get_list_of_volunteers_in_roles_at_event(
        self, event: Event
    ) -> ListOfVolunteersWithIdInRoleAtEvent:
        data_access_for_list_of_volunteers_in_roles_at_event = (
            get_data_access_for_list_of_volunteers_in_roles_at_event(
                self.data, event_id=event.id
            )
        )
        return self.store.read(
            data_access_method=data_access_for_list_of_volunteers_in_roles_at_event
        )

    def save_list_of_volunteers_in_roles_at_event(
        self,
        event: Event,
        list_of_volunteers_in_role_at_event: ListOfVolunteersWithIdInRoleAtEvent,
    ):
        data_access_for_list_of_volunteers_in_roles_at_event = (
            get_data_access_for_list_of_volunteers_in_roles_at_event(
                self.data, event_id=event.id
            )
        )
        return self.store.write(
            list_of_volunteers_in_role_at_event,
            data_access_method=data_access_for_list_of_volunteers_in_roles_at_event,
        )

    def get_list_of_voluteers_at_event_with_patrol_boats(
        self, event: Event
    ) -> ListOfVolunteersWithIdAtEventWithPatrolBoatsId:
        data_access_for_list_of_voluteers_at_event_with_patrol_boats = (
            get_data_access_for_list_of_voluteers_at_event_with_patrol_boats(
                self.data, event_id=event.id
            )
        )
        return self.store.read(
            data_access_for_list_of_voluteers_at_event_with_patrol_boats
        )

    def save_list_of_voluteers_at_event_with_patrol_boats(
        self,
        list_of_voluteers_at_event_with_patrol_boats: ListOfVolunteersWithIdAtEventWithPatrolBoatsId,
        event: Event,
    ):
        data_access_for_list_of_voluteers_at_event_with_patrol_boats = (
            get_data_access_for_list_of_voluteers_at_event_with_patrol_boats(
                self.data, event_id=event.id
            )
        )
        self.store.write(
            list_of_voluteers_at_event_with_patrol_boats,
            data_access_method=data_access_for_list_of_voluteers_at_event_with_patrol_boats,
        )

    def get_list_of_volunteer_skills(self) -> DictOfVolunteersWithSkills:
        data_access_for_list_of_volunteer_skills = (
            get_data_access_for_list_of_volunteer_skills(self.data)
        )
        return self.store.read(data_access_for_list_of_volunteer_skills)

    def save_list_of_volunteer_skills(
        self, list_of_volunteer_skills: DictOfVolunteersWithSkills
    ):
        data_access_for_list_of_volunteer_skills = (
            get_data_access_for_list_of_volunteer_skills(self.data)
        )
        self.store.write(
            list_of_volunteer_skills,
            data_access_method=data_access_for_list_of_volunteer_skills,
        )

    def get_list_of_targets_for_role_at_event(
        self, event: Event
    ) -> ListOfTargetForRoleAtEvent:
        data_access_for_list_of_targets_for_role_at_event = (
            get_data_access_for_list_of_targets_for_role_at_event(
                self.data, event_id=event.id
            )
        )
        return self.store.read(data_access_for_list_of_targets_for_role_at_event)

    def save_list_of_targets_for_role_at_event(
        self,
        list_of_targets_for_role_at_event: ListOfTargetForRoleAtEvent,
        event: Event,
    ):
        data_access_for_list_of_targets_for_role_at_event = (
            get_data_access_for_list_of_targets_for_role_at_event(
                self.data, event_id=event.id
            )
        )
        self.store.write(
            list_of_targets_for_role_at_event,
            data_access_method=data_access_for_list_of_targets_for_role_at_event,
        )

    def get_list_of_cadets_with_clothing_at_event(
        self, event: Event
    ) -> ListOfCadetsWithClothingAtEvent:
        data_access_for_cadets_with_clothing_at_event = (
            get_data_access_for_cadets_with_clothing_at_event(
                self.data, event_id=event.id
            )
        )
        return self.store.read(data_access_for_cadets_with_clothing_at_event)

    def save_list_of_cadets_with_clothing_at_event(
        self,
        list_of_cadets_with_clothing: ListOfCadetsWithClothingAtEvent,
        event: Event,
    ):
        data_access_for_cadets_with_clothing_at_event = (
            get_data_access_for_cadets_with_clothing_at_event(
                self.data, event_id=event.id
            )
        )
        self.store.write(
            list_of_cadets_with_clothing,
            data_access_method=data_access_for_cadets_with_clothing_at_event,
        )

    def get_list_of_cadets_with_food_at_event(
        self, event: Event
    ) -> ListOfCadetsWithFoodRequirementsAtEvent:
        data_access_for_cadets_with_food_at_event = (
            get_data_access_for_cadets_with_food_at_event(self.data, event_id=event.id)
        )
        return self.store.read(data_access_for_cadets_with_food_at_event)

    def save_list_of_cadets_with_food_at_event(
        self,
        list_of_cadets_with_food: ListOfCadetsWithFoodRequirementsAtEvent,
        event: Event,
    ):
        data_access_for_cadets_with_food_at_event = (
            get_data_access_for_cadets_with_food_at_event(self.data, event_id=event.id)
        )
        self.store.write(
            list_of_cadets_with_food,
            data_access_method=data_access_for_cadets_with_food_at_event,
        )

    def get_list_of_volunteers_with_food_at_event(
        self, event: Event
    ) -> ListOfVolunteersWithFoodRequirementsAtEvent:
        data_access_for_volunteers_with_food_at_event = (
            get_data_access_for_volunteers_with_food_at_event(
                self.data, event_id=event.id
            )
        )
        return self.store.read(data_access_for_volunteers_with_food_at_event)

    def save_list_of_volunteers_with_food_at_event(
        self,
        list_of_volunteers_with_food: ListOfVolunteersWithFoodRequirementsAtEvent,
        event: Event,
    ):
        data_access_for_volunteers_with_food_at_event = (
            get_data_access_for_volunteers_with_food_at_event(
                self.data, event_id=event.id
            )
        )
        self.store.write(
            list_of_volunteers_with_food,
            data_access_method=data_access_for_volunteers_with_food_at_event,
        )

    def get_list_of_patrol_boats(self) -> ListOfPatrolBoats:
        data_access_for_list_of_patrol_boats = get_data_access_for_list_of_patrol_boats(
            self.data
        )
        return self.store.read(data_access_for_list_of_patrol_boats)

    def save_list_of_patrol_boats(self, list_of_patrol_boats: ListOfPatrolBoats):
        data_access_for_list_of_patrol_boats = get_data_access_for_list_of_patrol_boats(
            self.data
        )
        self.store.write(
            list_of_patrol_boats,
            data_access_method=data_access_for_list_of_patrol_boats,
        )

    ### USERS
    def get_list_of_users(self) -> ListOfSkipperManUsers:
        data_access_for_list_of_users = get_data_access_for_list_of_users(self.data)
        return self.store.read(data_access_for_list_of_users)

    def save_list_of_users(self, list_of_users: ListOfSkipperManUsers):
        data_access_for_list_of_users = get_data_access_for_list_of_users(self.data)
        self.store.write(
            list_of_users, data_access_method=data_access_for_list_of_users
        )


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


def get_data_access_for_cadets_at_event(
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


def get_data_access_for_people_with_food_at_event(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "people_at_event_with_food",
        read_method=data.data_list_of_people_with_food_requirement_at_event.read,
        write_method=data.data_list_of_people_with_food_requirement_at_event.write,
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


def get_data_access_for_mapped_wa_event(
    data: GenericDataApi, event_id: str
) -> DataAccessMethod:
    return DataAccessMethod(
        "mapped_wa_event",
        read_method=data.data_mapped_wa_event.read,
        write_method=data.data_mapped_wa_event.write,
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


def get_data_access_for_list_of_cadet_volunteer_associations(
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


def get_data_access_for_list_of_dinghies(data: GenericDataApi) -> DataAccessMethod:
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
