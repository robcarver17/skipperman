from app.objects.volunteers import ListOfVolunteers, ListOfCadetVolunteerAssociations

from app.objects.volunteers_at_event import ListOfIdentifiedVolunteersAtEvent, ListOfVolunteersAtEvent

from app.objects.mapped_wa_event import MappedWAEvent

from app.objects.wa_field_mapping import ListOfWAFieldMappings

from app.objects.wa_event_mapping import ListOfWAEventMaps

from app.objects.cadet_at_event import ListOfCadetsAtEvent, ListOfIdentifiedCadetsAtEvent

from app.objects.events import Event

from app.data_access.storage_layer.store import Store, DataAccessMethod
from app.data_access.api.generic_api import GenericDataApi
from app.objects.ticks import ListOfCadetsWithTickListItems, ListOfTickSheetItems, ListOfTickSubStages
from app.objects.cadets import ListOfCadets
from app.objects.qualifications import ListOfQualifications
from app.objects.groups import ListOfCadetIdsWithGroups
from app.objects.events import ListOfEvents
from app.objects.club_dinghies import ListOfCadetAtEventWithClubDinghies
from app.objects.qualifications import ListOfCadetsWithQualifications
from app.objects.volunteers_in_roles import ListOfVolunteersInRoleAtEvent


