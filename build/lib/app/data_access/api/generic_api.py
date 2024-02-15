from app.data_access.classes.cadets import DataListOfCadets, DataListOfCadetsWithGroups, DataListOfCadetsAtEvent, DataListOfIdentifiedCadetsAtEvent
from app.data_access.classes.list_of_events import DataListOfEvents
from app.data_access.classes.wa_event_mapping import DataWAEventMapping
from app.data_access.classes.wa_field_mapping import DataWAFieldMapping
from app.data_access.classes.mapped_wa_event import DataMappedWAEvent
from app.data_access.classes.print_options import DataListOfPrintOptions
from app.data_access.classes.volunteers import DataListOfVolunteers, DataListOfVolunteersAtEvent, DataListOfVolunteerSkills, DataListOfCadetVolunteerAssociations, DataListOfCadetsWithoutVolunteersAtEvent, DataListOfVolunteersInRolesAtEvent
from app.data_access.classes.resources import *

class GenericDataApi(object):
    ## FOLLOWING SHOULD BE OVERWRITTEN BY SPECIFIC CLASSES
    @property
    def data_list_of_cadets(self) -> DataListOfCadets:
        raise NotImplemented

    @property
    def data_list_of_events(self) -> DataListOfEvents:
        raise NotImplemented

    @property
    def data_wa_event_mapping(self) -> DataWAEventMapping:
        raise NotImplemented

    @property
    def data_wa_field_mapping(self) -> DataWAFieldMapping:
        raise NotImplemented

    @property
    def data_mapped_wa_event(self) -> DataMappedWAEvent:
        raise NotImplemented


    @property
    def data_identified_cadets_at_event(
        self,
    ) -> DataListOfIdentifiedCadetsAtEvent:
        raise NotImplemented

    @property
    def data_cadets_at_event(
        self,
    ) -> DataListOfCadetsAtEvent:
        raise NotImplemented

    @property
    def data_list_of_cadets_with_groups(
        self,
    ) -> DataListOfCadetsWithGroups:
        raise NotImplemented

    @property
    def data_print_options(self) -> DataListOfPrintOptions:
        raise NotImplemented

    @property
    def data_list_of_volunteers(self) -> DataListOfVolunteers:
        raise NotImplemented

    @property
    def data_list_of_volunteer_skills(self) -> DataListOfVolunteerSkills:
        raise NotImplemented

    @property
    def data_list_of_cadet_volunteer_associations(self) -> DataListOfCadetVolunteerAssociations:
        raise NotImplemented

    @property
    def data_list_of_volunteers_at_event(self) -> DataListOfVolunteersAtEvent:
        raise NotImplemented

    @property
    def data_list_of_cadets_without_volunteers_at_event(self) -> DataListOfCadetsWithoutVolunteersAtEvent:
        raise NotImplemented

    @property
    def data_list_of_volunteers_in_roles_at_event(self) -> DataListOfVolunteersInRolesAtEvent:
        raise NotImplemented

    @property
    def data_list_of_patrol_boats(self) -> DataListOfPatrolBoats:
        raise NotImplemented

    @property
    def data_List_of_club_dinghies(self) -> DataListOfClubDinghies:
        raise NotImplemented

    @property
    def data_list_of_volunteers_at_event_with_patrol_boats(self) -> DataListOfVolunteersAtEventWithPatrolBoats:
        raise NotImplemented

    @property
    def data_list_of_volunteers_at_event_with_club_dinghies(self) -> DataListOfCadetAtEventWithClubDinghies:
        raise NotImplemented