class DataLayer():
    def __init__(self, store: Store, underlying_data: GenericDataApi):
        self.store = store
        self.data = underlying_data

    def clear_stored_items(self):
        self.store.clear_stored_items()

    def save_stored_items(self):
        self.store.save_stored_items()

    ## Just a long list of getters and setters
    def get_list_of_events(self) -> ListOfEvents:
        data_access_for_list_of_events = get_data_access_for_list_of_events(self.data)
        return self.store.read(data_access_for_list_of_events)

    def get_list_of_volunteers(self) -> ListOfVolunteers:
        data_access_for_list_of_volunteers = get_data_access_for_list_of_volunteers(self.data)
        return self.store.read(data_access_for_list_of_volunteers)

    def save_list_of_volunteers(self, list_of_volunteers: ListOfVolunteers):
        data_access_for_list_of_volunteers = get_data_access_for_list_of_volunteers(self.data)
        return self.store.write(list_of_volunteers, data_access_method=data_access_for_list_of_volunteers)

    def get_list_of_cadet_volunteer_associations(self)-> ListOfCadetVolunteerAssociations:
        data_access_for_list_of_cadet_volunteer_associations=get_data_access_for_list_of_cadet_volunteer_associations(self.data)
        return self.store.read(data_access_for_list_of_cadet_volunteer_associations)

    def save_list_of_cadet_volunteer_associations(self,  list_of_associations: ListOfCadetVolunteerAssociations):
        data_access_for_list_of_cadet_volunteer_associations=get_data_access_for_list_of_cadet_volunteer_associations(self.data)
        self.store.write(list_of_associations, data_access_method=data_access_for_list_of_cadet_volunteer_associations)

    def get_list_of_cadets_with_tick_list_items(self) -> ListOfCadetsWithTickListItems:
        data_access_for_list_of_cadets_with_tick_list_items = get_data_access_for_list_of_cadets_with_tick_list_items(self.data)
        return self.store.read(data_access_for_list_of_cadets_with_tick_list_items)

    def get_list_of_qualifications(self) -> ListOfQualifications:
        data_access_for_list_of_qualifications = get_data_access_for_list_of_qualifications(self.data)
        return self.store.read(data_access_for_list_of_qualifications)

    def get_list_of_tick_sub_stages(self) -> ListOfTickSubStages:
        data_access_for_list_of_substages = get_data_access_for_list_of_substages(self.data)
        return self.store.read(data_access_for_list_of_substages)

    def get_list_of_tick_sheet_items(self) -> ListOfTickSheetItems:
        data_access_for_list_of_tick_sheet_items = get_data_access_for_list_of_tick_sheet_items(self.data)
        return self.store.read(data_access_for_list_of_tick_sheet_items)

    def get_list_of_cadets(self)-> ListOfCadets:
        data_access_for_list_of_cadets = get_data_access_for_list_of_cadets(self.data)
        return self.store.read(data_access_for_list_of_cadets)

    def save_list_of_cadets(self, list_of_cadets:ListOfCadets):
        data_access_for_list_of_cadets = get_data_access_for_list_of_cadets(self.data)
        return self.store.write(list_of_cadets, data_access_method=data_access_for_list_of_cadets)

    def get_list_of_cadets_with_qualifications(self) -> ListOfCadetsWithQualifications:
        data_access_for_list_of_cadets_with_qualifications = get_data_access_for_list_of_cadets_with_qualifications(self.data)
        return self.store.read(data_access_for_list_of_cadets_with_qualifications)

    def get_wa_event_mapping(self) -> ListOfWAEventMaps:
        data_access_for_wa_event_mapping= get_data_access_for_wa_event_mapping(self.data)
        return self.store.read(data_access_for_wa_event_mapping)

    def save_wa_event_mapping(self, list_of_wa_event_maps:ListOfWAEventMaps):
        data_access_for_wa_event_mapping= get_data_access_for_wa_event_mapping(self.data)
        return self.store.write(list_of_wa_event_maps, data_access_method=data_access_for_wa_event_mapping)

    #### EVENT SPECIFIC
    def get_field_mapping_for_event(self, event: Event) -> ListOfWAFieldMappings:
        data_access_for_wa_field_mapping_at_event =get_data_access_for_wa_field_mapping_at_event(self.data, event_id=event.id)
        return self.store.read(data_access_for_wa_field_mapping_at_event)

    def save_field_mapping_for_event(self, event: Event, field_mapping: ListOfWAFieldMappings):
        data_access_for_wa_field_mapping_at_event =get_data_access_for_wa_field_mapping_at_event(self.data, event_id=event.id)
        self.store.write(field_mapping, data_access_method=data_access_for_wa_field_mapping_at_event)

    def get_mapped_wa_event(self, event: Event) ->MappedWAEvent:
        data_access_for_mapped_wa_event = get_data_access_for_mapped_wa_event(self.data, event_id=event.id)
        return self.store.read(data_access_for_mapped_wa_event)

    def save_mapped_wa_event(self, mapped_wa_event_data: MappedWAEvent, event: Event):
        data_access_for_mapped_wa_event = get_data_access_for_mapped_wa_event(self.data, event_id=event.id)
        self.store.write(mapped_wa_event_data, data_access_method=data_access_for_mapped_wa_event)

    def get_list_of_cadets_at_event_with_club_dinghies(self, event: Event) -> ListOfCadetAtEventWithClubDinghies:
        data_access_for_list_of_cadets_at_event_with_club_dinghies = get_data_access_for_list_of_cadets_at_event_with_club_dinghies(self.data, event_id=event.id)
        return self.store.read(data_access_for_list_of_cadets_at_event_with_club_dinghies)

    def get_list_of_cadets_with_groups_at_event(self, event: Event) -> ListOfCadetIdsWithGroups:
        data_access_for_cadets_with_groups = get_data_access_for_cadets_with_groups(self.data, event_id=event.id)

        return self.store.read(data_access_for_cadets_with_groups)

    def get_list_of_cadets_at_event(self, event: Event) -> ListOfCadetsAtEvent:
        data_access_for_cadets_at_event = get_data_access_for_cadets_at_event(self.data, event_id=event.id)

        return self.store.read(data_access_for_cadets_at_event)

    def save_list_of_cadets_at_event(self, event: Event, list_of_cadets_at_event: ListOfCadetsAtEvent):
        data_access_for_cadets_at_event = get_data_access_for_cadets_at_event(self.data, event_id=event.id)
        self.store.write(list_of_cadets_at_event, data_access_method=data_access_for_cadets_at_event)

    def get_list_of_identified_cadets_at_event(self, event: Event) -> ListOfIdentifiedCadetsAtEvent:
        data_access_for_identified_cadets_at_event = get_data_access_for_identified_cadets_at_event(self.data, event_id=event.id)

        return self.store.read(data_access_for_identified_cadets_at_event)

    def save_list_of_identified_cadets_at_event(self, event: Event, list_of_identified_cadets_at_event: ListOfIdentifiedCadetsAtEvent):
        data_access_for_identified_cadets_at_event = get_data_access_for_identified_cadets_at_event(self.data, event_id=event.id)

        return self.store.write(list_of_identified_cadets_at_event, data_access_method=data_access_for_identified_cadets_at_event)

    def get_list_of_identified_volunteers_at_event(self, event: Event)-> ListOfIdentifiedVolunteersAtEvent:
        data_access_for_identified_volunteers_at_event =  get_data_access_for_identified_volunteers_at_event(self.data, event_id=event.id)
        return self.store.read(data_access_for_identified_volunteers_at_event)

    def save_list_of_identified_volunteers_at_event(self, event: Event, list_of_volunteers: ListOfIdentifiedVolunteersAtEvent):
        data_access_for_identified_volunteers_at_event =  get_data_access_for_identified_volunteers_at_event(self.data, event_id=event.id)
        self.store.write(list_of_volunteers, data_access_method=data_access_for_identified_volunteers_at_event)

    def get_list_of_volunteers_at_event(self, event: Event) -> ListOfVolunteersAtEvent:
        data_access_for_volunteers_at_event = get_data_access_for_volunteers_at_event(self.data, event_id=event.id)
        return self.store.read(data_access_for_volunteers_at_event)

    def save_list_of_volunteers_at_event(self, event: Event, list_of_volunteers_at_event: ListOfVolunteersAtEvent):
        data_access_for_volunteers_at_event = get_data_access_for_volunteers_at_event(self.data, event_id=event.id)
        self.store.write(list_of_volunteers_at_event, data_access_method=data_access_for_volunteers_at_event)

    def get_list_of_volunteers_in_roles_at_event(self, event:Event) -> ListOfVolunteersInRoleAtEvent:
        data_access_for_list_of_volunteers_in_roles_at_event  = get_data_access_for_list_of_volunteers_in_roles_at_event(self.data, event_id=event.id)
        return self.store.read(data_access_method=data_access_for_list_of_volunteers_in_roles_at_event)

    def save_list_of_volunteers_in_roles_at_event(self, event:Event, list_of_volunteers_in_role_at_event: ListOfVolunteersInRoleAtEvent):
        data_access_for_list_of_volunteers_in_roles_at_event  = get_data_access_for_list_of_volunteers_in_roles_at_event(self.data, event_id=event.id)
        return self.store.write(list_of_volunteers_in_role_at_event, data_access_method=data_access_for_list_of_volunteers_in_roles_at_event)


def get_data_access_for_list_of_cadets(data: GenericDataApi) -> DataAccessMethod:
    return  DataAccessMethod(key="list_of_cadets",
            read_method=data.data_list_of_cadets.read,
            write_method=data.data_list_of_cadets.write)


def get_data_access_for_list_of_cadets_with_tick_list_items(data: GenericDataApi) -> DataAccessMethod:
    return  DataAccessMethod("list_of_cadets_with_tick_list_items",
    data.data_list_of_cadets_with_tick_list_items.read,
    data.data_list_of_cadets_with_tick_list_items.write
    )

def get_data_access_for_list_of_qualifications(data: GenericDataApi) -> DataAccessMethod:
    return  DataAccessMethod("list_of_qualifications",
    data.data_list_of_qualifications.read,
    data.data_list_of_qualifications.write
    )

def get_data_access_for_list_of_substages(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod("list_of_substages",
    data.data_list_of_tick_sub_stages.read,
    data.data_list_of_tick_sub_stages.write
    )

def get_data_access_for_list_of_tick_sheet_items(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod("list_of_tick_sheet_items",
data.data_list_of_tick_sheet_items.read,
    data.data_list_of_tick_sheet_items.write
)

def get_data_access_for_list_of_events(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod("list_of_events",
    data.data_list_of_events.read,
    data.data_list_of_events.write
)


def get_data_access_for_list_of_cadets_with_qualifications(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod("list_of_cadets_with_qualifications",
    data.data_list_of_cadets_with_qualifications.read,
    data.data_list_of_cadets_with_qualifications.write
)

def get_data_access_for_cadets_with_groups(data: GenericDataApi, event_id: str) -> DataAccessMethod:
    return DataAccessMethod("cadets_with_groups",
    data.data_list_of_cadets_with_groups.read_groups_for_event,
    data.data_list_of_cadets_with_groups.write_groups_for_event, event_id=event_id)

def get_data_access_for_cadets_at_event(data: GenericDataApi, event_id: str) -> DataAccessMethod:
    return DataAccessMethod("cadets_at_event",
    read_method=data.data_cadets_at_event.read,
    write_method=data.data_cadets_at_event.write, event_id=event_id)


def get_data_access_for_identified_cadets_at_event(data: GenericDataApi, event_id: str) -> DataAccessMethod:
    return DataAccessMethod("identified_cadets_at_event",
    read_method=data.data_identified_cadets_at_event.read,
    write_method=data.data_identified_cadets_at_event.write, event_id=event_id)


def get_data_access_for_identified_volunteers_at_event(data: GenericDataApi, event_id: str) -> DataAccessMethod:
    return DataAccessMethod("identified_volunteers_at_event",
    read_method=data.data_list_of_identified_volunteers_at_event.read,
    write_method=data.data_list_of_identified_volunteers_at_event.write,
        event_id=event_id)

def get_data_access_for_volunteers_at_event(data: GenericDataApi, event_id: str) -> DataAccessMethod:
    return DataAccessMethod("volunteers_at_event",
    read_method=data.data_list_of_volunteers_at_event.read,
    write_method=data.data_list_of_volunteers_at_event.write, event_id=event_id)


def get_data_access_for_wa_field_mapping_at_event(data: GenericDataApi, event_id: str) -> DataAccessMethod:
    return DataAccessMethod("wa_field_mapping_at_event",
    read_method=data.data_wa_field_mapping.read,
    write_method=data.data_wa_field_mapping.write, event_id=event_id)


def get_data_access_for_mapped_wa_event(data: GenericDataApi, event_id: str) -> DataAccessMethod:
    return DataAccessMethod("mapped_wa_event",
    read_method=data.data_mapped_wa_event.read,
    write_method=data.data_mapped_wa_event.write,
    event_id=event_id)

def get_data_access_for_list_of_cadets_at_event_with_club_dinghies(data: GenericDataApi, event_id: str) -> DataAccessMethod:
    return DataAccessMethod("list_of_cadets_at_event_with_club_dinghies",
    read_method=data.data_list_of_cadets_at_event_with_club_dinghies.read,
    write_method=data.data_list_of_cadets_at_event_with_club_dinghies.write,
    event_id=event_id
)

def get_data_access_for_wa_event_mapping(data: GenericDataApi):
    return DataAccessMethod("wa_event_mapping",
        read_method=data.data_wa_event_mapping.read,
        write_method=data.data_wa_event_mapping.write
    )

def get_data_access_for_list_of_volunteers(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod("list_of_volunteers",
        read_method=data.data_list_of_volunteers.read,
        write_method=data.data_list_of_volunteers.write,
    )

def get_data_access_for_list_of_cadet_volunteer_associations(data: GenericDataApi) -> DataAccessMethod:
    return DataAccessMethod("list_of_cadet_volunteer_associations",
        read_method=data.data_list_of_cadet_volunteer_associations.read,
        write_method=data.data_list_of_cadet_volunteer_associations.write,
    )

def get_data_access_for_list_of_volunteers_in_roles_at_event(data: GenericDataApi, event_id:str) -> DataAccessMethod:
    return DataAccessMethod("list_of_cadet_volunteer_associations",
        read_method=data.data_list_of_volunteers_in_roles_at_event.read,
        write_method=data.data_list_of_volunteers_in_roles_at_event.write,
        event_id = event_id
    )